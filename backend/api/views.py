from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from .models import Author, Follower, FollowRequest, Post, Comment, Like, Inbox
from .serializers import AuthorSerializer, FollowRequestSerializer, UserRegisterSerializer, UserLoginSerializer, PostSerializer, CommentSerializer, LikeSerializer, InboxSerializer
from django.contrib.auth import login, logout
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
import requests
from django.core.paginator import Paginator
#TODO: does a post not have a like value?
#TODO: should comment have content type like post?
# Create your views here.
class UserRegister(APIView):
    """
    Register a new user
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # clean_data = custom_validation(request.data)
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    """
    Login a user
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.check_user(request.data)
            login(request, user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogout(APIView):
    """
    Logout a user
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = ()

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


# will be removed
class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    ##
    def get(self, request):
        serializer = AuthorSerializer(request.user, context={'request': request})
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_authors(request):
    """
    Get all profiles on the server (paginated)
    """
    authors = Author.objects.all()
    serializer = AuthorSerializer(authors, context={'request': request}, many=True)
    response = {
        "type": "authors",
        "items": serializer.data,
    }
    return Response(response)


@api_view(['GET', 'POST'])
def get_and_update_author(request, id):
    """
    Get a single profile on the server by ID
    """
    if request.method == 'GET':
        author = get_object_or_404(Author, id=id)
        serializer = AuthorSerializer(author, context={'request': request})
        return Response(serializer.data)

    if request.method == 'POST':
        author = get_object_or_404(Author, id=id)
        serializer = AuthorSerializer(author, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


@api_view(['GET'])
def get_followers(request, id):
    """
    Get all followers of a single profile
    """
    author = get_object_or_404(Author, id=id)
    followers = author.followers.all()

    # better way to do this?
    followers_set = set()
    for follower_object in followers:
        followers_set.add(follower_object.follower)

    serializer = AuthorSerializer(followers_set, context={'request': request}, many=True)
    response = {
        "type": "followers",
        "items": serializer.data,
    }
    return Response(response)


@api_view(['GET', 'PUT', 'DELETE'])
def get_update_and_delete_follower(request, id_author, id_follower):
    """
    Get, update, or delete a single follower
    """

    if request.method == 'GET':
        follower_object = get_object_or_404(Follower, follower_id=id_follower, followed_user_id=id_author)
        serializer = AuthorSerializer(follower_object.follower, context={'request': request})
        # must return True or False??
        return Response(serializer.data)

    elif request.method == 'PUT':
        # create a new follower
        author = Author.objects.filter(id=id_follower)
        print(author)

        if author.exists() and author.count() == 1:
            follower, created = Follower.objects.get_or_create(follower_id=id_follower, followed_user_id=id_author)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'DELETE':
        follower_object = get_object_or_404(Follower, follower_id=id_follower, followed_user_id=id_author)
        follower_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(['GET'])
def get_received_follow_requests(request, id):
    """
    Get all received friend requests
    """
    author = get_object_or_404(Author, id=id)
    follow_requests = author.received_follow_requests.all()

    serializer = FollowRequestSerializer(follow_requests, context={'request': request}, many=True)
    response = {
        "type": "followrequests",
        "items": serializer.data,
    }
    return Response(response)

@api_view(['GET', 'DELETE'])
def get_and_delete_follow_request(request, id_author, id_sender):
    """
    Get or delete a single received follow request
    """
    # TODO: Not working
    if request.method == 'GET':
        follow_request = get_object_or_404(FollowRequest, from_user_id=id_sender, to_user_id=id_author)
        serializer = FollowRequestSerializer(follow_request, context={'request': request})
        return Response(serializer.data)

#custom uris for getting all public posts
@api_view(['GET'])
def get_all_public_posts(request):
    """
    Get all public posts
    primary used in the explore feed (public stream)
    """
    if request.method == 'GET':
        page_number = request.query_params.get('page', 0)
        size = request.query_params.get('size', 0)
        posts = Post.objects.filter(visibility="PUBLIC").order_by('-published')
        if int(page_number) and int(size):
            paginator = Paginator(posts, size)
            posts = paginator.get_page(page_number)
            serializer = PostSerializer(posts, context={'request': request}, many=True)
            response = {
                "type": "posts",
                "items": serializer.data,
            }
            return Response(response)
        else:
            serializer = PostSerializer(posts, context={'request': request}, many=True)
            response = {
                "type": "posts",
                "items": serializer.data,
            }
            return Response(response)
    
#custom uris for getting all the posts of everyone I am following
@api_view(['GET'])
def get_all_friends_follows_posts(request):
    """
    Get all friends and follows posts
    primary used in the home feed (friends stream)
    This will have all the public posts of the people I am following 
    and the friends only posts of the people I am friends with (they follow and I follow them)
    """
    user = request.user
    if(isinstance(user, Author)):
        userId = user.id
    else:
        userId = None
    if request.method == 'GET':
        if userId is None:
            return Response({"details":"User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            following = Follower.objects.filter(follower__id=userId)
            followers = Follower.objects.filter(followed_user__id=userId)
            friends = following.filter(followed_user__in=followers.values_list('follower', flat=True))
            
            public_posts = Post.objects.filter(author__in=following.values_list('followed_user', flat=True), visibility="PUBLIC")
            friends_posts = Post.objects.filter(author__in=friends.values_list('followed_user', flat=True), visibility="FRIENDS")
            posts = public_posts.union(friends_posts).order_by('-published')
            # pagination
            page_number = request.query_params.get('page', 0)
            size = request.query_params.get('size', 0)
            if int(page_number) and int(size):
                paginator = Paginator(posts, size)
                posts = paginator.get_page(page_number)
                serializer = PostSerializer(posts, context={'request': request}, many=True)
                response = {
                    "type": "posts",
                    "items": serializer.data,
                }
                return Response(response)
            else:
                serializer = PostSerializer(posts, context={'request': request}, many=True)
                response = {
                    "type": "posts",
                    "items": serializer.data,
                }
                return Response(response)

@api_view(['GET', 'POST'])
def get_and_create_post(request, id_author):
    """
    Get all posts by a single author or create a new post
    Primarily used in the authors page stream
    """
    user = request.user
    if(isinstance(user, Author)):
        userId = user.id
    else:
        userId = None
    
    author = Author.objects.filter(id=id_author).first()
    if request.method == 'GET':
        page_number = request.query_params.get('page', 0)
        size = request.query_params.get('size', 0)
        if author is None:
            # send a request to team 1 and then to team 2 to see if a user with that id exists
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            # the author is in our local server
            if userId is None:
                posts = Post.objects.filter(author=author, visibility="PUBLIC")
            elif userId == id_author:
                posts = Post.objects.filter(author=author)
            else:
                # check if the user is a friend of the author
                follower = Follower.objects.filter(follower__id=id_author, followed_user__id=userId).exists()
                following = Follower.objects.filter(follower__id=userId, followed_user__id=id_author).exists()

                if follower and following:
                    posts = Post.objects.filter(author=author, visibility__in=["PUBLIC", "FRIENDS"])
                else:
                    posts = Post.objects.filter(author=author, visibility="PUBLIC")
            
            if int(page_number) and int(size):
                paginator = Paginator(posts, size)
                posts = paginator.get_page(page_number)
                serializer = PostSerializer(posts, context={'request': request}, many=True)
                response = {
                    "type": "posts",
                    "items": serializer.data,
                }
                return Response(response)
            else:
                serializer = PostSerializer(posts, context={'request': request}, many=True)
                response = {
                    "type": "posts",
                    "items": serializer.data,
                }
                return Response(response)

    if request.method == 'POST':
        if userId != id_author:
            return Response({"detail":"Can't create post for another user"}, status=status.HTTP_400_BAD_REQUEST)
        
        copyData = request.data.copy()
        
        if(copyData.get("origin") is None):
            copyData["origin"] = ""
        
        if(copyData.get("source") is None):
            copyData["source"] = ""
        
        serializer = PostSerializer(data=copyData, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(author=author)
            # send the serializer.data (post) to the inbox of the author's followers
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#TODO: not sure what this endpoint means
@api_view(['GET'])
def get_image(request, id_author, id_post):
    """
    Get the image of a single post
    """
    user = request.user
    if(isinstance(user, Author)):
        userId = user.id
    else:
        userId = None

    post = get_object_or_404(Post, id=id_post)
    if post.contentType.startswith("image"):
        try:
            response = requests.get(post.image)
            response.raise_for_status()
            image_content = response.content
        except requests.exceptions.RequestException as e:
            return Response({'error': f'Error fetching image: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if post.visibility == "PUBLIC" or userId == id_author:
            return Response(image_content, status=status.HTTP_200_OK)
        
        elif post.visibility == "FRIENDS":
            if userId is None:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            follower = Follower.objects.filter(follower__id=id_author, followed_user__id=userId).exists()
            following = Follower.objects.filter(follower__id=userId, followed_user__id=id_author).exists()
            if follower and following:
                return Response(image_content, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        
        return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'PUT', 'DELETE'])
def get_update_and_delete_specific_post(request, id_author, id_post):
    """
    Get, update, or delete a single post
    """
    user = request.user
    if(isinstance(user, Author)):
        userId = user.id
    else:
        userId = None
    
    if request.method == 'GET':
        post = get_object_or_404(Post, id=id_post)
        serializer = PostSerializer(post, context={'request': request})
        if post.visibility == "PUBLIC" or userId == id_author:
            return Response(serializer.data)
        elif post.visibility == "FRIENDS":
            if userId is None:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            follower = Follower.objects.filter(follower__id=id_author, followed_user__id=userId).exists()
            following = Follower.objects.filter(follower__id=userId, followed_user__id=id_author).exists()
            if follower and following:
                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        elif post.visibility == "UNLISTED":
            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        post = get_object_or_404(Post, id=id_post)
        if userId != id_author:
            return Response({"detail":"Can't edit someone elses post"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = PostSerializer(post, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        post = get_object_or_404(Post, id=id_post)
        if userId != id_author:
            return Response({"detail":"Can't delete someone elses post"}, status=status.HTTP_401_UNAUTHORIZED)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# comments
@api_view(['GET', 'POST'])
def get_and_create_comment(request, id_author, id_post):
    """
    Get all comments of a single post or create a new comment
    """
    user = request.user
    if(isinstance(user, Author)):
        userId = user.id
    else:
        userId = None
    
    post = get_object_or_404(Post, id=id_post)
    if request.method == 'GET':
        page_number = request.query_params.get('page', 0)
        size = request.query_params.get('size', 0)
        comments = Comment.objects.filter(post=post).order_by('-published')
        if int(page_number) and int(size):
            paginator = Paginator(comments, size)
            comments = paginator.get_page(page_number)
            serializer = CommentSerializer(comments, context={'request': request}, many=True)
            response = {
                "type": "comments",
                "items": serializer.data,
            }
            return Response(response)
        else:
            serializer = CommentSerializer(comments, context={'request': request}, many=True)
            response = {
                "type": "comments",
                "items": serializer.data,
            }
            return Response(response)
    
    if request.method == 'POST':
        if userId is None:
            return Response({"details":"can't create a comment anonymously"}, status=status.HTTP_401_UNAUTHORIZED)
        commentAuthor = get_object_or_404(Author, id=userId)

        commentData = request.data.copy()
        commentData["author"] = commentAuthor.id
        commentData["post"] = post.id

        serializer = CommentSerializer(data=commentData, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            # send comment in inbox of post author
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_post_likes(request, id_author, id_post):
    """
    Get all likes of a single post
    """    
    post = get_object_or_404(Post, id=id_post, author__id=id_author)
    likes = Like.objects.filter(post=post)
    serializer = AuthorSerializer(likes, context={'request': request}, many=True)
    response = {
        "type": "likes",
        "items": serializer.data,
    }
    return Response(response)

@api_view(['GET'])
def get_comment_likes(request, id_author, id_post, id_comment):
    """
    Get all likes of a single comment
    """
    comment = get_object_or_404(Comment, id=id_comment, post__id=id_post, post__author__id=id_author)
    likes = Like.objects.filter(comment=comment)
    serializer = AuthorSerializer(likes, context={'request': request}, many=True)
    response = {
        "type": "likes",
        "items": serializer.data,
    }
    return Response(response)

@api_view(['GET'])
def get_liked(request, id_author):
    """
    Get all likes of a single author
    """
    author = get_object_or_404(Author, id=id_author)
    likes = Like.objects.filter(author=author)
    serializer = LikeSerializer(likes, context={'request': request}, many=True)
    response = {
        "type": "likes",
        "items": serializer.data,
    }
    return Response(response)

#TODO: inbox
# check if item is a post, comment, like, follow, follow request
# path("authors/<uuid:id_author>/inbox", views.get_and_post_inbox, name="get_and_post_inbox"),
# GET [local]: if authenticated get a list of posts sent to AUTHOR_ID (paginated)
# Should be sorted most recent first
# POST [local, remote]: send a post to the author
# if the type is "post" then add that post to AUTHOR_ID's inbox
# if the type is "follow" then add that follow is added to AUTHOR_ID's inbox to approve later
# if the type is "Like" then add that like to AUTHOR_ID's inbox
# if the type is "comment" then add that comment to AUTHOR_ID's inbox
# DELETE [local]: clear the inbox
@api_view(['GET', 'POST', 'DELETE'])
def get_and_post_inbox(request, id_author):
    """
    Get all items in the inbox of a single author or create a new item
    """
    user = request.user
    if(isinstance(user, Author)):
        userId = user.id
    else:
        userId = None
    author = get_object_or_404(Author, id=id_author)
    if request.method == 'GET':
        page_number = request.query_params.get('page', 0)
        size = request.query_params.get('size', 0)
        if userId is None:
            return Response({"details":"Can't get inbox anonymously"}, status=status.HTTP_401_UNAUTHORIZED)
        inbox = Inbox.objects.filter(author=author).order_by('-published')
        if int(page_number) and int(size):
            paginator = Paginator(inbox, size)
            inbox = paginator.get_page(page_number)
            serializer = InboxSerializer(inbox, context={'request': request}, many=True)
            response = {
                "type": "inbox",
                "items": serializer.data,
            }
            return Response(response)
        else:
            serializer = InboxSerializer(inbox, context={'request': request}, many=True)
            response = {
                "type": "inbox",
                "items": serializer.data,
            }
            return Response(response)
    if request.method == 'POST':
        if userId is None:
            return Response({"details":"Can't post to inbox anonymously"}, status=status.HTTP_401_UNAUTHORIZED)
        copyData = request.data.copy()
        copyData["author"] = author.id
        
        if copyData.get("item") is None:
            return Response({"details":"item is required"}, status=status.HTTP_400_BAD_REQUEST)
        itemType = copyData.get("item").get("type")
        
        if itemType == "like":
            likeAuthor = get_object_or_404(Author, id=userId)
            likeData = copyData.get("item")
            likeData["author"] = likeAuthor.id
            objectString = likeData.get("object")
            
            if objectString is not None or objectString != "":
                if "comments" in objectString:
                    commentId = objectString.split("/")[-1]
                    likeData["comment"] = get_object_or_404(Comment, id=commentId)
                else:
                    likeData["comment"] = None
                if "posts" in objectString:
                    postId = objectString.split("/")[-1]
                    likeData["post"] = get_object_or_404(Post, id=postId)
                else:
                    return Response({"details":"object should have a post"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"details":"object is required"}, status=status.HTTP_400_BAD_REQUEST)

            if likeData["comment"] is not None:
                likeExists = Like.objects.filter(author=likeAuthor, comment=likeData["comment"]).exists()
            else:
                likeExists = Like.objects.filter(author=likeAuthor, post=likeData["post"]).exists()
            
            if likeExists:
                return Response({"details":"like already exists"}, status=status.HTTP_400_BAD_REQUEST)

            likeSerializer = LikeSerializer(data=likeData, context={'request': request})
            
            if likeSerializer.is_valid():
                likeSerializer.save()
                copyData["item"] = likeSerializer.data
            else:
                return Response(likeSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif itemType == "follow":
            actor = copyData["item"].get("actor")
            object = copyData["item"].get("object")
            if actor is None or object is None:
                return Response({"details":"actor and object are required"}, status=status.HTTP_400_BAD_REQUEST)

            actorAuthor = Author.objects.filter(id = actor.get("id")).first()
            objectAuthor = Author.objects.filter(id = object.get("id")).first()

            followRequest = FollowRequest.objects.filter(from_user=actorAuthor, to_user=objectAuthor).exists()
            
            if followRequest:
                return Response({"details":"follow request already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            followRequestData = {
                "from_user": actorAuthor,
                "to_user": objectAuthor
            }
            
            followRequestSerializer = FollowRequestSerializer(data=followRequestData, context={'request': request})
            
            if followRequestSerializer.is_valid():
                followRequestSerializer.save()
                copyData["item"] = followRequestSerializer.data
            else:
                return Response(followRequestSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # if its a post or comment check if the post or comment exists
        elif itemType == "post":
            postId = copyData.get("item").get("id")
            if postId is None:
                return Response({"details":"post id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                post = Post.objects.get(id=postId)
                copyData["item"] = PostSerializer(post, context={'request': request}).data
            except Post.DoesNotExist:
                return Response({"details":"post does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        elif itemType == "comment":
            commentId = copyData.get("item").get("id")
            if commentId is None:
                return Response({"details":"comment id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                comment = Comment.objects.get(id=commentId)
                copyData["item"] = CommentSerializer(comment, context={'request': request}).data
            except Comment.DoesNotExist:
                return Response({"details":"comment does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({"details":"item type is required and should be one of post, comment, like, follow"}, status=status.HTTP_400_BAD_REQUEST)
        
        # create the inbox item
        inboxSerializer = InboxSerializer(data=copyData, context={'request': request})
        if inboxSerializer.is_valid():
            inboxSerializer.save()
            return Response(inboxSerializer.data, status=status.HTTP_201_CREATED)
        return Response(inboxSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if userId is None:
            return Response({"details":"Can't delete inbox anonymously"}, status=status.HTTP_401_UNAUTHORIZED)
        if userId != id_author:
            return Response({"details":"Can't delete someone elses inbox"}, status=status.HTTP_401_UNAUTHORIZED)
        inbox = Inbox.objects.filter(author=author)
        inbox.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)