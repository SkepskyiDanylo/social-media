from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.generics import DestroyAPIView
from rest_framework.response import Response

from social_media.models import Post, Comment
from social_media.permissions import CanDeleteComment
from social_media.serializers import (
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
    PostImageSerializer,
)
from user.serializers import EmptySerializer


@extend_schema(tags=["Posts"])
class PostViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        queryset = Post.objects.all()
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action == "comments":
            return CommentSerializer
        if self.action == "add_image":
            return PostImageSerializer
        if self.action == "toggle_like":
            return EmptySerializer
        return PostSerializer

    @action(
        detail=True,
        url_path="comments",
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def comments(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(
            data=request.data, context={"request": request, "post": instance}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user, post=instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="add-image")
    def add_image(self, request, pk=None):
        instance = self.get_object()
        serializer = PostImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            author=request.user, post=instance, position=instance.images.count() + 1
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["post"],
        url_path="toggle-like",
        permission_classes=[permissions.IsAuthenticated],
    )
    def toggle_like(self, request, pk=None):
        instance = self.get_object()
        user = self.request.user
        if user in instance.likes.all():
            instance.likes.remove(user)
        else:
            instance.likes.add(user)
        return Response(status=status.HTTP_200_OK)


@extend_schema(tags=["Posts"])
class CommentDestroyView(DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = (CanDeleteComment,)
    lookup_field = "cid"

    def get_queryset(self):
        post_id = self.kwargs.get("id")
        return Comment.objects.filter(post_id=post_id)
