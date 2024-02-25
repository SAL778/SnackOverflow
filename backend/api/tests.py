from django.test import TestCase
from django.core import serializers
from django.urls import reverse
import json

from .models import Author, Post, Comment, Like, Inbox, FollowRequest, Follower

# Create your tests here.

def create_author(email, name, github, image, password):
    """
    creates a dict with fields from the given information above
    """
    user = {"display_name": name, "github": github, "email":email, "password": password, "profile_image": image}
    return user
    

def create_post(title, source, origin, description, content_type, 
                content, author, count, comments, visibility):
    """
    creates a post based on the fields given from the specified author
    """
    return Post.objects.create(title=title, source=source, origin=origin, description=description, 
                               contentType=content_type, content=content, author=author, count=count, comments=comments,
                               visibility=visibility)

def create_follow_request(follower, followee):
    """ 
    creates a follower request object that has not been
    approved yet by the followee and will show up in their inbox
    to be accepted or denied
    """
    return FollowRequest.objects.create(follower=follower, followed_user=followee)

def create_comment(author, comment, content_type, post):
    print("no comment test yet")

def create_like(summary, author, post, object):
    """
    creates an like object for either a post or a comment
    """
    return Like.objects.create(summary=summary, author=author, post=post, object=object)

def create_inbox(author, item):
    """

    """
    return Inbox.objects.create(author=author, item=item)

def create_follower(follower, followee):
    """
    creates an follower object to add to the followee's list once the 
    request has been approved
    """
    return Follower.objects.create(follower=follower, followed_user=followee)

class UserCreation(TestCase):
    def test_create_a_user(self):
        # create user information for testing and login
        user = create_author("test@test.ca", "test user", "https://github.com", "", "12345")

        # create the user, login, and check if user is in authors list of server
        response = self.client.post(reverse("api:register"), user)
        self.assertEqual(response.status_code, 201)
        response = self.client.post(reverse("api:login"), user)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("api:get_authors"))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        author_object = result["items"][0]
        assert author_object["displayName"] == user["display_name"]
        assert author_object["github"] == user["github"]
        assert author_object["profileImage"] == user["profile_image"]

    def test_user_logout(self):
        # create user information for testing and login
        user = create_author("test@test.ca", "test user", "https://github.com", "", "12345")

        # create the user, login, and check if user is in authors list of server
        response = self.client.post(reverse("api:register"), user)
        self.assertEqual(response.status_code, 201)
        response = self.client.post(reverse("api:login"), user)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("api:get_authors"))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        author_object = result["items"][0]
        assert author_object["displayName"] == user["display_name"]
        assert author_object["github"] == user["github"]
        assert author_object["profileImage"] == user["profile_image"]
        
        # log out the user and confirm cannot access restricted urls
        response = self.client.post(reverse("api:logout"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("api:get_authors"))
        self.assertEqual(response.status_code, 403)

    # def test_multiple_users(self):
    #     print("This test is not complete yet")
        
class PostCreation(TestCase):
    # dont use set up if unit tests are not isolated from each other, this runs once at the beginning
    # def setUp(self):
    #     # creates a user 
    #     user = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
    #     response = self.client.post(reverse("api:register"), user)
    #     response = self.client.post(reverse("api:login"), user)
    #     print("")

    def test_create_post(self):
        # creates a user (if done in a specifc test case, this user is unique to the test case ie.id will not be the same as
        # a user created in another case)
        # if I dont need to do this for tests other than user creation that would be nice (our Author object is a custom User)
        user = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user)
        self.client.post(reverse("api:login"), user)

        # retrieve author info
        author = Author.objects.get(display_name="test user")
        # create the object internally (not with api)
        post = create_post("test title", '', '', "test description", "text/plain", "test content", author, "0", "", "public" )

        # pull posts from endpoint
        response = self.client.get(reverse("api:get_and_create_post", kwargs={"id_author": author.id}))
        self.assertEqual(response.status_code, 200)
        retrieved = json.loads(response.content)
        post_object = retrieved["items"][0]

        # test to ensure some aspects remain the same between both post objects
        assert post.title == post_object["title"]
        assert post.content == post_object["content"]
        assert post.description == post_object["description"]
        assert post.contentType == post_object["contentType"]
        # proper url has been serialized by backend for comments url
        assert post_object["comments"] != ""
        assert post_object["id"] != ""

    def test_create_post_api(self):
        user = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user)
        self.client.post(reverse("api:login"), user)

        # retrieve author info
        author = Author.objects.get(display_name="test user")
        response = self.client.get(reverse("api:get_authors"))
        result = json.loads(response.content)
        author_object = result["items"][0]

        # create the object
        post = {
            "type": "post",
            "id": "",
            "title": "Test post to create",
            "source": "",
            "origin": "",
            "description": "This post is an example",
            "contentType": "text/plain",
            "content": "this is an post with no comments",
            "author": author,
            "count": 0,
            "comments": "",
            "published": "2024-02-24T00:03:53.094474Z",
            "visibility": "PUBLIC"
        }
        
        response = self.client.post(reverse("api:get_and_create_post", kwargs={"id_author": author.id}), post)
        self.assertEqual(response.status_code, 201)

        # pull posts from endpoint
        response = self.client.get(reverse("api:get_and_create_post", kwargs={"id_author": author.id}))
        self.assertEqual(response.status_code, 200)
        retrieved = json.loads(response.content)
        post_object = retrieved["items"][0]

        # test to ensure some aspects remain the same between both post objects
        assert post["title"] == post_object["title"]
        assert post["content"] == post_object["content"]
        assert post["description"] == post_object["description"]
        assert post["contentType"] == post_object["contentType"]
        # proper url has been serialized by backend for comments url
        assert post_object["comments"] != ""
        assert post_object["id"] != ""