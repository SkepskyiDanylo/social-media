from rest_framework import serializers
from rest_framework.fields import URLField

from social_media.models import PostImage, Comment, Post
from user.models import User
from django.utils.translation import gettext_lazy as _


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = (
            "id",
            "image",
            "position",
        )
        read_only_fields = ("id", "position")


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = (
            "id",
            "user",
            "post",
            "text",
            "parent",
        )
        read_only_fields = ("id", "user", "post")

    def validate(self, attrs):
        parent = attrs.get("parent")
        post = self.context.get("post")
        if parent and parent.post != post:
            raise serializers.ValidationError(
                _("Parent comment belongs to another post.")
            )
        return attrs


class CommentNestedSerializer(serializers.ModelSerializer):
    replies = RecursiveField(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "user", "text", "replies")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "picture",
            "first_name",
            "last_name",
        )


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "description",
            "likes_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user")


class PostListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "image",
            "description",
            "likes_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user")

    def get_image(self, obj) -> URLField:
        request = self.context.get("request")
        image = obj.images.first()
        if image and request:
            return request.build_absolute_uri(image.image.url)
        return None


class PostDetailSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    images = PostImageSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "description",
            "likes_count",
            "comments",
            "created_at",
            "updated_at",
            "images",
            "is_liked",
        )

    def get_is_liked(self, obj) -> bool:
        request = self.context.get("request")
        user = request.user
        if user in obj.likes.all():
            return True
        return False

    def get_comments(self, obj) -> CommentNestedSerializer(many=True):
        queryset = obj.comments.filter(parent__isnull=True)
        return CommentNestedSerializer(queryset, many=True, context=self.context).data
