from django.urls import path
from . import views

app_name = "api"

urlpatterns = [
    path("authors/", views.get_authors, name="get_authors"),
    path("authors/<uuid:id>", views.get_and_update_author, name="get_and_update_author"),
    path("authors/<uuid:id>/followers", views.get_followers, name="get_followers"),
    path("authors/<uuid:id_author>/followers/<uuid:id_follower>", views.get_update_and_delete_follower, name="get_update_and_delete_follower"),

    # apis for follow requests? needed? Not sure
    path("authors/<uuid:id>/followrequests", views.get_received_follow_requests, name="get_received_follow_requests"),
    path("authors/<uuid:id_author>/followrequests/<uuid:id_sender>", views.get_and_delete_follow_request, name="get_and_delete_a_follow_request"),

    #apis for posts
    path("authors/<uuid:id_author>/posts/<uuid:id_post>", views.get_update_and_delete_post, name="get_update_and_delete_post"),
    path("authors/<uuid:id_author>/posts/", views.get_and_create_post, name="get_and_create_post"),
    path("authors/<uuid:id_author>/posts/<uuid:id_post>/image", views.get_image, name="get_image"),
    #TODO: can we add extra urls?
    path("posts/", views.get_posts, name="get_posts"),

    #apis for comments
    path("authors/<uuid:id_author>/posts/<uuid:id_post>/comments", views.get_and_create_comment, name="get_and_create_comment"),

    #apis for likes
    path("authors/<uuid:id_author>/inbox", views.send_like_to_inbox, name="send_like_to_inbox"),
    path("authors/<uuid:id_author>/posts/<uuid:id_post>/likes", views.get_like, name="get_like"),
    path("authors/<uuid:id_author>/posts/<uuid:id_post>/comments/<uuid:id_comment>/likes", views.get_like, name="get_like"),
    path("authors/<uuid:id_author>/liked", views.get_liked, name="get_liked"),

    #apis for inbox
    path("authors/<uuid:id_author>/inbox", views.get_and_post_inbox, name="get_and_post_inbox"),
]