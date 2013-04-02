
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from celery.result import AsyncResult

from opps.articles.models import Article
from .tasks import upload_video
from .youtube import Youtube


class Video(Article):

    HOST_YOUTUBE = 'youtube'
    HOST_UOLMAIS = 'uolmais'
    HOST_CHOICES = (
        (HOST_YOUTUBE, 'Youtube'),
        (HOST_UOLMAIS, 'UOL Mais'),
    )

    length = models.PositiveIntegerField(_(u'Length'), blank=True,
                                         help_text=_('Video lenght in seconds'))
    name = models.CharField(_(u'Name'), max_length='255')
    video_file = models.FileField(_(u'Video File'), upload_to='videos',
                                  help_text=_(('Temporary file stored '
                                               'until it\'s not sent to '
                                               'final hosting server '
                                               '(ie: Youtube)')))
    host = models.CharField(_('Host'), max_length=16, choices=HOST_CHOICES,
                            default=HOST_UOLMAIS,
                            help_text=_('Provider that will store the video'))
    host_id = models.CharField(_('Host ID'), max_length=64, null=True)
    host_url = models.URLField(max_length=255, null=True)
    host_swf_url = models.URLField(max_length=255, null=True)

    celery_task_id = models.CharField(_('Upload Task ID'), max_length=64,
                                      null=True)

    @property
    def hostctl(self):
        if self.host == Video.HOST_YOUTUBE:
            return Youtube(self)

    @property
    def celery_result(self):
        return AsyncResult(self.celery_task_id)

    def update_host(self):
        # Without a host_id we can't update anything at the host
        if not self.host_id:
            return

        if self.published:
            self.hostctl.publish()
        else:
            self.hostctl.unpublish()

    def save(self, *args, **kwargs):
        super(Video, self).save(*args, **kwargs)
        if not self.celery_task_id:
            async_res = upload_video.delay(self)
            self.celery_task_id = async_res.id
            self.save()
        else:
            self.update_host()
