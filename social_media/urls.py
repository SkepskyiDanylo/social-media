from django.urls import include, path
from rest_framework import routers

from social_media.views import PostViewSet, CommentDestroyView

app_name = "social_media "
router = routers.DefaultRouter()
router.register("posts", PostViewSet, basename="posts")


urlpatterns = [
    path("", include(router.urls)),
    path(
        "posts/<str:id>/comments/<str:cid>/",
        CommentDestroyView.as_view(),
        name="comments",
    ),
]
