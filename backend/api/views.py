from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from .models import Author, Follower, FollowRequest, Post, Comment, Like
from .serializers import AuthorSerializer, FollowRequestSerializer, UserRegisterSerializer, UserLoginSerializer, PostSerializer, CommentSerializer, LikeSerializer
from django.contrib.auth import login, logout
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
import requests
from django.core.paginator import Paginator
#TODO: does a post not have a like value?
#TODO: doesn't return the author information fix that
#TODO: add pagination
#TODO: should comment have content type like post?
#TODO: will there be individual comments or just a list of comments?
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
    page_number = request.query_params.get('page', 0)

    # default page size is 10
    size = request.query_params.get('size', 10)
    # ensure size is an integer
    try:
        size = int(size)
    except:
        size = 10

    response = {}
    response["type"] = "authors"

    # if page param is provided, paginate the authors, otherwise return all authors
    if page_number:
        paginator = Paginator(authors, size)
        authors = paginator.get_page(page_number)
        response["page"] = authors.number
        response["size"] = size

    serializer = AuthorSerializer(authors, context={'request': request}, many=True)
    response["items"] = serializer.data
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