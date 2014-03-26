# -*- encoding: utf-8 -*-
import datetime
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db import transaction
from celery import task
from .models import MediaHost

BLACKLIST = getattr(settings, 'OPPS_MULTIMEDIAS_BLACKLIST', [])


def log_it(s):
    with open("/tmp/multimedias_upload.log", "a") as log:
        msg = u"{} - {}\n".format(datetime.datetime.now(), s)
        log.write(msg.encode('utf-8'))


@task.periodic_task(run_every=timezone.timedelta(minutes=1))
def upload_media():
    mediahosts = MediaHost.objects.filter(
        status=MediaHost.STATUS_NOT_UPLOADED
    ).exclude(pk__in=BLACKLIST)

    for mediahost in mediahosts:
        try:
            if not mediahost.media:
                mediahost.delete()
                continue
        except Exception as e:
            log_it(u"Error deleting media host")
            continue

        mediahost.status = MediaHost.STATUS_SENDING
        mediahost.save()
        media = mediahost.media

        if media.tags:
            tags = [tag.lower().strip() for tag in media.tags.split(",")]
        else:
            tags = []

        if mediahost.host != MediaHost.HOST_LOCAL:
            try:
                media_info = mediahost.api.upload(
                    media.TYPE,
                    media.media_file.path,
                    media.title,
                    media.headline,
                    tags
                )
            except Exception as e:
                log_it(u'Error on upload {}: {}'.format(
                    unicode(mediahost.media), unicode(e)
                ))
                if mediahost.retries < 3:
                    mediahost.retries += 1
                    mediahost.status = MediaHost.STATUS_NOT_UPLOADED
                else:
                    mediahost.status = MediaHost.STATUS_ERROR
                    mediahost.status_message = _('Error on upload')
            else:
                log_it(u'Uploaded {} - Data returned: {}'.format(
                    unicode(mediahost.media),
                    unicode(media_info)
                ))
                mediahost.host_id = media_info['id']

                mediahost.status = MediaHost.STAUTS_PROCESSING

            with transaction.commit_on_success():
                mediahost.save()
        else:
            media_info = mediahost.api.upload(
                mediahost,
                tags
            )


@task.periodic_task(run_every=timezone.timedelta(minutes=2))
def update_mediahost():
    mediahosts = MediaHost.objects.filter(
        host_id__isnull=False
    )

    # Exclude local host
    mediahosts = mediahosts.exclude(
        host=MediaHost.HOST_LOCAL
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
