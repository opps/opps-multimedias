# -*- encoding: utf-8 -*-
import datetime
import subprocess as sp
import logging

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from celery import task
from opps.utils.text import split_tags

from .models import MediaHost
from .mediaapi import MediaAPIError


# Get an instance of a logger
logger = logging.getLogger(__name__)


BLACKLIST = getattr(settings, 'OPPS_MULTIMEDIAS_BLACKLIST', [])
LOCAL_MAX_PARALLEL = getattr(
    settings, 'OPPS_MULTIMEDIAS_LOCAL_MAX_PARALLEL', 1)
UPLOAD_MEDIA_INTERVAL = getattr(
    settings, 'OPPS_MULTIMEDIAS_UPLOAD_MEDIA_INTERVAL', 5)
UPDATE_MEDIAHOST_INTERVAL = getattr(
    settings, 'OPPS_MULTIMEDIAS_UPDATE_MEDIAHOST_INTERVAL', 2)


@task.periodic_task(run_every=timezone.timedelta(
    minutes=UPLOAD_MEDIA_INTERVAL))
def upload_media():
    mediahosts = MediaHost.objects.filter(
        status=MediaHost.STATUS_NOT_UPLOADED
    ).exclude(pk__in=BLACKLIST)

    if 'local' in settings.OPPS_MULTIMEDIAS_ENGINES:
        ffmpeg_active = False

        try:
            output = sp.check_output(
                "ps aux | grep -v grep | grep {0}".format(
                    settings.OPPS_MULTIMEDIAS_FFMPEG),
                shell=True)
            if not output:
                raise Exception("FFMPEG doesn't run!")
        except:
            MediaHost.objects.filter(
                host=MediaHost.HOST_LOCAL,
                status=MediaHost.STATUS_PROCESSING).update(
                    status=MediaHost.STATUS_NOT_UPLOADED)

    for mediahost in mediahosts:
        try:
            media = mediahost.media
        except:
            mediahost.to_delete()
            continue

        tags = split_tags(media.tags)

        if mediahost.host != MediaHost.HOST_LOCAL:
            if mediahost.host == MediaHost.HOST_VIMEO:
                mediahost.api.upload()
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
                    tags
                )
            except Exception as e:
                logger.error(u'Error on upload {}: {}'.format(
                    unicode(mediahost.media), unicode(e)
                ))
                if mediahost.retries < 3:
                    mediahost.retries += 1
                    mediahost.status = MediaHost.STATUS_NOT_UPLOADED
                else:
                    mediahost.status = MediaHost.STATUS_ERROR
                    mediahost.status_message = _('Error on upload')
            else:
                logger.info(u'Uploaded {} - Data returned: {}'.format(
                    unicode(mediahost.media),
                    unicode(media_info)
                ))
                mediahost.host_id = media_info['id']
                mediahost.status = MediaHost.STATUS_PROCESSING

            with transaction.commit_on_success():
                mediahost.save()
        else:
            local_in_process = MediaHost.objects.filter(
                host=MediaHost.HOST_LOCAL,
                status=MediaHost.STATUS_PROCESSING).count()

            if LOCAL_MAX_PARALLEL and local_in_process >= LOCAL_MAX_PARALLEL:
                continue

            media_info = mediahost.api.upload(
                mediahost,
                tags
            )


@task.periodic_task(run_every=timezone.timedelta(minutes=2))
def update_mediahost():
    mediahosts = MediaHost.objects.filter(status=MediaHost.STATUS_PROCESSING)
    mediahosts = mediahosts.exclude(
        Q(host_id__isnull=True) | Q(host_id=''),  # Empty host_id
        host=MediaHost.HOST_LOCAL,                # Exclude local host
        pk__in=BLACKLIST,                         # exclude blacklist
        host_id='NONE')                           # Exclude NONE host_id

    for mediahost in mediahosts:
        try:
            if not mediahost.media:
                mediahost.to_delete()
                continue
        except Exception as e:
            logger.exception(e.message)
            continue

        try:
            mediahost.update()
            continue
        except Exception as e:
            logger.exception(e.message)


@task.periodic_task(run_every=timezone.timedelta(minutes=60))
def delete_mediahost():
    mediahosts = MediaHost.objects.filter(status=MediaHost.STATUS_DELETED)
    for mediahost in mediahosts:
        api = mediahost.api
        if hasattr(api, 'delete'):
            try:
                api.delete()
            except NotImplementedError:
                pass
            except MediaAPIError as e:
                logger.exception(e.message)
            else:
                mediahost.delete()
