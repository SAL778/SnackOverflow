from rest_framework.decorators import api_view, parser_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from .models import Author, Follower, FollowRequest, Post, Comment, Like, Inbox, Node
from .serializers import AuthorSerializer, FollowRequestSerializer, UserRegisterSerializer, UserLoginSerializer, PostSerializer, CommentSerializer, LikeSerializer, InboxSerializer
from django.contrib.auth import login, logout
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from django.views import View
from django.http import HttpResponse, HttpResponseNotFound
import requests, json, os
from django.core.paginator import Paginator
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import authenticate
import uuid
from itertools import chain
from api.utils import get_request_remote, check_content, post_request_remote
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
import base64
from django.http import Http404
import validators
from urllib.parse import unquote, quote

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
        serializer = UserRegisterSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# The following class from: https://github.com/dotja/authentication_app_react_django_rest/blob/main/backend/user_api/views.py
# Accessed 2024-02-22
class UserLogin(APIView):
    """
    Login a user
    """

    permission_classes = [permissions.AllowAny]
    # allow only session authentication for this view
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
            user = authenticate(email=request.data['email'], password=request.data['password'])

            if not user:
                # either the credentials are invalid or the user is inactive
                user = Author.objects.filter(email=request.data['email']).first()

                if user and user.check_password(request.data['password']):
                    # user exists but is inactive
                    assert user.is_active == False
                    return Response({"detail": "User has not been activated yet."}, status=status.HTTP_403_FORBIDDEN)
                else:
                    return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            
            else:
                serializer = AuthorSerializer(user, data=request.data, partial=True)
                if serializer.is_valid():
                    login(request, user)
                    return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# The following class from: https://github.com/dotja/authentication_app_react_django_rest/blob/main/backend/user_api/views.py
# Accessed 2024-02-22
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


# The following class from: https://github.com/dotja/authentication_app_react_django_rest/blob/main/backend/user_api/views.py
# Accessed 2024-02-22
class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    # allow only session authentication for this view
    authentication_classes = (SessionAuthentication,)
    
    @swagger_auto_schema(
        operation_summary="get the user",   
        operation_description="Returns the user data.",
        responses={200: "Ok"},
    )
    def get(self, request):
        serializer = AuthorSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
    authors = Author.objects.filter(is_remote=False, is_staff=False)
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

    serializer = AuthorSerializer(authors, many=True)
    response["items"] = serializer.data
    return Response(response)

@swagger_auto_schema(
        method="get",
        operation_summary="gets the authors with the given id",   
        operation_description="Returns the author with the id. The author has to be in the server. Otherwise it will return a 404 error.",
        responses={200: "Ok", 400: "Bad Request", 404: "Not found"},
)
@swagger_auto_schema(
        method="put",
        operation_summary="creates an authors on the server",   
        operation_description="It creates an author on the server. If the author exists then it will throw an error. It will return the author's data.",
        request_body=AuthorSerializer,
        responses={200: "Ok", 400: "Bad Request", 404: "Not found"},
)
@api_view(['GET', 'PUT', 'POST'])
def get_and_update_author(request, id):
    """
    Get a single profile on the server by ID
    """
    if request.method == 'GET':
        author = get_object_or_404(Author, id=id)
        serializer = AuthorSerializer(author)
        return Response(serializer.data)

    if request.method == 'PUT':
        author = get_object_or_404(Author, id=id)
        serializer = AuthorSerializer(author, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
    if request.method == 'POST':
        # mainly to create a remote author in our local db
        serializer = AuthorSerializer(data=request.data)
        if serializer.is_valid():
            # remove trailing slash from url
            request.data['id'] = request.data.get('id').rstrip('/')
            # extract uuid from url/full id
            author_id = request.data.get('id').split('/')[-1]
            
            author = Author.objects.create(
                type=request.data.get('type'),
                id=uuid.UUID(author_id),
                host=request.data.get('host'),
                display_name=request.data.get('displayName'),
                url=request.data.get('url'),
                github=request.data.get('github'),
                profile_image=request.data.get('profileImage'),
                is_remote=True
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

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

    followers_set = set()
    for follower_object in followers:
        followers_set.add(follower_object.follower)

    serializer = AuthorSerializer(followers_set, many=True)
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

    # check if id_follower is a uuid or percent encoded url
    if validators.uuid(id_follower):
        id_follower = uuid.UUID(id_follower)
    else:
        try:
            id_follower = unquote(id_follower)
            # extract uuid from url
            id_follower = id_follower.split('/')[-1]
            # confirm it is a uuid
            id_follower = uuid.UUID(id_follower)
        except:
            return Response({'details': 'id_follower can either be a uuid or percent encoded url with uuid in it'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        follower_object = get_object_or_404(Follower, follower_id=id_follower, followed_user_id=id_author)
        serializer = AuthorSerializer(follower_object.follower)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # create a new follower
        author = Author.objects.filter(id=id_follower)
        if author.exists() and author.count() == 1:
            follower, created = Follower.objects.get_or_create(follower_id=id_follower, followed_user_id=id_author)

            print("ACCEPTING FOLLOW REQUEST ==> CREATE NEW FOLLOW")
            print("before follower host: ", follower.follower.host)

            # send a get request to authors/<uuid:requesting_author>/followers/<path:foreign_author_id>/accept
            if "testing" in follower.follower.host:
                try:
                    print("testing for team OK")
                    print("follower host: ", follower.follower.host)
                    print("follower id: ", follower.follower.id)
                    print("path: ", f"authors/{follower.follower.id}/followers/{quote(follower.followed_user.url)}/accept")
                    response = get_request_remote(host_url=follower.follower.host, path=f"authors/{follower.follower.id}/followers/{quote(follower.followed_user.url)}/accept")
                except:
                    print("ERROR sending request to /accept for team OK")


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

    serializer = AuthorSerializer(followings_set, many=True)
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
    # print(friends)

    friends_set = set()
    for friend_object in friends:
        friends_set.add(friend_object.followed_user)

    serializer = AuthorSerializer(friends_set, many=True)
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
        operation_summary="gets all the sent follow requests of the author with the given id",
        operation_description="Returns all the sent follow requests of the author with the given id. The author has to be in the server. Otherwise it will return a 404 error.",
        responses={200: "Ok", 400: "Bad Request", 404: "Not found"},
)
@api_view(['GET'])
def get_sent_follow_requests(request,id):
    """
    Get all sent friend requests
    """

    author= get_object_or_404(Author, id=id)
    sent_follow_requests = FollowRequest.objects.filter(from_user_id=id)
    serializer = FollowRequestSerializer(sent_follow_requests, context={'request': request}, many=True)
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

        # if sending follow request to remote author, make sure that remote author has been added to our local db before hand.
        author_receiver = Author.objects.filter(id=id_author)

        if author.exists() and author.count() == 1 and author_receiver.exists() and author_receiver.count() == 1:
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
def get_all_friends_follows_posts(request, id_author):
    """
    Get all friends and follows posts
    primary used in the home feed (friends stream)
    This will have all the public posts of the people I am following 
    and the friends only posts of the people I am friends with (they follow and I follow them)
    """
    userId = id_author
    print("userId: ", userId)
    print("getting all friends and follows posts")
    if request.method == 'GET':
        if userId is None:
            return Response({"details":"User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            following = Follower.objects.filter(follower__id=userId)

            followers = Follower.objects.filter(followed_user__id=userId)

            friends = following.filter(followed_user__in=followers.values_list('follower', flat=True))

            public_posts = Post.objects.filter(author__in=following.values_list('followed_user', flat=True), visibility="PUBLIC")

            friends_posts = Post.objects.filter(author__in=friends.values_list('followed_user', flat=True), visibility="FRIENDS")

            own_friends_only_posts = Post.objects.filter(author__id=userId, visibility="FRIENDS")
            
            # get all the following whose is_remote is true
            remote_following = following.filter(followed_user__is_remote=True)
            remote_following_posts_list = []
            # get all the posts of the remote following
            for remote_author in remote_following:
                response = get_request_remote(host_url=remote_author.followed_user.host, path=f"authors/{remote_author.followed_user.id}/posts/")

                if response is not None:
                    if response.status_code == 200:
                        all_posts = response.json().get('items')
                        for post in all_posts:
                            # check if the post type is public
                            # filter the post so that the post id is not equal to the post source
                            print("source: ", post.get("source"))
                            print("id: ", post.get("id"))
                            if post.get("source") and post.get("source") != post.get("id"):
                                print("going to continue")
                                continue
                            else:
                                print("good")
                            if post.get('visibility').upper() == "PUBLIC":
                                post = check_content(post, request)
                                remote_following_posts_list.append(post)
                    else:
                        print("remote_following_posts error: ", response.status_code)
            print("remote_following_posts_list: ", remote_following_posts_list)
            # get all the friends whose is_remote is true            
            remote_friends = friends.filter(followed_user__is_remote=True)
            print("remote_friends: ", remote_friends)
            remote_friends_posts_list = []
            # get all the posts of the remote friends
            for remote_author in remote_friends:
                response = get_request_remote(host_url=remote_author.followed_user.host, path=f"authors/{remote_author.followed_user.id}/posts/")
                
                if response is not None:
                    if response.status_code == 200:
                        all_posts = response.json().get('items')

                        for post in all_posts:
                            print("source 2: ", post.get("source"))
                            print("id 2: ", post.get("id"))
                            if post.get("source") and post.get("source") != post.get("id"):
                                print("going to continue 2")
                                continue
                            else:
                                print("good 2")
                            if post.get('visibility').upper() == "FRIENDS":
                                print("freins post")
                                post = check_content(post, request)
                                remote_friends_posts_list.append(post)
            # print("remote_friends_posts_list: ", remote_friends_posts_list)

            posts = public_posts.union(friends_posts)

            posts = posts.union(own_friends_only_posts)
            # pagination
            page_number = request.query_params.get('page', 0)
            size = request.query_params.get('size', 0)
            if int(page_number) and int(size):
                paginator = Paginator(posts, size)
                posts = paginator.get_page(page_number)
                serializer = PostSerializer(posts, context={'request': request}, many=True)
            
                #responseSerializer = PostSerializer(remote_following_posts.union(remote_friends_posts), context={'request': request}, many=True)
                items = serializer.data + remote_following_posts_list + remote_friends_posts_list
                # print("items: ", items)
                # items = serializer.data + responseSerializer.data
                response = {
                    "type": "posts",
                    "items": items,
                }
                return Response(response)
            else:
                print("before serializer")
                try:
                    serializer = PostSerializer(posts, context={'request': request}, many=True)
                    #responseSerializer = PostSerializer(remote_following_posts.union(remote_friends_posts), context={'request': request}, many=True)
                    items = serializer.data + remote_following_posts_list + remote_friends_posts_list
                    # print("items: ", items)
                    # items = serializer.data + responseSerializer.data
                    response = {
                        "type": "posts",
                        "items": items,
                    }
                    return Response(response)
                except Exception as e:
                    print(str(e))
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
@parser_classes([MultiPartParser, FormParser, JSONParser])
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
            return Response(status=status.HTTP_404_NOT_FOUND)
        elif author.is_remote:
            response = get_request_remote(host_url=author.host, path=f"authors/{id_author}/posts/")

            if response is not None and response.status_code == 200:
                all_posts = response.json().get('items')
                posts = []
                for post in all_posts:
                    # check if the post type is public
                    post = check_content(post, request)
                    if post.get('visibility').upper() == "PUBLIC":
                        posts.append(post)
                    if userId is not None:
                        follower = Follower.objects.filter(follower__id=id_author, followed_user__id=userId).exists()
                        following = Follower.objects.filter(follower__id=userId, followed_user__id=id_author).exists()
                        if follower and following:
                            if post.get('visibility').upper() == "FRIENDS":
                                posts.append(post)
                if int(page_number) and int(size):
                    paginator = Paginator(posts, size)
                    posts = paginator.get_page(page_number)
                    response = {
                        "type": "posts",
                        "items": posts,
                    }
                    return Response(response)
                else:
                    response = {
                        "type": "posts",
                        "items": posts,
                    }
                    return Response(response)
        else:
            # the author is in our local server
            print("userId remote",userId)
            if userId is None:
                posts = Post.objects.filter(author=author, visibility="PUBLIC")
            elif userId == id_author:
                posts = Post.objects.filter(author=author)
            else:
                # check if the user is a friend of the author
                follower = Follower.objects.filter(follower__id=id_author, followed_user__id=userId).exists()
                following = Follower.objects.filter(follower__id=userId, followed_user__id=id_author).exists()
                print("user: ", user)
                print("user remote", user.is_remote)
                if (follower and following) or user.is_remote:
                    posts = Post.objects.filter(author=author, visibility__in=["PUBLIC", "FRIENDS"])
                else:
                    posts = Post.objects.filter(author=author, visibility="PUBLIC")
            print("all posts",posts)
            posts = posts.order_by('-published')
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
        print("inside post")
        if userId != id_author:
            print("userId",userId)
            print("id_author",id_author)
            return Response({"detail":"Can't create post for another user"}, status=status.HTTP_401_UNAUTHORIZED)
        # requestData = dict(request.data)
        requestData = request.data
        # REQUest data is query dict
        serializer = PostSerializer(data=requestData, context={'request': request})

        if serializer.is_valid():
            serializer.save(author=author)
            print("Post created")
            # send the serializer.data (post) to the inbox of the author's followers
            # send the post to the author's followers or friends
            # check if the post is coming from our host. If its from our host do this else just add that to the inbox (everything is correct in that case)

            postId = serializer.data.get("id").split("/")[-1]
            post = Post.objects.filter(id=postId).first()
            postType = post.visibility

            # slice out the data:image... section of the base64 string
            if post.contentType == "image/jpeg;base64":
                post.content = post.content[23:]
            elif post.contentType == "image/png;base64":
                post.content = post.content[22:]

            # set the origin for the post
            if post.origin == "":
                post.origin = serializer.data.get("id")
            if post.source == "":
                post.source = serializer.data.get("id")
            post.save()
            
            if postType == "PUBLIC":
                print("Public post")
                followers = Follower.objects.filter(followed_user__id=id_author)
                for follower in followers:
                    # check if the follower is in another server and if it is then send the request
                    followerAuthor = Author.objects.filter(id=follower.follower.id).first()
                    if followerAuthor.is_remote:
                        print("Remote author")
                        # send the request to the remote server
                        host_url = followerAuthor.host

                        node = Node.objects.filter(host_url=host_url).first()

                        request_url = f"{node.api_url}authors/{follower.follower.id}/inbox"

                        post_payload = {
                            "type":"inbox",
                            "author": f"{node.api_url}authors/{follower.follower.id}",
                            "items":[serializer.data],
                        }

                        if "testing" in request_url:
                            print("testing url")
                            post_payload = serializer.data
                            print("post payload for team ok", post_payload)

                        response = requests.post(request_url, json=post_payload, headers={'Authorization': f'Basic {node.base64_authorization}'})
                        if response.status_code ==200:
                            print("Post sent to the remote server inbox")
                        else:
                            print("Error sending the post to the remote server inbox")
                            print(response.status_code, response.text)
                            return Response(response.text, status=response.status_code)
                    else:
                        requestData = serializer.data
                        inboxSerializer = InboxSerializer(data=requestData, context={'request': request})
                        if inboxSerializer.is_valid():
                            inboxSerializer.save()
            elif postType == "FRIENDS":
                print("Friends post")
                followers = Follower.objects.filter(followed_user__id=id_author)
                for follower in followers:
                    followerObject = Follower.objects.filter(follower__id=id_author, followed_user__id=follower.follower.id).first()
                    if followerObject is not None:
                        friendAuthor = Author.objects.filter(id=follower.follower.id).first()
                        if friendAuthor.is_remote:
                            # send the request to the remote server
                            host_url = friendAuthor.host
                            node = Node.objects.filter(host_url=host_url).first()
                            request_url = f"{node.api_url}authors/{follower.follower.id}/inbox"
                            post_payload = {
                                "type":"inbox",
                                "author": f"{node.api_url}authors/{follower.follower.id}",
                                "items":[serializer.data],
                            }
                            # TODO: for friends only post might have to add a viewing_author field with the id to the payload
                            # like this
                            # { serializer.data, "viewing_author": id_author}
                            if "testing" in request_url:
                                print("testing url")
                                post_payload = serializer.data
                                print("post payload for team ok", post_payload)
                            
                            response = requests.post(request_url, json=post_payload, headers={'Authorization': f'Basic {node.base64_authorization}'})
                            if response.status_code ==200:
                                print("Post sent to the remote server inbox")
                            else:
                                print("Error sending the post to the remote server inbox")
                                print(response.status_code)
                                return Response({"details":"wrong response"}, status=response.status_code)
                        else:
                            requestData = serializer.data
                            inboxSerializer = InboxSerializer(data=requestData, context={'request': request})
                            if inboxSerializer.is_valid():
                                inboxSerializer.save()
            else:
                print("unlisted post")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Here:",serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
        method="get",
        operation_summary="gets the image of the post with the given id_post and id_author",
        operation_description="Returns the image of the post with the given id_post. The post has to be in the server. Otherwise it will return a 404 error.",
        responses={200: "Ok", 404: "Not found"},
)
@api_view(['GET'])
def get_image(request, id_author, id_post):
    author = Author.objects.filter(id=id_author).first()
    if not author:
        raise Http404("Author does not exist.")
    if author.is_remote:
        response = get_request_remote(host_url=author.host, path=f"authors/{id_author}/posts/{id_post}/image")

        if response is not None and response.status_code == 200:
            print("response", response)
            return HttpResponse(response.content, content_type=response.headers.get('Content-Type'))
    try:
        post = Post.objects.get(id=id_post, author__id=id_author)

        if not post.contentType.startswith("image/"):
            raise Http404("No image found.")

        # if full dataURL given, parse out, otherwise decode as given
        if post.content[:4] == "data":
            format, imgstr = post.content.split(';base64,') 
            data = base64.b64decode(imgstr) # Decoding the base64 string to image data
        else:
            data = base64.b64decode(post.content)

        return HttpResponse(data, content_type=post.contentType) # correct MIME type
    
    except Post.DoesNotExist:
        raise Http404("Post does not exist.")

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
    print("wasdasdjasjdnasdjnasdjn")
    user = request.user
    if(isinstance(user, Author)):
        userId = user.id
    else:
        userId = None

    if request.method == 'GET':
        print("id_author", id_author)
        post_author = get_object_or_404(Author, id=id_author)
        print("post_author",post_author)
        if post_author.is_remote:
            # send the request to the remote server
            response = get_request_remote(host_url=post_author.host, path=f"authors/{id_author}/posts/{id_post}")

            if response is not None:
                if response.status_code == 200:
                    response_json = response.json()
                    response_json["author"] = response_json.get('author').get("id").split("/")[-1]
                    response_json["author"] = Author.objects.filter(id = response_json["author"]).first()
                    response_json = check_content(response_json, request)

                    # create the new post object
                    new_post = Post(response_json)
                    new_post.type = response_json.get('type')
                    new_post.count = response_json.get('count')
                    new_post.comments = response_json.get('comments')
                    new_post.author = response_json["author"]
                    new_post.id = response_json.get('id').split("/")[-1]
                    new_post.title = response_json.get('title')
                    new_post.source = response_json.get('source')
                    new_post.origin = response_json.get('origin')
                    new_post.contentType = response_json.get('contentType')
                    new_post.content = response_json.get('content')
                    new_post.description = response_json.get('description')
                    new_post.published = response_json.get('published')
                    new_post.visibility = response_json.get('visibility')
                    new_post.sharedBy = response_json.get('sharedBy')
                    postSerializer = PostSerializer(new_post, context={'request': request})
                    return Response(postSerializer.data)
                else:
                    return Response(response.text, status=response.status_code)
                        
        print("before post")
        post = get_object_or_404(Post, id=id_post)
        print("after post")
        serializer = PostSerializer(post, context={'request': request})
        if post.visibility == "PUBLIC" or userId == id_author:
            print("public post")
            return Response(serializer.data)
        elif post.visibility == "FRIENDS":
            print("friends post")
            if userId is None:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            follower = Follower.objects.filter(follower__id=id_author, followed_user__id=userId).exists()
            following = Follower.objects.filter(follower__id=userId, followed_user__id=id_author).exists()
            if (follower and following) or user.is_remote:
                return Response(serializer.data)
            else:
                print("Post not found with friends")
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
    not using this endpoint
    """
    user = request.user
    if(isinstance(user, Author)):
        userId = user.id
    else:
        userId = None
    # if the post is not in our server, we have to send a request to the server where the post is and get that specific post
    if request.method == 'GET':
        post_author = get_object_or_404(Author, id=id_author)
        if post_author.is_remote:
            # send the request to the remote server
            response = get_request_remote(host_url=post_author.host, path=f"authors/{id_author}/posts/{id_post}/comments")

            if response is not None:
                if response.status_code == 200:
                    return_response = response.json()
                    if "comments" in return_response and "items" not in return_response:
                        return_response["items"] = return_response["comments"]
                    return Response(return_response)
                else:
                    return Response(response.text, status=response.status_code)
                
        post = get_object_or_404(Post, id=id_post)
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
        post_author = get_object_or_404(Author, id=id_author)
        if post_author.is_remote:
            # send the request to the remote server            
            response = post_request_remote(host_url=post_author.host, path=f"authors/{id_author}/posts/{id_post}/comments", data=request.data)
            
            if response is not None:
                if response.status_code == 201 or response.status_code == 200:
                    return Response({"details":"comments posted properly"}, status=response.status_code)
                else:
                    return Response({"details":"comment wrong status code"}, status=response.status_code)
            else:
                return Response({"details": "Error posting comment to remote server"}, status=status.HTTP_400_BAD_REQUEST)
            
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
            # print(commentInbox)
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
    post_author = get_object_or_404(Author, id=id_author)
    if post_author.is_remote:

        print("BEFORE RESPONSE")
        # send the request to the remote server
        response = get_request_remote(host_url=post_author.host, path=f"authors/{id_author}/posts/{id_post}/likes")
        print("AFTER RESPONSE")

        if response is not None:
            print("RESPONSE CODE: ", response.status_code)
            if response.status_code == 200:
                return Response(response.json())
            else:
                return Response(response.text, status=response.status_code)
        else:
            return Response({"details": "Error getting likes from remote server"}, status=status.HTTP_400_BAD_REQUEST)
        
    post = get_object_or_404(Post, id=id_post, author__id=id_author)
    likes = Like.objects.filter(post=post)
    
    serializer = LikeSerializer(likes, context={'request': request}, many=True)
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
    if author.is_remote:
        # send the request to the remote server
        response = get_request_remote(host_url=author.host, path=f"authors/{id_author}/liked")

        if response is not None:
            if response.status_code == 200:
                # never used
                #TODO: change url
                return Response(response.json())
            else:
                return Response(response.text, status=response.status_code)
            
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

    print("User: ", userId)

    if request.method == 'GET':
        author = get_object_or_404(Author, id=id_author)

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
        requestData["author"] = id_author
        items = requestData.get("items")
        if not (isinstance(items, list)):
            items = [items]
        item = items[0]

        if item is None:
            return Response({"details":"item is required"}, status=status.HTTP_400_BAD_REQUEST)
        itemType = item.get("type").lower()

        author = Author.objects.filter(id=id_author).first()
        
        if itemType == "like":
            # send the like to the author of the post/comments inbox - frontend
            likeAuthor = get_object_or_404(Author, id=item.get("author").get("id").split("/")[-1])
            if author.is_remote:
                # Send it to the post author’s inbox, if it’s a remote author, 
                # then send the inbox request to another server and do nothing on local server 
                # except create the payload for the request, else do what we are doing currently
                # send the request to the remote server
                host_url = author.host
                node = Node.objects.filter(host_url=host_url).first()
                request_url = f"{node.api_url}authors/{id_author}/inbox"
                postId = item.get("object").split("/")[-1]
                item["object"] = f"{node.api_url}authors/{id_author}/posts/{postId}"
                like_payload = {
                    "type":"inbox",
                    "author": f"{node.api_url}authors/{id_author}",
                    "items":[{
                        "type":"like",
                        "author": AuthorSerializer(likeAuthor, context={'request': request}).data,
                        "summary": likeAuthor.display_name + " liked your post",
                        "object": item.get("object"),
                    }],
                }

                print("LIKE PAYLOAD: ", like_payload)
                
                if "testing" in request_url:
                    like_payload = {
                        "type":"like",
                        "author": AuthorSerializer(likeAuthor, context={'request': request}).data,
                        "summary": likeAuthor.display_name + " liked your post",
                        "object": item.get("object"),
                    }
                    print("sending to team OK like payload", like_payload)
                
                response = post_request_remote(host_url=author.host, path=f"authors/{id_author}/inbox", data=like_payload)

                print("AFTER LIKE PAYLOAD SENDING REMOTE")

                if response is not None:
                    if response.status_code ==200 or response.status_code == 201: 
                        print("Like sent to the remote server inbox")
                        return Response({"details":"like sent"}, status=response.status_code)
                    else:
                        print("Error sending the like to the remote server inbox")
                        print(response.status_code)
                        return Response({"details":"like sent error"}, status=response.status_code)
                else:
                    return Response({"details":"Error sending the like to the remote server inbox"}, status=status.HTTP_400_BAD_REQUEST)
                

            likeData = item.copy()
            likeData["author"] = likeAuthor.id
            objectString = likeData.get("object")
            if likeAuthor.is_remote:
                # get the proper post id
                if objectString is not None or objectString != "":
                    if "comments" in objectString:
                        return Response({"details":"object have a comment"}, status=status.HTTP_200_OK)
                    else:
                        if "testing" in likeAuthor.host:
                            print("testing request for team ok")
                            if objectString is not None or objectString != "":
                                if "posts" in objectString:
                                    if "comments" in objectString:
                                        postId = objectString.split("/")[-3]
                                    else:
                                        postId = objectString.split("/")[-1]

                                    likeData["post"] = get_object_or_404(Post, id=postId).id
                                    print(likeData["post"])
                                else:
                                    return Response({"details":"object should have a post"}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                return Response({"details":"object is required"}, status=status.HTTP_400_BAD_REQUEST)
                        elif "linkup" in likeAuthor.host:
                            fakePostId = objectString.split("/")[-1]
                            print("fakePostId: ", fakePostId)
                            request_url_fakepostId = "".join(["authors", objectString.split("authors")[1]])
                            #make a request to the remote server to get the post
                            response = get_request_remote(host_url=likeAuthor.host, path=f"{request_url_fakepostId}")
                            print(request_url_fakepostId)
                            if response is not None:
                                print(response.status_code)
                                if response.status_code == 200:
                                    print("getting post")
                                    post = response.json()
                                    print(post)
                                    postId = post.get("source").split("/")[-1]
                                    print(postId)
                                    likeData["post"] = get_object_or_404(Post, id=postId).id
                                    print(likeData["post"])
                                else:
                                    return Response(response.text, status=response.status_code) 
                            else:
                                return Response({"details":"Error getting the post from the remote server"}, status=status.HTTP_400_BAD_REQUEST)
                        elif "3rdTeam" in likeAuthor.host:
                            print("likeAuthor.host: ", likeAuthor.host)
                        else:
                            # for our remote node
                            if objectString is not None or objectString != "":
                                if "posts" in objectString:
                                    if "comments" in objectString:
                                        postId = objectString.split("/")[-3]
                                    else:
                                        postId = objectString.split("/")[-1]

                                    likeData["post"] = get_object_or_404(Post, id=postId).id
                                else:
                                    return Response({"details":"object should have a post"}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                return Response({"details":"object is required"}, status=status.HTTP_400_BAD_REQUEST)
                            
            else:
                if objectString is not None or objectString != "":
                    if "posts" in objectString:
                        if "comments" in objectString:
                            postId = objectString.split("/")[-3]
                        else:
                            postId = objectString.split("/")[-1]

                        likeData["post"] = get_object_or_404(Post, id=postId).id
                    else:
                        return Response({"details":"object should have a post"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"details":"object is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            likeExists = Like.objects.filter(author=likeAuthor, post=likeData["post"]).exists()
            
            print("checking likeExists")

            if likeExists:
                print("likeExists")
                return Response({"details":"like already exists"}, status=status.HTTP_400_BAD_REQUEST)

            likeSerializer = LikeSerializer(data=likeData, context={'request': request})
            print("likeSerializer created")
            if likeSerializer.is_valid():
                print("saving likeSerializer")
                likeSerializer.save()
                requestData["item"] = likeSerializer.data
            else:
                return Response(likeSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif itemType == "follow":
            # send the follow request to the objectAuthor's inbox - frontend
            print("we are in follow")

            actor = item.get("actor")
            object = item.get("object")

            print("actor: ", actor)
            print("object: ", object)
            if actor is None or object is None:
                return Response({"details":"actor and object are required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # actor - the person sending the request
            # object - the person receiving the request
            actorId = actor.get("id").split("/")[-1]
            objectId = object.get("id").split("/")[-1]

            print("actorId: ", actorId)
            print("objectId: ", objectId)

            if objectId != str(id_author):
                return Response({"details":"Can't send follow request to someone else's inbox"}, status=status.HTTP_401_UNAUTHORIZED)

            
            actorAuthor = Author.objects.filter(id = actorId).first()
            objectAuthor = Author.objects.filter(id = objectId).first()
            if actorAuthor is None:
                # actorAuthor is most likely from another server
                # create a new author with the actor's details
                print("Creating actor author...")
                actorAuthor = Author.objects.create(
                    id=actorId, 
                    host=actor.get("host"), 
                    display_name=actor.get("displayName"), 
                    url=actor.get("url"),
                    github=actor.get("github"),
                    profile_image=actor.get("profileImage"),
                    is_remote=True
                )
                print("after creating actor author...")
            if objectAuthor is None or objectAuthor.is_remote:
                # the id_author is remote now
                # most likely a remote author,  create the author
                # need to send to the remote user inbox
                print("Creating object author...")
                if objectAuthor is None:
                    objectAuthor = Author.objects.create(
                        id=objectId, 
                        host=object.get("host"), 
                        display_name=object.get("displayName"), 
                        url=object.get("url"),
                        github=object.get("github"),
                        profile_image=object.get("profileImage"),
                        is_remote=True
                    )
                print("after creating object author...")
                
                author = Author.objects.filter(id=id_author).first()

                print("Author in creating object author: ", author)

                # now we need to send it to remote server
                node = Node.objects.filter(host_url = author.host).first()
                print("Node: ", node)

                request_url = f"{node.api_url}authors/{id_author}/inbox"
                print("Request url: ", request_url)
                
                actorAuthorSerializerDict = AuthorSerializer(actorAuthor, context={'request': request}).data
                objectAuthorSerializerDict = AuthorSerializer(objectAuthor, context={'request': request}).data

                print(actorAuthorSerializerDict)
                print(objectAuthorSerializerDict)

                actor["id"] = f"{actorAuthorSerializerDict.get('host')}api/authors/{actorId}"
                object["id"] = f"{objectAuthorSerializerDict.get('host')}api/authors/{objectId}"

                payload = {
                    "type": "inbox",
                    "author": f"{node.api_url}/authors/{id_author}",
                    "items": [
                        {
                            "type": "follow",
                            "summary": f"{actor.get('displayName')} wants to follow {object.get('displayName')}",
                            "actor": actor,
                            "object": object
                        }
                    ]
                }

                if "testing" in request_url:
                    payload = {
                        "type": "follow",
                        "summary": f"{actor.get('displayName')} wants to follow {object.get('displayName')}",
                        "actor": actor,
                        "object": object
                    }
                    print("sending to team OK follow payload", payload)


                print("encoding: ", node.base64_authorization)

                try:
                    response = requests.post(request_url, json=payload, headers={'Authorization': f'Basic {node.base64_authorization}'})
                except Exception as e:
                    print("Error sending the follow request to the remote server inbox")
                    print(str(e))
                    return Response({"details":str(e)}, status=status.HTTP_400_BAD_REQUEST)

                # print("Response: ", response.status_code, response.json())
                

                if (response.status_code != 201) and (response.status_code != 200):
                    print("Not 201")
                    print(response.status_code)
                    print(response.json())
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                else:
                    print("Yes 201 or 200")

                    followRequest = FollowRequest.objects.filter(from_user=actorAuthor, to_user=objectAuthor).exists()
            
                    if followRequest:
                        return Response({"details":f"{actorAuthor.display_name} already follows {objectAuthor.display_name}"}, status=status.HTTP_400_BAD_REQUEST)
                    
                    followRequestData = {
                        "from_user": actorAuthor,
                        "to_user": objectAuthor
                    }
                    # create a follow request
                    try:
                        newFollowRequest = FollowRequest.objects.create(from_user=actorAuthor, to_user=objectAuthor)
                        serializer = FollowRequestSerializer(newFollowRequest, context={'request': request})
                        requestData["item"] = serializer.data
                    except Exception as e:
                        return Response({"details":str(e)}, status=status.HTTP_400_BAD_REQUEST)
                    # if resposne.json exist sent it
                    # else return the response
                    try:
                        return Response(response.json(), status=response.status_code)
                    except Exception as e:
                        return Response({"details":"correct response"}, status=response.status_code)

            followRequest = FollowRequest.objects.filter(from_user=actorAuthor, to_user=objectAuthor).exists()
            
            if followRequest:
                return Response({"details":f"{actorAuthor.display_name} already follows {objectAuthor.display_name}"}, status=status.HTTP_400_BAD_REQUEST)
            
            followRequestData = {
                "from_user": actorAuthor,
                "to_user": objectAuthor
            }
            # create a follow request
            try:
                newFollowRequest = FollowRequest.objects.create(from_user=actorAuthor, to_user=objectAuthor)
                serializer = FollowRequestSerializer(newFollowRequest, context={'request': request})
                print("follow request created")
                requestData["item"] = serializer.data
            except Exception as e:
                return Response({"details":str(e)}, status=status.HTTP_400_BAD_REQUEST)

        elif itemType == "post":
            # ignore it

            # postId = item.get("id").split("/")[-1]
            # if postId is None:
            #     return Response({"details":"post id is required"}, status=status.HTTP_400_BAD_REQUEST)
            # try:
            #     # if the post is in our host do this else put the post in the requestData item
            #     post = Post.objects.get(id=postId)
            #     requestData["item"] = item
            # except Post.DoesNotExist:
            #     return Response({"details":"post does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_200_OK)
        
        elif itemType == "comment":
            # I think post will always be in our server
            # if the post is not in our server then make a request to the server where the post is and send the comment
            if author.is_remote:
                # send the request to the remote server
                host_url = author.host
                node = Node.objects.filter(host_url=host_url).first()
                request_url = f"{node.api_url}authors/{id_author}/inbox"
                item_author_id = item.get("author").get("id").split("/")[-1]
                item_author = Author.objects.filter(id=item_author_id).first()
                item["author"] = AuthorSerializer(item_author, context={'request': request}).data
                psot_id =item["post"]["id"].split("/")[-1]
                item["post"]["id"] = f"{node.api_url}authors/{id_author}/posts/{psot_id}"
                if "testing" in request_url:
                    item["post"] = item["post"]["id"]
                    print("item post sending to team ok", item["post"])
                    comment_payload = item
                    print("sending to team OK comment payload", comment_payload)
                else:
                    item["id"] = item.get("post").get("id")
                    comment_payload = {
                        "type":"inbox",
                        "author": f"{node.api_url}authors/{id_author}",
                        "items":[item],
                    }

                    print("ITEM: ", item)
                    print("COMMENT PAYLOAD for team HTTP: ", comment_payload)

                response = requests.post(request_url, json=comment_payload, headers={'Authorization': f'Basic {node.base64_authorization}'})
                if response.status_code ==201 or response.status_code ==200:
                    print("Comment sent to the remote server inbox")
                    try:
                        return Response(response.json(), status=response.status_code)
                    except Exception as e:
                        return Response({"details":"correct response"}, status=response.status_code)
                else:
                    print("Error sending the comment to the remote server inbox")
                    print(response.status_code, response.text)
                    return Response(response.text, status=response.status_code)
            commentAuthorId = item.get("author").get("id").split("/")[-1]

            # check if the comment author is in our server
            commentAuthor = Author.objects.filter(id=commentAuthorId).first()
            if commentAuthor is None:
                # do something - create an author copy
                print("Comment author is not in our server")
                return
            commentData = item.copy()
            commentData["author"] = commentAuthor.id
            
            if commentAuthor.is_remote:
                # get the proper post id
                if "linkup" in commentAuthor.host:
                    getPostUrl = item.get("id").split("/")[:-2]
                    getPostUrl = "/".join(getPostUrl)
                    print("getPostUrl: ", getPostUrl)
                    request_url_fakepostId = "".join(["authors", getPostUrl.split("authors")[1]])
                    print("request_url_fakepostId: ", request_url_fakepostId)
                    response = get_request_remote(host_url=commentAuthor.host, path=f"{request_url_fakepostId}")
                    if response is not None:
                        if response.status_code == 200:
                            print("getting post for commenting")
                            post = response.json()
                            print(post)
                            postId = post.get("source").split("/")[-1]
                            print(postId)
                            commentData["post"] = get_object_or_404(Post, id=postId).id
                            print(commentData["post"])
                        else:
                            return Response(response.text, status=response.status_code)
                    else:
                        print("response is none")
                elif "testing" in commentAuthor.host:
                    print("testing comment request for team ok")
                    print(item.get("post"))
                    postId = item.get("post").split("/")[-1]
                    commentData["post"] = get_object_or_404(Post, id=postId).id
                    
                elif "3rdTeam" in commentAuthor.host:
                    pass
                else:
                    # our own remote server
                    commentData["post"] = item.get("post").get("id").split("/")[-1]    
            else:
                commentData["post"] = item.get("post").get("id").split("/")[-1]
            #increment the comment count in the post
            post = Post.objects.filter(id=commentData["post"]).first()
            post.count += 1
            post.save()

            commentSerializer = CommentSerializer(data=commentData, context={'request': request})
            if commentSerializer.is_valid():
                commentSerializer.save()
                requestData["item"] =  commentSerializer.data
            else:
                print(commentSerializer.errors)
                return Response(commentSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"details":"item type is required and should be one of post, comment, like, follow"}, status=status.HTTP_400_BAD_REQUEST)
        
        # create the inbox item

        inboxSerializer = InboxSerializer(data=requestData, context={'request': request})
        if inboxSerializer.is_valid():
            inboxSerializer.save()
            return Response(inboxSerializer.data, status=status.HTTP_201_CREATED)

        print("inboxSerializer.errors")
        print(inboxSerializer.errors)
        return Response(inboxSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    if request.method == 'DELETE':
        if userId is None:
            return Response({"details":"Can't delete inbox anonymously"}, status=status.HTTP_401_UNAUTHORIZED)
        if userId != id_author:
            return Response({"details":"Can't delete someone elses inbox"}, status=status.HTTP_401_UNAUTHORIZED)
        inbox = Inbox.objects.filter(author=author)
        inbox.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


@api_view(['GET'])
def get_remote_authors(request):
    """
    Get all remote authors from all remote servers
    """
    remote_nodes = Node.objects.filter(is_active=True)
    allRemoteAuthors = []
    print(remote_nodes)
    for node in remote_nodes:
        response = get_request_remote(host_url=node.host_url, path="authors/")
        print(response)
        if response is not None:
            print("Response for get remote authors")
            if response.status_code == 200:
                payload = response.json()
                authors = payload.get("items")
                print(payload)
                # discard author whose host field is not a valid url
                # discard author who is a local author, that is, its host field is the same as the current server's host
                request_domain = request.build_absolute_uri('/')[:-1]
                authors = [author for author in authors if validators.url(author.get("host")) and not author.get("host").startswith(request_domain)]
                allRemoteAuthors += authors

    data = {
        "type": "authors",
        "items": allRemoteAuthors
    }

    return Response(data, status=status.HTTP_200_OK)


@api_view(['GET'])
def check_remote_follow_requests_approved(request, id_author):
    """
    Check if the remote follow request is approved
    """
    # check if any of the remote follow requests sent by id_author are approved
    # if it is then create a follower object and delete the follow request object

    print("Checking remote follow requests")
    # get all follow requests, with receiver being a remote author and sender being id_author
    follow_requests = FollowRequest.objects.filter(to_user__is_remote=True, from_user__id=id_author)
    print("Remote Follow requests: ", follow_requests)

    # loop through all the remote follow requests and check if they are approved
    for follow_request in follow_requests:
        print(follow_request.from_user.id, follow_request.to_user.id)
        sender_id = follow_request.from_user.id # the person who sent the follow request
        receiver_id = follow_request.to_user.id # the person who received the follow request

        response = get_request_remote(host_url=follow_request.to_user.host, path=f"authors/{follow_request.to_user.id}/followers/{quote(follow_request.from_user.url)}")

        if response is not None:
            if response.status_code == 200:
                print("Follow request was approved")
                # follow request was approved, local user is now a follower of the remote user
                # create a follower object in our local db
                follower = Follower.objects.create(follower_id=sender_id, followed_user_id=receiver_id)
                # delete the local follow request
                follow_request.delete()            

    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def check_remote_follower_still_exists(request, id_author):
    """
    Check if the remote followers of id_author still exists
    """
    # check if the follower still exists
    # if it doesn't then delete the follower object

    print("Checking remote followers")
    # get all remote followers if id_author
    # all remote followers that is on our db
    followers = Follower.objects.filter(follower__is_remote=True, followed_user__id=id_author)
    print("Remote Followers: ", followers)

    # loop through all the followers and check if they still exist
    for follower in followers:
        response = get_request_remote(host_url=follower.follower.host, path=f"authors/{follower.followed_user.id}/followers/{quote(follower.follower.url)}")

        if response is not None:
            if response.status_code == 404:
                # no longer a follower, delete follower object
                follower.delete()

    return Response(status=status.HTTP_200_OK)