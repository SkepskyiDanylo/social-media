from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.generics import DestroyAPIView, GenericAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from social_media.models import Post, Comment
from social_media.permissions import CanDeleteComment, PostPermission, ProfilePermission
from social_media.serializers import (
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
    PostImageSerializer,
    CommentNestedSerializer,
    UserSerializer,
    ProfileListSerializer,
    ProfileDetailSerializer,
)
from user.serializers import EmptySerializer


class Pagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    page_query_param = "page"


@extend_schema(tags=["Posts"])
class PostViewSet(viewsets.ModelViewSet):
    permission_classes = (PostPermission,)
    pagination_class = Pagination

    def get_queryset(self):
        queryset = Post.objects.all()
        hashtag = self.request.GET.get("hashtag", None)
        hashtag = f"#{hashtag}"
        if hashtag:
            queryset = queryset.filter(content__icontains=hashtag)
        if self.action == "list":
            return queryset.select_related("author").prefetch_related("images")
        if self.action == "retrieve":
            return queryset.select_related("author").prefetch_related(
                "images", "comments", "comments__author"
            )
        return queryset.filter(is_published=True)

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
class CommentView(DestroyAPIView, RetrieveAPIView):
    serializer_class = CommentNestedSerializer
    permission_classes = (CanDeleteComment,)
    lookup_field = "pk"
    lookup_url_kwarg = "cid"

    def get_queryset(self):
        post_id = self.kwargs.get("id")
        return Comment.objects.filter(post_id=post_id)


@extend_schema(tags=["Posts"])
class CommentToggleLikeView(GenericAPIView):
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "cid"

    def post(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user
        if user in instance.comments.all():
            instance.comments.remove(user)
        else:
            instance.comments.add(user)
        return Response(status=status.HTTP_200_OK)


@extend_schema(tags=["Profiles"])
class ProfileViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    permission_classes = (ProfilePermission,)
    pagination_class = Pagination

    def get_serializer_class(self):
        if self.action in ("list", "following_profiles"):
            return ProfileListSerializer
        if self.action in ("retrieve", "me"):
            return ProfileDetailSerializer
        if self.action in ("liked_posts", "delayed_posts"):
            return PostListSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = get_user_model().objects.all()
        if self.action in "retrieve":
            queryset = queryset.prefetch_related("posts", "followers")
        return queryset

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        instance = request.user
        serializer = self.get_serializer(instance=instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="me/liked-posts")
    def liked_posts(self, request):
        instance = self.request.user
        posts = instance.liked_posts.select_related("author").prefetch_related("images")
        serializer = self.get_serializer(instance=posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="me/following-profiles")
    def following_profiles(self, request):
        instance = self.request.user
        profiles = instance.following.all()
        serializer = self.get_serializer(instance=profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="me/posts/delayed")
    def delayed_posts(self, request):
        instance = self.request.user
        posts = instance.posts.all().filter(is_published=False)
        serializer = self.get_serializer(instance=posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
