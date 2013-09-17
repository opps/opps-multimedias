# -*- encoding: utf-8 -*-
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from celery import task
from .models import MediaHost

BLACKLIST = getattr(settings, 'OPPS_MULTIMEDIAS_BLACKLIST', [])


@task.periodic_task(run_every=timezone.timedelta(minutes=5))
def upload_media():
    mediahosts = MediaHost.objects.filter(
        status=MediaHost.STATUS_NOT_UPLOADED,
        host_id__isnull=True
    ).exclude(pk__in=BLACKLIST)

    for mediahost in mediahosts:
        if not mediahost.media:
            mediahost.delete()
            continue
        mediahost.status = MediaHost.STATUS_SENDING
        mediahost.save()
        media = mediahost.media
        try:
            media_info = mediahost.api.upload(
                media.TYPE,
                media.media_file.path,
                media.title,
                media.headline,
                media.tags or ''
            )
        except:
            mediahost.status = MediaHost.STATUS_ERROR
            mediahost.status_message = _('Error on upload')
            mediahost.save()
        else:
            mediahost.host_id = media_info['id']
            mediahost.status = MediaHost.STAUTS_PROCESSING
            mediahost.save()


@task.periodic_task(run_every=timezone.timedelta(minutes=2))
def update_mediahost():
    mediahosts = MediaHost.objects.filter(
        host_id__isnull=False,
    )

    # exclude blacklist
    mediahosts = mediahosts.exclude(
        pk__in=BLACKLIST
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
        except:
            pass

        try:
            mediahost.update()
        except:
            pass
