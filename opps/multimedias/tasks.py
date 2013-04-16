
from django.db.models import Q
from django.utils import timezone

from celery import task
from djcelery.models import TaskMeta


@task
def upload_media(mediahost):
    media = mediahost.media
    media_info = mediahost.api.upload(media.TYPE, media.media_file.path,
                                      media.title, media.headline, [])  # media.tags)
    mediahost.host_id = media_info['id']
    mediahost.celery_task = TaskMeta.objects.get(task_id=upload_media.request.id)
    mediahost.save()


@task.periodic_task(run_every=timezone.timedelta(minutes=5))
def update_mediahost():
    q = Q(status='SUCCESS', mediahost__isnull=False)
    error_without_reason = Q(mediahost__status='error',
                             mediahost__status_message__isnull=True)
    no_url = Q(mediahost__url__isnull=True)
    q &= no_url | error_without_reason
    tasks = TaskMeta.objects.filter(q)

    for task in tasks:
        task.mediahost.update()
