from django.urls import include, path
from rest_framework import routers

from social_media.views import (
    PostViewSet,
    CommentView,
    CommentToggleLikeView,
    ProfileViewSet,
)

app_name = "social_media"
router = routers.DefaultRouter()
router.register("posts", PostViewSet, basename="posts")
router.register("profiles", ProfileViewSet, basename="profiles")


urlpatterns = [
    path("", include(router.urls)),
    path(
        "posts/<str:id>/comments/<str:cid>/",
        CommentView.as_view(),
        name="comments",
    ),
    path(
        "posts/<str:id>/comments/<str:cid>/toggle-like/",
        CommentToggleLikeView.as_view(),
        name="comments",
    ),
]
