from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomAuthorManager
import uuid

class Author(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    display_name = models.CharField(max_length=100)
    github = models.URLField(max_length=100)
    profile_image = models.URLField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomAuthorManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['display_name']

    def __str__(self):
        return self.display_name


class Follower(models.Model):
    follower = models.ForeignKey(Author, related_name='following', on_delete=models.CASCADE)
    followed_user = models.ForeignKey(Author, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # to ensure that a user can only follow another user once
        unique_together = ('follower', 'followed_user')

    def __str__(self):
        return f'{self.follower.display_name} follows {self.followed_user.display_name}'


class FollowRequest(models.Model):
    from_user = models.ForeignKey(Author, related_name='sent_follow_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(Author, related_name='received_follow_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f'{self.from_user.display_name} sent a follow request to {self.to_user.display_name}'
    
# #posts
# class Post(models.Model):
#     CONTENT_TYPES = (
#         ('text/markdown', 'text/markdown'),
#         ('text/plain', 'text/plain'),
#         ('application/base64', 'application/base64'),
#         ('image/png;base64', 'image/png;base64'),
#         ('image/jpeg;base64', 'image/jpeg;base64')
#     )
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
#     title = models.CharField(max_length=100)
#     source = models.URLField(max_length=200, blank=True)
#     origin = models.URLField(max_length=200, blank=True)
#     description = models.TextField()
#     contentType = models.CharField(max_length=50, choices=CONTENT_TYPES, default="text/markdown")
#     content = models.TextField()
#     author = models.ForeignKey(Author, related_name='posts_author', on_delete=models.CASCADE)
#     count = models.IntegerField(default=0)
#     comments = models.CharField(max_length=100, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     visibility = models.CharField(choices=['PUBLIC','FRIENDS','UNLISTED'])
#     image = models.URLField(max_length=200, blank=True, null=True)
#     #not sure if we need this
#     commentsSrc = models.JSONField(null=True, blank=True)
#
# #comments
# class Comment(models.Model):
#     id = models.UUIDField(primary_key=True,unique=True, default=uuid.uuid4, editable=False)
#     author = models.ForeignKey(User, related_name='author', on_delete=models.CASCADE)
#     comment=models.TextField()
#     contentType = models.CharField(max_length=50, default="text/markdown")
#     created_at = models.DateTimeField(auto_now_add=True)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#
# #likes
# class Like(models.Model):
#     author = models.ForeignKey(User, related_name='author', on_delete=models.CASCADE)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="like_post", null=True)
#     comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="like_comment", null=True)
#
# #inbox
# class Inbox(models.Model):
#     author = models.ForeignKey(Author, related_name='author', on_delete=models.CASCADE)
#     items = models.JSONField()
#     created_at = models.DateTimeField(auto_now_add=True)
