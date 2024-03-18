from django.urls import path
from . import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
app_name = "api"
schema_view = get_schema_view(
   openapi.Info(
      title="Snack-Overflow-team API",
      default_version='v1',
      description="API description"
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
   # swagger urls
   path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
   path('swagger/schema', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('swagger/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

   path("login/", views.UserLogin.as_view(), name="login"),
   path("register/", views.UserRegister.as_view(), name="register"),
   path("logout/", views.UserLogout.as_view(), name="logout"),
   path("user/", views.UserView.as_view(), name="user"),

   path("authors/", views.get_authors, name="get_authors"),
   path("authors/<uuid:id>", views.get_and_update_author, name="get_and_update_author"),
   path("authors/<uuid:id>/followers", views.get_followers, name="get_followers"),
   path("authors/<uuid:id_author>/followers/<uuid:id_follower>", views.get_update_and_delete_follower, name="get_update_and_delete_follower"),

    # custom apis for followings and friends
   path("authors/<uuid:id_author>/followings", views.get_followings, name="get_followings"),
   path("authors/<uuid:id_author>/friends", views.get_friends, name="get_friends"),

   # custom apis for follow requests? needed? Not sure
   path("authors/<uuid:id>/followrequests", views.get_received_follow_requests, name="get_received_follow_requests"),
   path("authors/<uuid:id_author>/followrequests/<uuid:id_sender>", views.get_create_delete_and_accept_follow_request, name="get_and_delete_a_follow_request"),

   # apis for posts
   path("authors/<uuid:id_author>/posts/", views.get_and_create_post, name="get_and_create_post"),
   path("authors/<uuid:id_author>/posts/<uuid:id_post>/image", views.get_image, name="get_image"),
   path("authors/<uuid:id_author>/posts/<uuid:id_post>", views.get_update_and_delete_specific_post, name="get_update_and_delete_specific_post"),

   # apis for comments
   path("authors/<uuid:id_author>/posts/<uuid:id_post>/comments", views.get_and_create_comment, name="get_and_create_comment"),

   # apis for likes
   path("authors/<uuid:id_author>/posts/<uuid:id_post>/likes", views.get_post_likes, name="get_post_likes"),
   path("authors/<uuid:id_author>/liked", views.get_liked, name="get_liked"),

   # apis for inbox
   path("authors/<uuid:id_author>/inbox", views.get_and_post_inbox, name="get_and_post_inbox"),

   # custom urls
   path("publicPosts/", views.get_all_public_posts, name="get_all_public_posts"),
   path("friendsFollowerPosts/<uuid:id_author>", views.get_all_friends_follows_posts, name="get_all_friends_follows_posts"),


   # urls for remote stuff
   path("remote-authors/", views.get_remote_authors, name="get_remote_authors"),
   # this should be called every x seconds from frontend
   path("checkRemoteFollowRequests/", views.check_remote_follow_requests_approved, name="check_remote_follow_requests_approved"),
   path("checkRemoteFollowers/", views.check_remote_follower_still_exists, name="check_remote_follower_still_exists"),
]