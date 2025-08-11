import os
import uuid

from django.db import models

from social_media_api import settings
from django.utils.translation import gettext_lazy as _


def post_image(instance: "Post", filename: str) -> str:
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join("images", "posts", filename)


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class PostImage(BaseModel):
    image = models.ImageField(
        upload_to=post_image,
    )
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["post", "position"],
                name="unique_post_position",
            )
        ]
        verbose_name_plural = _("Post Images")
        verbose_name = _("Post Image")

    def __str__(self):
        return f"{self.post.pk} - {self.position}"


class Comment(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="replies", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    post = models.OneToOneField("Post", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="comment_likes", blank=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = _("Comments")
        verbose_name = _("Comment")

    def __str__(self):
        return f"{self.user} comment for {self.post.pk}"


class Post(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True
    )
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = _("Posts")
        verbose_name = _("Post")

    def __str__(self):
        return f"{self.user.username} post #{self.created_at}"
