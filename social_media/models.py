import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property

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
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="images")
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
        return f"Image {self.position} for Post {self.post.id}"


class Comment(BaseModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="replies", on_delete=models.CASCADE
    )
    text = models.CharField(max_length=255)
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="comment_likes", blank=True
    )

    def clean(self):
        if self.parent and self.parent.post_id != self.post_id:
            raise ValidationError(_("Parent comment must belong to the same post."))

    def save(self, *args, **kwargs):
        self.full_clean()  # вызовет clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = _("Comments")
        verbose_name = _("Comment")

    def __str__(self):
        snippet = (self.text[:30] + "...") if len(self.text) > 30 else self.text
        return f"{self.author} → Post {self.post.id}: {snippet}"


class Post(BaseModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True
    )
    content = models.CharField(max_length=255)
    is_published = models.BooleanField(default=False)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = _("Posts")
        verbose_name = _("Post")

    def publish(self):
        self.is_published = True
        if self.scheduled_at:
            self.created_at = self.scheduled_at
        self.save()

    def __str__(self):
        snippet = (self.content[:30] + "...") if len(self.content) > 30 else self.content
        return f"{self.author.email} | {snippet} ({'published' if self.is_published else 'draft'})"

    @cached_property
    def likes_count(self) -> int:
        return self.likes.count()
