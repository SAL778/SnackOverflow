from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from .models import Author, Follower, FollowRequest, Post, Comment, Like, Inbox
from .serializers import AuthorSerializer, FollowRequestSerializer, UserRegisterSerializer, UserLoginSerializer, PostSerializer, CommentSerializer, LikeSerializer, InboxSerializer
from django.contrib.auth import login, logout
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from django.views import View
from django.http import HttpResponse, HttpResponseNotFound
import requests, json, os
from django.core.paginator import Paginator
from drf_yasg.utils import swagger_auto_schema
#TODO: does a post not have a like value?
#TODO: should comment have content type like post?

class UserRegister(APIView):
    """
    Register a new user
    """

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_summary="Register a new user",
        operation_description="Register a new user on the server. The user will be able to login and use the server's features. It will return the user's data.",
        request_body=UserRegisterSerializer,
        responses={201: "Created", 400: "Bad Request"},
    )
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
    @swagger_auto_schema(
        operation_summary="Login a user",
        operation_description="Login a user on the server. The user will be able to use the server's features. It will return the user's data.",
        request_body=UserLoginSerializer,
        responses={200: "Ok", 400: "Bad Request"},
    )
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

    @swagger_auto_schema(
        operation_summary="Logout a user",
        operation_description="Logout a user from the server. It deletes the user's session cookie.",
        responses={200: "Ok", 400: "Bad Request"},
    )
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


# will be removed
class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (SessionAuthentication,)
    ##
    @swagger_auto_schema(
        operation_summary="get the user",   
        operation_description="Returns the user data.",
        responses={200: "Ok"},
    )
    def get(self, request):
        serializer = AuthorSerializer(request.user, context={'request': request})
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)

@swagger_auto_schema(
        method="get",
        operation_summary="gets all the authors",   
        operation_description="Returns all the authors on the server. Paginated.",
        responses={200: "Ok", 403: "Authentication credentials weren't provided", 500: "Internal Server Error"},
)
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

@swagger_auto_schema(
        method="get",
        operation_summary="gets the authors with the given id",   
        operation_description="Returns the author with the id. The author has to be in the server. Otherwise it will return a 404 error.",
        responses={200: "Ok", 400: "Bad Request", 404: "Not found"},
)
@swagger_auto_schema(
        method="post",
        operation_summary="creates an authors on the server",   
        operation_description="It creates an author on the server. If the author exists then it will throw an error. It will return the author's data.",
        request_body=AuthorSerializer,
        responses={200: "Ok", 400: "Bad Request", 404: "Not found"},
)
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
@swagger_auto_schema(
        method="get",
        operation_summary="gets all the followers of the author with the given id",   
        operation_description="Returns all the followers of the author with the given id. The author has to be in the server. Otherwise it will return a 404 error.",
        responses={200: "Ok", 400: "Bad Request", 404: "Not found"},
)
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
@swagger_auto_schema(
        method="get",
        operation_summary="gets the specific follower with id_follower of the author with the given id_author",   
        operation_description="Returns the specific follower with id_follower of the author with the given id_author. \
        The author has to be in the server and the follower has to be in the server as well. Otherwise it will return a 404 error.",
        responses={200: "Ok", 400: "Bad Request", 404: "Not found"},
)
@swagger_auto_schema(
        method="put",
        operation_summary="updates the specific follower with id_follower of the author with the given id_author",   
        operation_description="Updates and Returns the specific follower with id_follower of the author with the given id_author. \
        The author has to be in the server and the follower has to be in the server as well. Otherwise it will return a 404 error.",
        responses={201: "Created",  400: "Bad Request", 404: "Not found"},
)
@swagger_auto_schema(
        method="delete",
        operation_summary="deletes the specific follower with id_follower of the author with the given id_author",   
        operation_description="Deletes the specific follower with id_follower of the author with the given id_author. \
        The author has to be in the server and the follower has to be in the server as well. Otherwise it will return a 404 error.",
        responses={204: "No Content",  400: "Bad Request", 404: "Not found"},
)
@api_view(['GET', 'PUT', 'DELETE'])
def get_update_and_delete_follower(request, id_author, id_follower):
    """
    Get, update, or delete a single follower
    """

    if request.method == 'GET':
        follower_object = get_object_or_404(Follower, follower_id=id_follower, followed_user_id=id_author)
        serializer = AuthorSerializer(follower_object.follower, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        # create a new follower
        author = Author.objects.filter(id=id_follower)

        if author.exists() and author.count() == 1:
            follower, created = Follower.objects.get_or_create(follower_id=id_follower, followed_user_id=id_author)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'DELETE':
        follower_object = get_object_or_404(Follower, follower_id=id_follower, followed_user_id=id_author)
        follower_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(
        method="get",
        operation_summary="gets all the followings of the author with the given id",
        operation_description="Returns all the followings of the author with the given id. The author has to be in the server. Otherwise it will return a 404 error.",
        responses={200: "Ok", 400: "Bad Request", 404: "Not found"},
)
@api_view(['GET'])
def get_followings(request, id_author):
    """
    Get all followings of a single profile
    """
    author = get_object_or_404(Author, id=id_author)
    followings = author.following.all()

    followings_set = set()
    for following_object in followings:
        followings_set.add(following_object.followed_user)

    serializer = AuthorSerializer(followings_set, context={'request': request}, many=True)
    response = {
        "type": "followings",
        "items": serializer.data,
    }
    return Response(response)

@swagger_auto_schema(
        method="get",
        operation_summary="gets all the friends of the author with the given id",
        operation_description="Returns all the friends of the author with the given id. The author has to be in the server. Otherwise it will return a 404 error.\
            Friends are the people who follow the author and the author follows them back.",
        responses={200: "Ok", 400: "Bad Request", 404: "Not found"},
)
@api_view(['GET'])
def get_friends(request, id_author):
    """
    Get all friends of a single profile
    """
    author = get_object_or_404(Author, id=id_author)
    following = author.following.all()
    followers = author.followers.all()

    # for my following, check if they are also in my followers
    friends = following.filter(followed_user__in=followers.values_list('follower', flat=True))    
    print(friends)

    friends_set = set()
    for friend_object in friends:
        friends_set.add(friend_object.followed_user)

    serializer = AuthorSerializer(friends_set, context={'request': request}, many=True)
    response = {
        "type": "friends",
        "items": serializer.data,
    }
    return Response(response)

@swagger_auto_schema(
        method="get",        
        operation_summary="gets all the follow requests of the author with the given id",
        operation_description="Returns all the follow requests of the author with the given id. The author has to be in the server. Otherwise it will return a 404 error.",
        responses={200: "Ok", 400: "Bad Request", 404: "Not found"},
)
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

@swagger_auto_schema(
        method="get",
        operation_summary="gets the specific follow request with id_sender of the author with the given id_author",
        operation_description="Returns the specific follow request with id_sender of the author with the given id_author. \
        The follow request has to be in the server. Otherwise it will return a 404 error.",
        responses={200: "Ok", 400: "Bad Request", 404: "Not found"},
)
@swagger_auto_schema(
        method="post",
        operation_summary="creates a follow request for the author with the given id_author and the sender with the given id_sender",
        operation_description="Creates a follow request for the author with the given id_author and the sender with the given id_sender. \
        The author and the sender have to be in the server. Otherwise it will return a 404 error.",
        responses={201: "Created", 400: "Bad Request", 404: "Not found"},
)
@swagger_auto_schema(
        method="put",
        operation_summary="accepts the specific follow request with id_sender of the author with the given id_author",
        operation_description="Accepts the specific follow request with id_sender of the author with the given id_author. \
        The follow request has to be in the server. Otherwise it will return a 404 error. \
        It will also delete the follow request and create a follower.",
        responses={201: "Created", 400: "Bad Request", 404: "Not found"},
)
@swagger_auto_schema(

        method="delete",
        operation_summary="declines the specific follow request with id_sender of the author with the given id_author",
        operation_description="Declines the specific follow request with id_sender of the author with the given id_author. \
        The follow request has to be in the server. Otherwise it will return a 404 error. It will delete the follow request object since it has been decliend",
        responses={204: "No Content", 400: "Bad Request", 404: "Not found"},
)
@api_view(['GET', 'DELETE', 'PUT', 'POST'])
def get_create_delete_and_accept_follow_request(request, id_author, id_sender):
    """
    Get, create, delete or accept a received follow request
    """
    if request.method == 'GET':
        follow_request = get_object_or_404(FollowRequest, from_user_id=id_sender, to_user_id=id_author)
        serializer = FollowRequestSerializer(follow_request, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # create a new follow request
        author = Author.objects.filter(id=id_sender)

        if author.exists() and author.count() == 1:
            follow_request, created = FollowRequest.objects.get_or_create(from_user_id=id_sender, to_user_id=id_author)
            # send it to the inbox of the author
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'PUT':
        # friend request accepted => create a new follower and delete the follow request
        # confirm the follow request exists
        follow_request = get_object_or_404(FollowRequest, from_user_id=id_sender, to_user_id=id_author)

        author = Author.objects.filter(id=id_sender)

        if author.exists() and author.count() == 1:
            follower, created = Follower.objects.get_or_create(follower_id=id_sender, followed_user_id=id_author)
            follow_request = get_object_or_404(FollowRequest, from_user_id=id_sender, to_user_id=id_author)
            follow_request.delete()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    elif request.method == 'DELETE':
        # friend request declined
        follow_request = get_object_or_404(FollowRequest, from_user_id=id_sender, to_user_id=id_author)
        follow_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#custom uris for getting all public posts
@swagger_auto_schema(
        method="get",
        operation_summary="gets all public posts",
        operation_description="Returns all the public posts on the server. Paginated (Optional).",
        responses={200: "Ok", 400: "Bad Request"},
)
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
@swagger_auto_schema(
        method="get",
        operation_summary="gets all the posts of everyone the author is following and the author is friends with",
        operation_description="Returns all the public posts of all the people the author is following and the friends only post of the people the author is friends with. Paginated (Optional).\
            The author has to be authenticated. Otherwise it will return a 401 error.",
        responses={200: "Ok", 401: "Unauthorized", 400: "Bad Request"},
)
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

@swagger_auto_schema(
        method="get",
        operation_summary="gets all the posts of the author with the given id",
        operation_description="Returns all the posts of the author with the given id. The author has to be in the server. Otherwise it will return a 404 error. Paginated (Optional).\
            If the user making the request is the same same as the author then it will return all the posts. Otherwise it will return only the public posts.\
            If the user making the request is a friend of the author then it will return all the public and friends only posts.\
            If the user is not authenticated then it will return only the public posts.",
        responses={200: "Ok", 400: "Bad Request", 404: "Not found"},
)
@swagger_auto_schema(
        method="post",
        operation_summary="creates a post for the author with the given id",
        operation_description="Creates a post for the author with the given id. The author has to be in the server. Otherwise it will return a 404 error.\
            The user making the request has to be the same as the author. Otherwise it will return a 401 error. \
            If the body of the post is incorrect then it will return a 400 error. This will also send the created post to the appropriate inboxes.",
        request_body=PostSerializer,
        responses={201: "Created", 400: "Bad Request", 401: "Unauthorized", 404: "Not found"},
)
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
            return Response({"detail":"Can't create post for another user"}, status=status.HTTP_401_UNAUTHORIZED)

        requestData = dict(request.data)
        #requestData = json.loads(requestData)
        #print("Data: ",requestData, type(requestData))

        if(requestData.get("origin") is None):
            requestData["origin"] = ""

        if(requestData.get("source") is None):
            requestData["source"] = ""

        serializer = PostSerializer(data=requestData, context={'request': request})

        if serializer.is_valid():
            serializer.save(author=author)
            # send the serializer.data (post) to the inbox of the author's followers
            # send the post to the author's followers or friends
            # check if the post is coming from our host. If its from our host do this else just add that to the inbox (everything is correct in that case)
            postId = serializer.data.get("id").split("/")[-1]
            post = Post.objects.filter(id=postId).first()
            postType = post.visibility
            if postType == "PUBLIC":
                followers = Follower.objects.filter(followed_user__id=id_author)
                for follower in followers:
                    # check if the follower is in another server and if it is then send the request
                    requestData["author"] = follower.follower.id
                    inboxSerializer = InboxSerializer(data=requestData, context={'request': request})
                    if inboxSerializer.is_valid():
                        inboxSerializer.save()
            elif postType == "FRIENDS":
                followers = Follower.objects.filter(followed_user__id=id_author)
                for follower in followers:
                    followerObject = Follower.objects.filter(follower__id=id_author, followed_user__id=follower.follower.id).first()
                    if followerObject is not None:
                        requestData["author"] = follower.follower.id
                        inboxSerializer = InboxSerializer(data=requestData, context={'request': request})
                        if inboxSerializer.is_valid():
                            inboxSerializer.save()
                # what if the follower is in another server, how do we know its a friend?
                # we have to know its a friend so that we can send it to their inbox
            else:
                print("unlisted post")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Here:",serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#TODO: not sure what this endpoint means
# @swagger_auto_schema(
#         method="get",
#         operation_summary="gets the image of the post with the given id_post",
#         operation_description="Returns the image of the post with the given id_post. The post has to be in the server. Otherwise it will return a 404 error.",
#         responses={200: "Ok", 400: "Bad Request", 404: "Not found"},
# )
# @api_view(['GET'])
# def get_image(request, id_author, id_post):
#     """
#     Get the image of a single post
#     """
#     user = request.user
#     if(isinstance(user, Author)):
#         userId = user.id
#     else:
#         userId = None

#     post = get_object_or_404(Post, id=id_post)
#     if post.contentType.startswith("image"):
#         try:
#             response = requests.get(post.image)
#             response.raise_for_status()
#             image_content = response.content
#         except requests.exceptions.RequestException as e:
#             return Response({'error': f'Error fetching image: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         if post.visibility == "PUBLIC" or userId == id_author:
#             return Response(image_content, status=status.HTTP_200_OK)

#         elif post.visibility == "FRIENDS":
#             if userId is None:
#                 return Response(status=status.HTTP_401_UNAUTHORIZED)
#             follower = Follower.objects.filter(follower__id=id_author, followed_user__id=userId).exists()
#             following = Follower.objects.filter(follower__id=userId, followed_user__id=id_author).exists()
#             if follower and following:
#                 return Response(image_content, status=status.HTTP_200_OK)
#             else:
#                 return Response(status=status.HTTP_404_NOT_FOUND)

#         return Response(status=status.HTTP_404_NOT_FOUND)
#     else:
#         return Response(status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
        method="get",
        operation_summary="gets the specific post with id_post of the author with the given id_author",
        operation_description="Returns the specific post with id_post of the author with the given id_author. \
        The post has to be in the server. Otherwise it will return a 404 error. \
        If the user making the request is the same same as the author then it will return the post. \
        If the user making the request is a friend of the author then it will return the post if its visibility is FRIENDS or PUBLIC. \
        If the post is FRIENDS then the user has to be authenticated. Otherwise it will return a 401 error.",
        responses={200: "Ok", 400: "Bad Request", 401: "Unauthorized", 404: "Not found"},
)
@swagger_auto_schema(
        method="put",
        operation_summary="updates the specific post with id_post of the author with the given id_author",
        operation_description="Updates and Returns the specific post with id_post of the author with the given id_author. \
        The post has to be in the server. Otherwise it will return a 404 error. \
        The user making the request has to be the same as the author. Otherwise it will return a 401 error. \
        If the body of the post is incorrect then it will return a 400 error.",
        request_body=PostSerializer,
        responses={200: "Ok", 400: "Bad Request", 401: "Unauthorized", 404: "Not found"},
)
@swagger_auto_schema(
        method="delete",
        operation_summary="deletes the specific post with id_post of the author with the given id_author",
        operation_description="Deletes the specific post with id_post of the author with the given id_author. \
        The post has to be in the server. Otherwise it will return a 404 error. \
        The user making the request has to be the same as the author. Otherwise it will return a 401 error.",
        responses={204: "No Content", 400: "Bad Request", 401: "Unauthorized", 404: "Not found"},
)
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
@swagger_auto_schema(
        method="get",
        operation_summary="gets all the comments of the post with the given id_post",
        operation_description="Returns all the comments of the post with the given id_post. The post has to be in the server. Otherwise it will return a 404 error. Paginated (Optional).",
        responses={200: "Ok", 400: "Bad Request", 404: "Not found"},
)
@swagger_auto_schema(
        method="post",
        operation_summary="creates a comment for the post with the given id_post",
        operation_description="Creates a comment for the post with the given id_post. The post has to be in the server. Otherwise it will return a 404 error. \
        The user making the request has to be authenticated. Otherwise it will return a 401 error. \
        If the body of the comment is incorrect then it will return a 400 error. This will also send the created comment to the appropriate inboxes.",
        request_body=CommentSerializer,
        responses={201: "Created", 400: "Bad Request", 401: "Unauthorized", 404: "Not found"},
)
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
    # if the post is not in our server, we have to send a request to the server where the post is and get that specific post
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

        requestData = request.data.copy()
        requestData["author"] = commentAuthor.id
        requestData["post"] = post.id

        serializer = CommentSerializer(data=requestData, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            # send comment in inbox of post author
            inboxCommentData = requestData.copy()
            inboxCommentData["author"] = str(commentAuthor.id)
            inboxCommentData["post"] = str(post.id)
            commentInbox = {
                "author": str(post.author.id),
                "item": inboxCommentData
            }
            print(commentInbox)
            inboxSerializer = InboxSerializer(data=commentInbox, context={'request': request})
            if inboxSerializer.is_valid():
                inboxSerializer.save()
            else:
                return Response(inboxSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
        method="get",
        operation_summary = "gets all the likes of the post with the given id_post",
        operation_description="Returns all the likes of the post with the given id_post. The post has to be in the server. Otherwise it will return a 404 error.",
        responses={200: "Ok", 400: "Bad Request", 404: "Not found"},
)
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

@swagger_auto_schema(
        method="get",
        operation_summary="gets all the likes of the comment with the given id_comment",
        operation_description="Returns all the likes of the comment with the given id_comment. The comment has to be in the server. Otherwise it will return a 404 error.",
        responses={200: "Ok", 400: "Bad Request", 404: "Not found"},
)
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

@swagger_auto_schema(
        method="get",
        operation_summary="gets all the likes of the author with the given id_author",
        operation_description="Returns all the likes of the author with the given id_author. The author has to be in the server. Otherwise it will return a 404 error.",
        responses={200: "Ok", 400: "Bad Request", 404: "Not found"},
)
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

@swagger_auto_schema(
        method="get",
        operation_summary="gets all the items in the inbox of the author with the given id_author",
        operation_description="Returns all the items in the inbox of the author with the given id_author. The author has to be in the server. Otherwise it will return a 404 error. Paginated (Optional).\
            if the user is not authenticated then it will return a 401 error.",
        responses={200: "Ok", 401: "Unauthorized", 400: "Bad Request", 404: "Not found"},
)
@swagger_auto_schema(
        method="post",
        operation_summary="creates a new item in the inbox of the author with the given id_author",
        operation_description="Creates a new item in the inbox of the author with the given id_author. The author has to be in the server. Otherwise it will return a 404 error. \
        The post call must have items field and it can only be a follow, like, post, or comment. \
        If the body of the item is incorrect then it will return a 400 error.",
        request_body=InboxSerializer,
        responses={201: "Created", 400: "Bad Request", 401: "Unauthorized", 404: "Not found"},
)
@swagger_auto_schema(
        method="delete",
        operation_summary="deletes all the items in the inbox of the author with the given id_author",
        operation_description="Deletes all the items in the inbox of the author with the given id_author. The author has to be in the server. Otherwise it will return a 404 error. \
        The user making the request has to be the same as the author. Otherwise it will return a 401 error.",
        responses={204: "No Content", 400: "Bad Request", 401: "Unauthorized", 404: "Not found"},
)
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
                "author": request.build_absolute_uri(f"/api/authors/{id_author}"),
                "items": serializer.data,
            }
            return Response(response)
    
    if request.method == 'POST':
        if userId is None:
            return Response({"details":"Can't post to inbox anonymously"}, status=status.HTTP_401_UNAUTHORIZED)
        requestData = request.data.copy()
        requestData["author"] = author.id
        items = requestData.get("items")
        if not (isinstance(items, list)):
            items = [items]
        item = items[0]

        if item is None:
            return Response({"details":"item is required"}, status=status.HTTP_400_BAD_REQUEST)
        itemType = item.get("type").lower()

        if itemType == "like":
            # send the like to the author of the post/comments inbox - frontend
            likeAuthor = get_object_or_404(Author, id=item.get("author").get("id").split("/")[-1])
            likeData = item.copy()
            likeData["author"] = likeAuthor.id
            objectString = likeData.get("object")
            
            if objectString is not None or objectString != "":
                if "comments" in objectString:
                    commentId = objectString.split("/")[-1]
                    likeData["comment"] = get_object_or_404(Comment, id=commentId).id
                else:
                    likeData["comment"] = None
                if "posts" in objectString:
                    postId = objectString.split("/")[-1]
                    likeData["post"] = get_object_or_404(Post, id=postId).id
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
                requestData["item"] = item
            else:
                return Response(likeSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif itemType == "follow":
            # send the follow request to the objectAuthor's inbox - frontend
            actor = item.get("actor")
            object = item.get("object")
            if actor is None or object is None:
                return Response({"details":"actor and object are required"}, status=status.HTTP_400_BAD_REQUEST)
            
            actorAuthor = Author.objects.filter(id = actor.get("id").split("/")[-1]).first()
            objectAuthor = Author.objects.filter(id = object.get("id").split("/")[-1]).first()

            followRequest = FollowRequest.objects.filter(from_user=actorAuthor, to_user=objectAuthor).exists()
            
            if followRequest:
                # # unfollow them
                # # if the followed_user is in our server do this else send the request
                # Follower.objects.filter(follower=actorAuthor, followed_user=objectAuthor).delete()
                # return Response({"details":f"{actorAuthor.display_name} unfollowed {objectAuthor.display_name}"}, status=status.HTTP_200_OK)
                return Response({"details":f"{actorAuthor.display_name} already follows {objectAuthor.display_name}"}, status=status.HTTP_400_BAD_REQUEST)
            
            # followingData = {
            #     "follower": actorAuthor,
            #     "followed_user": objectAuthor
            # }
            followRequestData = {
                "from_user": actorAuthor,
                "to_user": objectAuthor
            }
            # create a follow request
            try:
                newFollowRequest = FollowRequest.objects.create(from_user=actorAuthor, to_user=objectAuthor)
                newFollowRequest.save()
                requestData["item"] = item
            except Exception as e:
                return Response({"details":str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # if its a post or comment check if the post or comment exists
        elif itemType == "post":
            postId = item.get("id").split("/")[-1]
            if postId is None:
                return Response({"details":"post id is required"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                # if the post is in our host do this else put the post in the requestData item
                post = Post.objects.get(id=postId)
                requestData["item"] = item
            except Post.DoesNotExist:
                return Response({"details":"post does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        elif itemType == "comment":
            # do you want to send the comment to the author of the post
            commentId = item.get("id").split("/")[-1]
            if commentId is None:
                return Response({"details":"comment id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                comment = Comment.objects.get(id=commentId)
                item["post"] = str(comment.post.id)
                requestData["item"] = item
                # if the author of the post is not in our domain send the request, else just add the comment to the inbox
            except Comment.DoesNotExist:
                return Response({"details":"comment does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({"details":"item type is required and should be one of post, comment, like, follow"}, status=status.HTTP_400_BAD_REQUEST)
        
        # create the inbox item

        inboxSerializer = InboxSerializer(data=requestData, context={'request': request})
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