from typing import Iterable
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomAuthorManager
import uuid
import os

class Author(AbstractBaseUser, PermissionsMixin):
    type = models.CharField(max_length=30, default="author")
    # leave id as uuid to minimize the number of changes to be done to views
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.URLField(max_length=500, editable=False)
    url = models.URLField(max_length=500, editable=False)
    display_name = models.CharField(max_length=100)
    github = models.URLField(max_length=100)
    profile_image = models.URLField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False, editable=False)
    is_active = models.BooleanField(default=True)

    is_remote = models.BooleanField(default=False)

    email = models.EmailField(unique=True)
    objects = CustomAuthorManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['display_name']

    def __str__(self):
        return self.display_name

    # Reference: https://www.sankalpjonna.com/learn-django/how-to-override-the-save-method-in-your-django-models
    # Reference: https://stackoverflow.com/questions/907695/in-a-django-model-custom-save-method-how-should-you-identify-a-new-object
    # Accessed on: 2024-03-05
    def save(self, *args, **kwargs):
        isActive = os.getenv('IS_ACTIVE')

        if self._state.adding and not self.is_staff:

            if self.password:
                self.set_password(self.password)

            # set is_active to isActive only when user is created, and not when updated
            if isActive and isActive.lower() == 'false':
                self.is_active = False
            else:
                self.is_active = True

        super().save(*args, **kwargs)
    
    

class Follower(models.Model):
    follower = models.ForeignKey(Author, related_name='following', on_delete=models.CASCADE)
    followed_user = models.ForeignKey(Author, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # to ensure that a user can only follow another user once
        unique_together = ('follower', 'followed_user')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.follower.display_name} follows {self.followed_user.display_name}'


# took inspiration from: https://medium.com/analytics-vidhya/add-friends-with-689a2fa4e41d
# and https://stackoverflow.com/questions/58794639/how-to-make-follower-following-system-with-django-model 
class FollowRequest(models.Model):
    from_user = models.ForeignKey(Author, related_name='sent_follow_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(Author, related_name='received_follow_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.from_user.display_name} sent a follow request to {self.to_user.display_name}'
    
# #posts
class Post(models.Model):
    CONTENT_TYPES = (
        ('text/markdown', 'text/markdown'),
        ('text/plain', 'text/plain'),
        ('application/base64', 'application/base64'),
        ('image/png;base64', 'image/png;base64'),
        ('image/jpeg;base64', 'image/jpeg;base64')
    )
    type = models.CharField(max_length=50, default="post")
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=100)
    source = models.URLField(default="",max_length=200, blank=True)
    origin = models.URLField(default="",max_length=200, blank=True)
    description = models.TextField()
    contentType = models.CharField(max_length=50, choices=CONTENT_TYPES, default="text/markdown")
    content = models.TextField(default="",blank=True, null=True)
    author = models.ForeignKey(Author, related_name='posts_author', on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    comments = models.CharField(max_length=100)
    published = models.DateTimeField(auto_now_add=True)
    visibility = models.CharField(max_length=50, choices=(('PUBLIC','PUBLIC'),('FRIENDS', 'FRIENDS'),('UNLISTED','UNLISTED')))
    # image = models.URLField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='post_images', blank=True, null=True)  
    image_url = models.URLField(max_length=200, blank=True, null=True)  
# #comments
class Comment(models.Model):
    type = models.CharField(max_length=50, default="comment")
    id = models.UUIDField(primary_key=True,unique=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, related_name='comments_author', on_delete=models.CASCADE)
    comment=models.TextField()
    contentType = models.CharField(max_length=50, choices = (('text/markdown', 'text/markdown'), ('text/plain', 'text/plain')), default="text/markdown")
    published = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

# #likes
class Like(models.Model):
    type = models.CharField(max_length=20, default="Like")
    summary = models.CharField(max_length=248)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="likes_author")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="like_post", null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="like_comment", null=True)
    object = models.CharField(max_length=250, null=False, blank=False, default="")
# #inbox
class Inbox(models.Model):
    type = models.CharField(max_length=50, default="inbox")
    author = models.ForeignKey(Author, related_name='author', on_delete=models.CASCADE)
    item = models.JSONField()
    published = models.DateTimeField(auto_now_add=True)


class Node(models.Model):
    team_name = models.CharField(max_length=100)
    api_url = models.URLField(max_length=200)
    base64_authorization = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.team_name}: {self.api_url}'

    def __str__(self):
        return self.name