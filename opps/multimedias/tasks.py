from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from celery import task
from .models import MediaHost


@task.periodic_task(run_every=timezone.timedelta(minutes=5))
def upload_media():
    mediahosts = MediaHost.objects.filter(
        status=MediaHost.STATUS_NOT_UPLOADED,
        host_id__isnull=True
    )

    for mediahost in mediahosts:
        try:
            if not mediahost.media:
                mediahost.delete()
                continue
        except Exception as e:
            print e.message
            continue
            
        mediahost.status = MediaHost.STATUS_SENDING
        mediahost.save()
        media = mediahost.media
        
        try:
             tags = list(media.tags.values_list('name', flat=True))
        except Exception as e:
            print e.message
            tags = []
            
        try:
            media_info = mediahost.api.upload(
                media.TYPE,
                media.media_file.path,
                media.title,
                media.headline,
                tags
            )
        except Exception as e:
            print e.message
            mediahost.status = MediaHost.STATUS_ERROR
            mediahost.status_message = _('Error on upload')
            mediahost.save()

        mediahost.host_id = media_info['id']
        mediahost.status = MediaHost.STAUTS_PROCESSING
        mediahost.save()


@task.periodic_task(run_every=timezone.timedelta(minutes=2))
def update_mediahost():
    mediahosts = MediaHost.objects.filter(
        host_id__isnull=False,
    )
    # Exclude ok content
    mediahosts = mediahosts.exclude(
        status=MediaHost.STATUS_OK,
        url__isnull=False
    )
    # Exclude sending content
    mediahosts = mediahosts.exclude(
        status=MediaHost.STATUS_SENDING
    )
    # Exclude error with reason
    mediahosts = mediahosts.exclude(
        status=MediaHost.STATUS_ERROR,
        status_message__isnull=False
    )
    # Exclude deleted content
    mediahosts = mediahosts.exclude(
        status=MediaHost.STATUS_DELETED,
    )
    # Exclude NONE host_id
    mediahosts = mediahosts.exclude(
        host_id='NONE'
    )

    for mediahost in mediahosts:
        try:
            if not mediahost.media:
                mediahost.delete()
                continue
        except Exception as e:
            print e.message

        try:
            mediahost.update()
        except Exception as e:
            print e.message
