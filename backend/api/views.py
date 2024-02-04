from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from .models import Author, Follower, FollowRequest
from .serializers import AuthorSerializer, FollowRequestSerializer

# Create your views here.
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