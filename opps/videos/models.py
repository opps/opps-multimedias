
import ffvideo

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from djcelery.models import TaskMeta
from opps.articles.models import Article

from .tasks import upload_video
from .videoapi import Youtube, UOLMais


class VideoHost(models.Model):

    HOST_YOUTUBE = 'youtube'
    HOST_UOLMAIS = 'uolmais'
    HOST_CHOICES = (
        (HOST_YOUTUBE, 'Youtube'),
        (HOST_UOLMAIS, 'UOL Mais'),
    )
    host = models.CharField(_('Host'), max_length=16, choices=HOST_CHOICES,
                            default=HOST_UOLMAIS,
                            help_text=_('Provider that will store the video'))
    host_id = models.CharField(_('Host ID'), max_length=64, null=True)
    url = models.URLField(max_length=255, null=True)
    celery_task = models.OneToOneField('djcelery.TaskMeta', null=True,
                                       verbose_name=_('Celery Task ID'))
    updated = models.BooleanField(_('Updated'), default=False)

    def __unicode__(self):
        return u'{} - {}'.format(self.get_host_display(), self.video)

    @property
    def status(self):
        if self.celery_task:
            return self.celery_task.status
        return _(u'Not Started')

    @property
    def video(self):
        if self.host == VideoHost.HOST_UOLMAIS:
            return self.uolmais_video
        elif self.host == VideoHost.HOST_YOUTUBE:
            return self.youtube_video

    @property
    def api(self):
        if self.host == VideoHost.HOST_UOLMAIS:
            return UOLMais()
        elif self.host == VideoHost.HOST_YOUTUBE:
            return Youtube()

    def upload(self):
        if not self.celery_task:
            result = upload_video.delay(self)
            taskmeta = TaskMeta.objects.get_or_create(task_id=result.id)[0]
            self.celery_task = taskmeta
            self.save()


class Video(Article):
    youtube = models.OneToOneField(VideoHost, verbose_name=_(u'Youtube'),
                                related_name=u'youtube_video',
                                blank=True, null=True)
    uolmais = models.OneToOneField(VideoHost, verbose_name=_(u'UOL Mais'),
                                related_name=u'uolmais_video',
                                blank=True, null=True)
    length = models.PositiveIntegerField(_(u'Length'), null=True,
                                         help_text=_('Video lenght in seconds'))
    video_file = models.FileField(_(u'Video File'), upload_to='videos',
                                  help_text=_(('Temporary file stored '
                                               'until it\'s not sent to '
                                               'final hosting server '
                                               '(ie: Youtube)')))

    def __unicode__(self):
        return u'{}'.format(self.title)

    def _update_length(self):
        """Method used to update video length. This method is usually
        called just after the file upload.

        """
        vs = ffvideo.VideoStream(self.video_file.path)
        self.length = int(vs.duration)

    def save(self, *args, **kwargs):
        super(Video, self).save(*args, **kwargs)

        # We have to save before uploading the video because
        #   the video file is only available on filesystem
        #   after the first save.
        # If there is a way to use the temp_path outside the form
        # we could save just one time.
        # @author: Sergio Oliveira <sergio@tracy.com.br>

        save_again = False

        if not self.length:
            self._update_length()
            save_again = True

        if not self.youtube:
            self.youtube = VideoHost.objects.create(host=VideoHost.HOST_YOUTUBE)
            save_again = True

        if not self.uolmais:
            self.uolmais = VideoHost.objects.create(host=VideoHost.HOST_UOLMAIS)
            save_again = True

        if save_again:
            self.save()

        #self.youtube.upload()
        self.uolmais.upload()
