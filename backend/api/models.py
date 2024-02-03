from django.db import models
from django.contrib.auth.models import User

import uuid

class Author(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # using default django user model for authentication purposes (includes username, email, password, etc.)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    display_name = models.CharField(max_length=100)
    github = models.URLField(max_length=100)
    profile_image = models.URLField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    is_accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f'{self.from_user.display_name} sent a follow request to {self.to_user.display_name}'