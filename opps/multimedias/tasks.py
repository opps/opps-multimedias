
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from celery import task
from djcelery.models import TaskMeta


@task
def upload_media(mediahost):
    media = mediahost.media
    tags = list(media.tags.values_list('name', flat=True))
    media_info = mediahost.api.upload(
        media.TYPE,
        media.media_file.path,
        media.title,
        media.headline,
        tags
    )
    mediahost.host_id = media_info['id']
    mediahost.celery_task = TaskMeta.objects.get(
        task_id=upload_media.request.id
    )
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

    # update failure tasks
    tasks = TaskMeta.objects.filter(
        ~Q(mediahost__status='error'),
        status='FAILURE'
    )
    for task in tasks:
        task.mediahost.status = 'error'
        task.mediahost.status_message = _('Error on upload')
        task.mediahost.save()
