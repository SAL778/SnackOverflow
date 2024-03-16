from django.test import TestCase, Client
from django.core import serializers
from django.urls import reverse
import json

from .models import Author, Post, Comment, Like, Inbox, FollowRequest, Follower

# Create your tests here.

def set_active(author):
    setattr(author, "is_active", True)
    author.save()

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
    return FollowRequest.objects.create(from_user=follower, to_user=followee)

def create_comment(author, comment, post, content_type="type/markdown"):
    """ 
    creates a comment object given a post
    """
    return Comment.objects.create(author=author, comment=comment, contentType=content_type, post=post)

def create_like(summary, author, post, object):
    """
    creates an like object for either a post or a comment
    """
    return Like.objects.create(summary=summary, author=author, post=post, object=object)

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
        # allow the user to be active via admin command
        author = Author.objects.get(display_name="test user")
        set_active(author)
        # LOGIN
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
        # allow the user to be active via admin command
        author = Author.objects.get(display_name="test user")
        set_active(author)
        # LOGIN
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
        user2 = create_author("test1@test1.ca", "test1 user1", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)
        # allow the user to be active via admin command
        author = Author.objects.get(display_name="test user")
        set_active(author)
        author = Author.objects.get(display_name="test1 user1")
        set_active(author)

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
        author = Author.objects.get(display_name="test user")
        set_active(author)
        self.client.post(reverse("api:login"), user)

        # test authentication and retrieval of user information
        response =self.client.get(reverse("api:user"))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        assert user["display_name"] == result["displayName"]
        assert user["github"] == result["github"]

    # def test_github_field(self):

    # TODO: part 2 since no likes
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
        author = Author.objects.get(display_name="test user")
        set_active(author)
        self.client.post(reverse("api:login"), user)

        # create the object 
        post = create_post("test title", '', '', "test description", "text/plain", "test content", author, "0", "", "PUBLIC" )

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

    def test_create_post_api(self):
        """
            tests post creation from the endpoint
        """
        user = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user)
        author_object = Author.objects.get(display_name="test user")
        set_active(author_object)
        self.client.post(reverse("api:login"), user)

        # retrieve author info
        response = self.client.get(reverse("api:get_authors"))
        result = json.loads(response.content)
        author = result["items"][0]
        
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
            "published": "",
            "visibility": "PUBLIC"
        }
        response = self.client.post(reverse("api:get_and_create_post", kwargs={"id_author": author_object.id}), json.dumps(post), content_type="application/vnd.api+json")
        print(response.content)
        self.assertEqual(response.status_code, 201)

        # pull posts from endpoint
        response = self.client.get(reverse("api:get_and_create_post", kwargs={"id_author": author_object.id}))
        self.assertEqual(response.status_code, 200)
        retrieved = json.loads(response.content)
        post_object = retrieved["items"][0]

        # test to ensure some aspects remain the same between both post objects
        assert post["title"] == post_object["title"]
        assert post["content"] == post_object["content"]
        assert post["description"] == post_object["description"]
        assert post["contentType"] == post_object["contentType"]
        assert post["visibility"] == post_object["visibility"]
        # proper url has been serialized by backend for comments url
        assert post_object["comments"] != ""
        assert post_object["id"] != ""
        # author has been properly assigned
        assert post_object["author"]["displayName"] == author_object.display_name
        assert post_object["author"]["github"] == author_object.github
        
    def test_create_markdown(self):
        """
            tests markdown post creation for a user and the retrieval of posts from the endpoint
        """
        user = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user)
        author = Author.objects.get(display_name="test user")
        set_active(author)
        self.client.post(reverse("api:login"), user)

        # create the object internally (not with api)
        post = create_post("test title", '', '', "# this is a header", "text/markdown", "test content", author, "0", "", "PUBLIC" )

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

    def test_create_friendsonly_text_post(self):
        """
            tests friends only post creation for a user and the retrieval of posts from the endpoint
        """
        user = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user)
        author = Author.objects.get(display_name="test user")
        set_active(author)
        self.client.post(reverse("api:login"), user)
        # create the object internally (not with api)
        post = create_post("test title", '', '', "friends only", "text/plain", "test content", author, "0", "", "FRIENDS" )

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

    def test_get_specific_text_post(self):
        """
            test to get post information from the post url (not including image post)
        """
        user = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user)
        author = Author.objects.get(display_name="test user")
        set_active(author)
        self.client.post(reverse("api:login"), user)

        # retrieve author info
        # create the object internally (not with api)
        post = create_post("test title", '', '', "test description", "text/plain", "test content", author, "0", "", "public" )
        response = self.client.get(reverse("api:get_update_and_delete_specific_post", kwargs={"id_author":author.id, "id_post": post.id}))
        self.assertEqual(response.status_code, 200)
        retrieved = json.loads(response.content)

        assert post.title == retrieved["title"]
        assert post.content == retrieved["content"]
        assert post.description == retrieved["description"]
        assert post.contentType == retrieved["contentType"]
        assert post.visibility == retrieved["visibility"]
        assert retrieved["author"]["displayName"] == author.display_name
        assert retrieved["author"]["github"] == author.github
        assert retrieved["comments"] != post.comments
        assert retrieved["id"] != post.id
        
    def test_delete_post(self):
        """
            test to get post information from the post url (not including image post)
        """
        user = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user)
        author = Author.objects.get(display_name="test user")
        set_active(author)
        self.client.post(reverse("api:login"), user)

        # create the object and attempt to delete
        post = create_post("test title", '', '', "test description", "text/plain", "test content", author, "0", "", "public" )
        response = self.client.delete(reverse("api:get_update_and_delete_specific_post", kwargs={"id_author":author.id, "id_post": post.id}))
        self.assertEqual(response.status_code, 204)

        # should not exist
        response = self.client.get(reverse("api:get_update_and_delete_specific_post", kwargs={"id_author":author.id, "id_post": post.id}))
        self.assertEqual(response.status_code, 404)
    # TODO: part 2 as we dont have likes atm
    # def test_view_post_likes(self):

            
class FeedTests(TestCase):
    def test_all_public_posts(self):
        """
            test that public feed only gets public posts and that they are viewable
        """
        # create users and login as user1
        user1 = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        user2 = create_author("test1@test1.ca", "test1 user1", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)
        author1 = Author.objects.get(display_name="test user")
        set_active(author1)
        author2 = Author.objects.get(display_name="test1 user1")
        set_active(author2)
        self.client.post(reverse("api:login"), user1)

        # create public posts as user1, log out
        post1 = create_post("test title", '', '', "test description", "text/plain", "test content", author1, "0", "", "PUBLIC" )
        post11 = create_post("another", '', '', "description", "text/plain", "wow", author1, "0", "", "PUBLIC" )
        post111 = create_post("another", '', '', "description", "text/plain", "wow", author1, "0", "", "UNLISTED" )
        self.client.post(reverse("api:logout"))

        # login as user 2, create public post, and get posts from public endpoint
        self.client.post(reverse("api:login"), user2)   
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

    def test_get_all_author_posts_visibility(self):
        """
            tests to see if the user can see their own posts regardless of visibility
        """
        user = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user)
        author = Author.objects.get(display_name="test user")
        set_active(author)
        self.client.post(reverse("api:login"), user)

        # retrieve author info and create posts through model creation, oldest post to most recent
        post1 = create_post("test public", '', '', "1 description", "text/plain", "test content", author, "0", "", "PUBLIC" )
        post2 = create_post("test friends", '', '', "2 description", "text/plain", "test content", author, "0", "", "FRIENDS" )
        post3 = create_post("test unlisted", '', '', "3 description", "text/plain", "test content", author, "0", "", "UNLISTED" )
        # this test currently fails if done in this order
        # created_posts = [post3, post2, post1]
        #USE THIS UNLESS FIXED TO SHOW RECENT FIRST (FRONT END FIXES THIS BUT NOT BACK)
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
        # create users and login as user1
        user1 = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        user2 = create_author("test1@test1.ca", "test1 user1", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)
        author1 = Author.objects.get(display_name="test user")
        set_active(author1)
        author2 = Author.objects.get(display_name="test1 user1")
        set_active(author2)
        self.client.post(reverse("api:login"), user1)

        # create a few posts
        post1 = create_post("test title", '', '', "friends only", "text/plain", "test content", author2, "0", "", "FRIENDS" )
        post2 = create_post("test title", '', '', "public", "text/plain", "test content", author2, "0", "", "PUBLIC" )

        response = self.client.get(reverse("api:get_and_create_post", kwargs={"id_author": author2.id}))
        self.assertEqual(response.status_code, 200)
        posts = json.loads(response.content)
        retrieved = posts["items"][0]

        # only one post returned, check contents to public post
        assert len(posts["items"]) == 1
        assert post2.title == retrieved["title"]
        assert post2.content == retrieved["content"]
        assert post2.description == retrieved["description"]
        assert post2.contentType == retrieved["contentType"]
        assert post2.visibility == retrieved["visibility"]
        assert retrieved["author"]["displayName"] == author2.display_name
        assert retrieved["author"]["github"] == author2.github
        assert retrieved["comments"] != post2.comments
        assert retrieved["id"] != post2.id
    
    def test_feed_posts(self):
        """
            test getting personalized feed in order
        """
        user1 = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        user2 = create_author("test1@test1.ca", "test1 user1", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)
        author1 = Author.objects.get(display_name="test user")
        set_active(author1)
        author2 = Author.objects.get(display_name="test1 user1")
        set_active(author2)
        self.client.post(reverse("api:login"), user1)

        follwer = create_follower(author1, author2)
        post1 = create_post("test title", '', '', "public", "text/plain", "test content", author2, "0", "", "PUBLIC" )
        post1 = create_post("test title", '', '', "public", "text/plain", "test content", author2, "0", "", "PUBLIC" )

        # this needs to be finished
        response = self.client.get(reverse("api:get_all_friends_follows_posts"))
        self.assertEqual(response.status_code, 200)
        posts = json.loads(response.content)


    def test_friends_only_posts(self):
        """
            test to see that you recieve friends only posts
        """
        # create users and login as user1
        user1 = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        user2 = create_author("test1@test1.ca", "test1 user1", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)

        author1_obj = Author.objects.get(display_name="test user")
        author2_obj = Author.objects.get(display_name="test1 user1")
        set_active(author1_obj)
        set_active(author2_obj)

        # make each user a follower of each other
        follower_user1 = create_follower(author1_obj, author2_obj)
        follower_user2 = create_follower(author2_obj, author1_obj)

        # make an post object for user 2
        post1 = create_post("test public", '', '', "1 description", "text/plain", "test content", author2_obj, "0", "", "FRIENDS" )

        # get the post from the endpoint
        self.client.post(reverse("api:login"), user1)
        response = self.client.get(reverse("api:get_all_friends_follows_posts"))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        retrieved = result["items"][0]

        assert post1.title == retrieved["title"]
        assert post1.content == retrieved["content"]
        assert post1.description == retrieved["description"]
        assert post1.contentType == retrieved["contentType"]
        assert post1.visibility == retrieved["visibility"]
        assert retrieved["author"]["displayName"] == author2_obj.display_name
        assert retrieved["author"]["github"] == author2_obj.github
        assert retrieved["comments"] != post1.comments
        assert retrieved["id"] != post1.id

            
class FollowingandFollowers(TestCase):
    def test_get_followers(self):
        """
            test getting followers
        """
        user1 = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        user2 = create_author("test1@test1.ca", "test1 user1", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)
        author1_obj = Author.objects.get(display_name="test user")
        author2_obj = Author.objects.get(display_name="test1 user1")
        set_active(author1_obj)
        set_active(author2_obj)
        self.client.post(reverse("api:login"), user2)

        # make author 1 an follower of author 2 via call methods
        follower = create_follower(author1_obj, author2_obj)

        # check if author 1 is follower
        response = self.client.get(reverse("api:get_followers", kwargs={"id":author2_obj.id}))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        follower = result["items"][0]

        assert author1_obj.display_name == follower["displayName"]
        assert author1_obj.github == follower["github"]
        assert author1_obj.profile_image == follower["profileImage"]

    def test_get_following(self):
        """
            test getting following
        """
        user1 = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        user2 = create_author("test1@test1.ca", "test1 user1", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)
        author1_obj = Author.objects.get(display_name="test user")
        author2_obj = Author.objects.get(display_name="test1 user1")
        set_active(author1_obj)
        set_active(author2_obj)
        self.client.post(reverse("api:login"), user1)

        # make and now check the following list of author 1
        follower = create_follower(author1_obj, author2_obj)
        response = self.client.get(reverse("api:get_followings", kwargs={"id_author":author1_obj.id}))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        followee = result["items"][0]

        # check to see that author two is the followee
        assert author2_obj.display_name == followee["displayName"]
        assert author2_obj.github == followee["github"]
        assert author2_obj.profile_image == followee["profileImage"]
        
    def test_get_friends(self):
        """
            test getting friends
        """
        user1 = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        user2 = create_author("test1@test1.ca", "test1 user1", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)
        author1_obj = Author.objects.get(display_name="test user")
        author2_obj = Author.objects.get(display_name="test1 user1")
        set_active(author1_obj)
        set_active(author2_obj)
        self.client.post(reverse("api:login"), user1)

        # make each user a follower of each other
        follower_user1 = create_follower(author1_obj, author2_obj)
        follower_user2 = create_follower(author2_obj, author1_obj)

        # check to see if author 1 has author 2 on friends list
        response = self.client.get(reverse("api:get_friends", kwargs={"id_author":author1_obj.id}))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        friend = result["items"][0]

        assert author2_obj.display_name == friend["displayName"]
        assert author2_obj.github == friend["github"]
        assert author2_obj.profile_image == friend["profileImage"]

        # check to see if author 2 has author 1 on friends list
        response = self.client.get(reverse("api:get_friends", kwargs={"id_author":author2_obj.id}))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        friend = result["items"][0]

        assert author1_obj.display_name == friend["displayName"]
        assert author1_obj.github == friend["github"]
        assert author1_obj.profile_image == friend["profileImage"]


class RequestTests(TestCase):
    def test_accept_follow_request(self):
        """
            accept a follow request from a user
        """
        user1 = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        user2 = create_author("test1@test1.ca", "test1 user1", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)
        author1_obj = Author.objects.get(display_name="test user")
        author2_obj = Author.objects.get(display_name="test1 user1")
        set_active(author1_obj)
        set_active(author2_obj)
        self.client.post(reverse("api:login"), user1)

        # author 1 sends a request to author two
        request = create_follow_request(author1_obj, author2_obj)

        self.client.post(reverse("api:logout"), user1)
        self.client.post(reverse("api:login"), user2)

        # accept the request as author 2
        response = self.client.put(reverse("api:get_and_delete_a_follow_request", kwargs={"id_author":author2_obj.id, "id_sender": author1_obj.id}))
        self.assertEqual(response.status_code, 201)

        # check if author 1 is follower
        response = self.client.get(reverse("api:get_followers", kwargs={"id":author2_obj.id}))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        follower = result["items"][0]

        assert author1_obj.display_name == follower["displayName"]
        assert author1_obj.github == follower["github"]
        assert author1_obj.profile_image == follower["profileImage"]

        # individual follower object URL exists
        response = self.client.get(reverse("api:get_update_and_delete_follower", 
                                     kwargs={"id_author":author2_obj.id, "id_follower": author1_obj.id}))
        self.assertEqual(response.status_code, 200)

    def test_deny_follow_request(self):
        """
            deny a follow request from a user
        """
        user1 = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        user2 = create_author("test1@test1.ca", "test1 user1", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)
        author1_obj = Author.objects.get(display_name="test user")
        author2_obj = Author.objects.get(display_name="test1 user1")
        set_active(author1_obj)
        set_active(author2_obj)
        self.client.post(reverse("api:login"), user1)

        # author 1 sends a request to author two
        request = create_follow_request(author1_obj, author2_obj)

        self.client.post(reverse("api:logout"), user1)
        self.client.post(reverse("api:login"), user2)

        # accept the request as author 2
        response = self.client.delete(reverse("api:get_and_delete_a_follow_request", kwargs={"id_author":author2_obj.id, "id_sender": author1_obj.id}))
        self.assertEqual(response.status_code, 204)

        # check if author 1 is follower
        response = self.client.get(reverse("api:get_followers", kwargs={"id":author2_obj.id}))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        
        assert len(result["items"]) == 0

        # check if follow request still exists
        response = self.client.get(reverse("api:get_and_delete_a_follow_request", kwargs={"id_author":author2_obj.id, "id_sender": author1_obj.id}))
        self.assertEqual(response.status_code, 404)

    def test_making_friends(self):
        """
            make two users friends of each other
        """
        user1 = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        user2 = create_author("test1@test1.ca", "test1 user1", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)
        author1_obj = Author.objects.get(display_name="test user")
        author2_obj = Author.objects.get(display_name="test1 user1")
        set_active(author1_obj)
        set_active(author2_obj)

        # make follow requests for each user to each other
        request1 = create_follow_request(author1_obj, author2_obj)
        request2 = create_follow_request(author2_obj, author1_obj)

        # have both users accept the requests
        self.client.post(reverse("api:login"), user2)
        response = self.client.put(reverse("api:get_and_delete_a_follow_request", 
                                     kwargs={"id_author":author2_obj.id, "id_sender": author1_obj.id}))
        self.assertEqual(response.status_code, 201)

        self.client.post(reverse("api:logout"))
        self.client.post(reverse("api:login"), user1)
        response = self.client.put(reverse("api:get_and_delete_a_follow_request", 
                                     kwargs={"id_author":author1_obj.id, "id_sender": author2_obj.id}))
        self.assertEqual(response.status_code, 201)
        self.client.post(reverse("api:logout"))

        # login as author 2 and view the friends list
        self.client.post(reverse("api:login"), user2)
        response = self.client.get(reverse("api:get_friends", kwargs={"id_author":author2_obj.id}))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        friend = result["items"][0]

        # author 1 should be on the list
        assert author1_obj.display_name == friend["displayName"]
        assert author1_obj.github == friend["github"]
        assert author1_obj.profile_image == friend["profileImage"]

        # check for author 1
        self.client.post(reverse("api:logout"))
        self.client.post(reverse("api:login"), user1)
        response = self.client.get(reverse("api:get_friends", kwargs={"id_author":author1_obj.id}))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        friend = result["items"][0]

        # author 2 should be on the list
        assert author2_obj.display_name == friend["displayName"]
        assert author2_obj.github == friend["github"]
        assert author2_obj.profile_image == friend["profileImage"]


    def test_unmaking_friends(self):
        """
            remove a friend from your friends list
        """
        # create users
        user1 = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        user2 = create_author("test1@test1.ca", "test1 user1", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)

        author1_obj = Author.objects.get(display_name="test user")
        author2_obj = Author.objects.get(display_name="test1 user1")
        set_active(author1_obj)
        set_active(author2_obj)

        # make each user a follower of each other (friends)
        follower_user1 = create_follower(author1_obj, author2_obj)
        follower_user2 = create_follower(author2_obj, author1_obj)

        # make author 1 unfollow author 2
        self.client.post(reverse("api:login"), user2)
        response = self.client.delete(reverse("api:get_update_and_delete_follower", 
                                     kwargs={"id_author":author2_obj.id, "id_follower": author1_obj.id}))
        self.assertEqual(response.status_code, 204)

        # check friends list of author 2
        response = self.client.get(reverse("api:get_friends", kwargs={"id_author":author2_obj.id}))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        assert len(result["items"]) == 0

        # check friends list of author 1
        response = self.client.get(reverse("api:get_friends", kwargs={"id_author":author1_obj.id}))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        assert len(result["items"]) == 0

        # check followers of author 1
        self.client.post(reverse("api:login"), user2)
        response = self.client.get(reverse("api:get_followers", kwargs={"id":author1_obj.id}))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        follower = result["items"][0]

        assert author2_obj.display_name == follower["displayName"]
        assert author2_obj.github == follower["github"]
        assert author2_obj.profile_image == follower["profileImage"]

    def test_follow(self):
        """
            create an follow request for a specific user
        """
        user1 = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        user2 = create_author("test1@test1.ca", "test1 user1", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)
        author1_obj = Author.objects.get(display_name="test user")
        author2_obj = Author.objects.get(display_name="test1 user1")
        set_active(author1_obj)
        set_active(author2_obj)
        self.client.post(reverse("api:login"), user1)

        # author 1 sends a request to author two
        response = self.client.get(reverse("api:get_authors"))
        result = json.loads(response.content)
        users = result["items"]
        author1 = users[0]
        author2 = users[1]

        request = {
            "type" : "Follow",
            "summary": "",
            "actor": author1,
            "object": author2
        }

        # send the request to the second user
        response = self.client.post(reverse("api:get_and_delete_a_follow_request", 
                                            kwargs={"id_author":author2_obj.id, "id_sender": author1_obj.id}), request)
        self.assertEqual(response.status_code, 201)

        # checks to see if individual request exists
        response = self.client.get(reverse("api:get_and_delete_a_follow_request", kwargs={"id_author":author2_obj.id, "id_sender": author1_obj.id}))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)

        assert result["summary"] != ""
        assert request["type"] == result["type"]
        assert request["actor"] == result["actor"]
        assert request["object"] == result["object"]

    def test_get_requests(self):
        """
            get follow requests for a user
        """
        user1 = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        user2 = create_author("test1@test1.ca", "test1 user1", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)
        author1_obj = Author.objects.get(display_name="test user")
        author2_obj = Author.objects.get(display_name="test1 user1")
        set_active(author1_obj)
        set_active(author2_obj)
        self.client.post(reverse("api:login"), user1)

        # author 1 sends a request to author two
        request = create_follow_request(author1_obj, author2_obj)

        self.client.post(reverse("api:logout"), user1)
        self.client.post(reverse("api:login"), user2)

        # check the request at the followee's side
        response = self.client.get(reverse("api:get_received_follow_requests", kwargs={"id":author2_obj.id}))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        request_return = result["items"][0]

        # assert that the information is correct
        assert request_return["summary"] != ""
        assert "Follow" == request_return["type"]
        assert author1_obj.display_name == request_return["actor"]["displayName"]
        assert author2_obj.display_name == request_return["object"]["displayName"]

    def test_unfollow(self):
        """
            test unfollowing an user
        """

        user1 = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        user2 = create_author("test1@test1.ca", "test1 user1", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)
        author1_obj = Author.objects.get(display_name="test user")
        author2_obj = Author.objects.get(display_name="test1 user1")
        set_active(author1_obj)
        set_active(author2_obj)
        self.client.post(reverse("api:login"), user2)

        # make author 1 the follower of author 2
        follower = create_follower(author1_obj, author2_obj)

        # remove author 1 as a follower
        response = self.client.delete(reverse("api:get_update_and_delete_follower", 
                                           kwargs={"id_author":author2_obj.id, "id_follower": author1_obj.id}))
        self.assertEqual(response.status_code, 204)

        # check to see if still in followers
        response = self.client.get(reverse("api:get_followers", kwargs={"id":author2_obj.id}))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        
        assert len(result["items"]) == 0


class InboxTests(TestCase):
    def test_notifications_follow_requests(self):
        """
            test getting follow requests in the inbox
        """
        user1 = create_author("test@test.ca", "test user", "https://github.com", "", "12345")
        user2 = create_author("test1@test1.ca", "test1 user1", "https://github.com", "", "12345")
        self.client.post(reverse("api:register"), user1)
        self.client.post(reverse("api:register"), user2)
        author1_obj = Author.objects.get(display_name="test user")
        author2_obj = Author.objects.get(display_name="test1 user1")
        set_active(author1_obj)
        set_active(author2_obj)
        self.client.post(reverse("api:login"), user2)

        # get author information
        response = self.client.get(reverse("api:get_authors"))
        result = json.loads(response.content)
        users = result["items"]
        author1 = users[0]
        author2= users[1]

        request = {
            "type": "follow",
            "summary": "someone wants to follow you",
            "actor": author1,
            "object": author2
        }

        inbox = {
            "type": "inbox",
            "author": author2["id"],
            "published": "",
            "items": [request,]
        }

        # send the follow request to the inbox
        response = self.client.post(reverse("api:get_and_post_inbox", kwargs={"id_author":author2_obj.id}), json.dumps(inbox), content_type="application/json")
        self.assertEqual(response.status_code, 201)

        response = self.client.get(reverse("api:get_and_post_inbox", kwargs={"id_author":author2_obj.id}))
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        request_obj = result["items"][0]

        assert request["actor"]["displayName"] == request_obj["actor"]["displayName"]
        assert request["object"]["displayName"] == request_obj["object"]["displayName"]


    # TODO: no likes for part 1
    # def test_notifications_likes(self):
