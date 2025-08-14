from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.fields import URLField

from social_media.models import PostImage, Comment, Post
from django.utils.translation import gettext_lazy as _

from social_media.tasks import delayed_post_publish


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
            "author",
            "post",
            "text",
            "parent",
        )
        read_only_fields = ("id", "author", "post")

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
    is_liked = serializers.SerializerMethodField()
    author_name = serializers.CharField(source="author.full_name", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "author", "author_name", "text", "is_liked", "replies")

    def get_is_liked(self, obj) -> bool:
        request = self.context.get("request")
        user = request.user
        return user in obj.likes.all()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
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
            "author",
            "content",
            "likes_count",
            "scheduled_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "author")

    def create(self, validated_data):
        scheduled_at = validated_data.get("scheduled_at")
        post = super().create(validated_data)

        if scheduled_at and scheduled_at > now():
            task = delayed_post_publish.apply_async(args=[post.id], eta=scheduled_at)
            post.celery_task_id = task.id
            post.save()
        else:
            post.publish()

        return post


class PostListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "author",
            "image",
            "content",
            "likes_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "author")

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
            "author",
            "content",
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


class ProfileListSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "picture",
            "first_name",
            "last_name",
            "followers_count",
        )


class ProfileDetailSerializer(serializers.ModelSerializer):
    is_followed = serializers.SerializerMethodField()
    posts = PostListSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "picture",
            "first_name",
            "last_name",
            "followers_count",
            "following_count",
            "is_followed",
            "posts",
        )

    def get_is_followed(self, obj) -> bool:
        request = self.context.get("request")
        user = request.user
        if user in obj.followers.all():
            return True
        return False
