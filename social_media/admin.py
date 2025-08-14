from django.contrib import admin
from social_media.models import Post, Comment, PostImage


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "short_content", "is_published", "likes_count", "created_at", "scheduled_at")
    list_filter = ("is_published", "created_at", "scheduled_at")
    search_fields = ("content", "author__email")
    readonly_fields = ("created_at", "updated_at", "likes_count")

    def short_content(self, obj):
        return (obj.content[:40] + "...") if len(obj.content) > 40 else obj.content
    short_content.short_description = "Content"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "short_text", "post", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("text", "author__email")
    readonly_fields = ("created_at", "updated_at")

    def short_text(self, obj):
        return (obj.text[:40] + "...") if len(obj.text) > 40 else obj.text
    short_text.short_description = "Comment"


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "position", "image")
    list_filter = ("post",)
    search_fields = ("post__content",)
