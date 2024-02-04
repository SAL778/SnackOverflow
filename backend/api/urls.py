from django.urls import path
from . import views

app_name = "api"

urlpatterns = [
    path("authors/", views.get_authors, name="get_authors"),
    path("authors/<uuid:id>", views.get_and_update_author, name="get_and_update_author"),
    path("authors/<uuid:id>/followers", views.get_followers, name="get_followers"),
    path("authors/<uuid:id_author>/followers/<uuid:id_follower>", views.get_update_and_delete_follower, name="get_update_and_delete_follower"),
    path("authors/<uuid:id>/followrequests", views.get_received_follow_requests, name="get_received_follow_requests"),
    path("authors/<uuid:id_author>/followrequests/<uuid:id_sender>", views.get_and_delete_follow_request, name="get_and_delete_a_follow_request"),
]