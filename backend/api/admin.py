from django.contrib import admin

from .models import Author, Follower, FollowRequest, Post, Comment, Like, Inbox

admin.site.register(Author)
admin.site.register(Follower)
admin.site.register(FollowRequest)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Inbox)