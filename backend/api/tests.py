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
        """
            tests user creation and login via endpoint, as well as getting all available authors endpoint
        """
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
        """
            tests the logout api for a user
        """
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

    def test_multiple_users(self):
        """
            tests hosting multiple users on one server
        """
        # create two users
        user1 = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        user2 = create_author("test1@test1.ca", "test1 user1", "https://google.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)

        # login as user 1 and test the authors endpoint
        self.client.post(reverse("api:login"), user1)
        response = self.client.get(reverse("api:get_authors"))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        users = result["items"]

        # compare the output from the get request to our users
        assert users[0]["displayName"] == user1["display_name"]
        assert users[0]["github"] == user1["github"]

        assert users[1]["displayName"] == user2["display_name"]
        assert users[1]["github"] == user2["github"]

        # each user should have their own unique id in the field
        assert users[0]["id"] != users[1]["id"]

    def test_validate_auth(self):
        """
            test for user validation endpoint
        """
        user = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user)
        self.client.post(reverse("api:login"), user)

        # test authentication and retrieval of user information
        response =self.client.get(reverse("api:user"))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        object = result["user"]
        assert user["display_name"] == object["displayName"]
        assert user["github"] == object["github"]

    # TODO:
    # def test_get_liked(self):
        
class PostCreation(TestCase):
    # dont use set up if unit tests are not isolated from each other, this runs once at the beginning
    # def setUp(self):

    def test_create_post(self):
        """
            tests post creation for a user and the retrieval of posts from the endpoint
        """
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
        assert post.visibility == post_object["visibility"]
        assert post_object["author"]["displayName"] == author.display_name
        assert post_object["author"]["github"] == author.github
        # proper url has been serialized by backend for comments url and id of post
        assert post_object["comments"] != ""
        assert post_object["id"] != ""

    # def test_create_post_api(self):
    #     """
    #         tests post creation from the endpoint
    #     """
    #     user = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
    #     self.client.post(reverse("api:register"), user)
    #     self.client.post(reverse("api:login"), user)

    #     # retrieve author info
    #     author_object = Author.objects.get(display_name="test user")
    #     response = self.client.get(reverse("api:get_authors"))
    #     result = json.loads(response.content)
    #     author = result["items"][0]
        
    #     # create the object
    #     post = {
    #         "type": "post",
    #         "id": "",
    #         "title": "Test post to create",
    #         "source": "",
    #         "origin": "",
    #         "description": "This post is an example",
    #         "contentType": "text/plain",
    #         "content": "this is an post with no comments",
    #         "author": author,
    #         "count": 0,
    #         "comments": "",
    #         "published": "",
    #         "visibility": "PUBLIC"
    #     }
    #     response = self.client.post(reverse("api:get_and_create_post", kwargs={"id_author": author_object.id}), post)
    #     self.assertEqual(response.status_code, 201)

    #     # pull posts from endpoint
    #     response = self.client.get(reverse("api:get_and_create_post", kwargs={"id_author": author_object.id}))
    #     self.assertEqual(response.status_code, 200)
    #     retrieved = json.loads(response.content)
    #     post_object = retrieved["items"][0]
    #     print(post_object["author"])

    #     # test to ensure some aspects remain the same between both post objects
    #     assert post["title"] == post_object["title"]
    #     assert post["content"] == post_object["content"]
    #     assert post["description"] == post_object["description"]
    #     assert post["contentType"] == post_object["contentType"]
    #     assert post["visibility"] == post_object["visibility"]
    #     # proper url has been serialized by backend for comments url
    #     assert post_object["comments"] != ""
    #     assert post_object["id"] != ""
    #     # author has been properly assigned
    #     assert post_object["author"]["displayName"] == author_object.display_name
    #     assert post_object["author"]["github"] == author_object.github
        
    # TODO:
    # def test_create_markdown(self):

    # TODO:
    # def test_create_friendsonly_text_post(self):

    def test_get_all_author_posts_visibility(self):
        """
            tests to see if the user can see their own posts regardless of visibility
        """
        user = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user)
        self.client.post(reverse("api:login"), user)

        # retrieve author info and create posts through model creation, oldest post to most recent
        author = Author.objects.get(display_name="test user")
        post1 = create_post("test public", '', '', "1 description", "text/plain", "test content", author, "0", "", "PUBLIC" )
        post2 = create_post("test friends", '', '', "2 description", "text/plain", "test content", author, "0", "", "FRIENDS" )
        post3 = create_post("test unlisted", '', '', "3 description", "text/plain", "test content", author, "0", "", "UNLISTED" )
        # this test currently fails if done in this order
        # created_posts = [post3, post2, post1]
        #USE THIS UNLESS FIXED TO SHOW RECENT FIRST
        created_posts = [post1, post2, post3]

        # pull posts from endpoint
        response = self.client.get(reverse("api:get_and_create_post", kwargs={"id_author": author.id}))
        self.assertEqual(response.status_code, 200)
        retrieved = json.loads(response.content)
        posts = retrieved["items"]

        for i in range(len(posts)):
            assert created_posts[i].title == posts[i]["title"]
            assert created_posts[i].visibility == posts[i]["visibility"]

    def test_get_other_author_posts_visibility(self):
        """
            test to see if an users can only see public posts on another author's page
        """
        print()

    def test_get_specific_text_post(self):
        """
            test to get post information from the post url (not including image post)
        """
        user = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user)
        self.client.post(reverse("api:login"), user)

        # retrieve author info
        author = Author.objects.get(display_name="test user")
        # create the object internally (not with api)
        post = create_post("test title", '', '', "test description", "text/plain", "test content", author, "0", "", "public" )
        response = self.client.get(reverse("api:get_update_and_delete_specific_post", kwargs={"id_author":author.id, "id_post": post.id}))
        self.assertEqual(response.status_code, 200)
        retrieved = json.loads(response.content)
        print(retrieved)
        print("finish this test")
    # TODO:
    # def test_delete_post(self):
    # TODO:
    # def test_view_post_likes(self):

            
class FeedTests(TestCase):
    def test_all_public_posts(self):
        """
            test that public feed only gets public posts and that they are viewable
        """
        # create users and login as user1
        user1 = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        user2 = create_author("test1@test1.ca", "test1 user1", "https://google.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)
        self.client.post(reverse("api:login"), user1)

        # create public posts as user1, log out
        author1 = Author.objects.get(display_name="test user")
        post1 = create_post("test title", '', '', "test description", "text/plain", "test content", author1, "0", "", "PUBLIC" )
        post11 = create_post("another", '', '', "description", "text/plain", "wow", author1, "0", "", "PUBLIC" )
        post111 = create_post("another", '', '', "description", "text/plain", "wow", author1, "0", "", "UNLISTED" )
        self.client.post(reverse("api:logout"))

        # login as user 2, create public post, and get posts from public endpoint
        self.client.post(reverse("api:login"), user2)   
        author2 = Author.objects.get(display_name="test1 user1")
        post2 = create_post("nice", '', '', "nice", "text/plain", "nice content", author2, "0", "", "PUBLIC" )
        response = self.client.get(reverse("api:get_all_public_posts"))
        self.assertEqual(response.status_code, 200)
        retrieved = json.loads(response.content)
        posts = retrieved["items"]

        created_posts = [post2, post11, post1]
        for i in range(len(posts)):
            assert created_posts[i].title == posts[i]["title"]
            assert created_posts[i].visibility == posts[i]["visibility"]
            assert posts[i]["visibility"] == "PUBLIC"
    # TODO:
    # def test_feed_posts(self):
        # test recent posts here
    # TODO:
    # def test_friends_only_posts(self):
# TODO:
# class FollowingandFollowers(TestCase):
#     def test_get_followers(self):

#     def test_get_following(self):

#     def test_get_friends(self):

# class RequestTests(TestCase):
#     def test_accept_follow_request(self):

#     def test_deny_follow_request(self):

#     def test_making_friends(self):

#     def test_unmaking_friends(self):

#     def test_follow(self):

#     def test_unfollow(self):

# class InboxTests(TestCase):
#     # these two test inbox api
#     def test_notifications_follow_requests(self):

#     def test_notifications_likes(self):
