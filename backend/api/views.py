from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Author, Follower, FollowRequest
from .serializers import AuthorSerializer

# Create your views here.
@api_view(['GET'])
def get_authors(request):
    """
    Get all profiles on the server (paginated)
    """
    questions = Author.objects.all()
    serializer = AuthorSerializer(questions, context={'request': request}, many=True)
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
    return Response("Single author")


@api_view(['GET'])
def get_followers(request, id):
    """
    Get all followers of a single profile
    """
    return Response("All followers of User x")


@api_view(['GET', 'PUT', 'DELETE'])
def get_update_and_delete_follower(request, id_author, id_follower):
    """
    Get, update, or delete a single follower
    """
    return Response("Single follower")

