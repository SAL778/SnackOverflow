from django.contrib import admin

from .models import Author, Follower, FollowRequest, Post

admin.site.register(Author)
admin.site.register(Follower)
admin.site.register(FollowRequest)
admin.site.register(Post)