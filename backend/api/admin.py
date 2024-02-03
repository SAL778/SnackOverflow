from django.contrib import admin

from .models import Author, Follower, FollowRequest

admin.site.register(Author)
admin.site.register(Follower)
admin.site.register(FollowRequest)