from celery import shared_task
from django.utils.timezone import now

from social_media.models import Post


@shared_task
def delayed_post_publish(pk):

    try:
        post = Post.objects.get(id=pk)
    except Post.DoesNotExist:
        return

    # публикуем только если ещё не опубликован
    if not post.is_published and (not post.scheduled_at or post.scheduled_at <= now()):
        post.publish()
