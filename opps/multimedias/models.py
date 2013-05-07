import os

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from djcelery.models import TaskMeta
from opps.articles.models import Article

from .tasks import upload_media
from opps.core.models import BaseBox
from opps.core.models import BaseConfig
from .mediaapi import Youtube, UOLMais

app_namespace = getattr(
    settings,
    'OPPS_MULTIMEDIAS_URL_NAMESPACE',
    'multimedias'
)


class MediaHost(models.Model):

    STATUS_OK = 'ok'
    STATUS_ERROR = 'error'
    STATUS_DELETED = 'deleted'
    STATUS_NOT_UPLOADED = 'notuploaded'
    STATUS_CHOICES = (
        (STATUS_OK, _('OK')),
        (STATUS_ERROR, _('Error')),
        (STATUS_DELETED, _('Deleted')),
        (STATUS_NOT_UPLOADED, _('Not Uploaded')),
    )

    HOST_YOUTUBE = 'youtube'
    HOST_UOLMAIS = 'uolmais'
    HOST_CHOICES = (
        (HOST_YOUTUBE, 'Youtube'),
        (HOST_UOLMAIS, 'UOL Mais'),
    )
    host = models.CharField(_('Host'), max_length=16, choices=HOST_CHOICES,
                            default=HOST_UOLMAIS,
                            help_text=_('Provider that will store the media'))
    status = models.CharField(_('Status'), max_length=16,
                              choices=STATUS_CHOICES,
                              default=STATUS_NOT_UPLOADED)
    host_id = models.CharField(_('Host ID'), max_length=64, null=True)
    url = models.URLField(max_length=255, null=True)
    embed = models.TextField(default='')
    celery_task = models.OneToOneField('djcelery.TaskMeta', null=True,
                                       verbose_name=_('Celery Task ID'))
    updated = models.BooleanField(_('Updated'), default=False)
    status_message = models.CharField(_('Detailed Status Message'),
                                      max_length=64, null=True)

    def __unicode__(self):
        return u'{} - {}'.format(self.get_host_display(), self.media)

    @property
    def upload_status(self):
        if self.celery_task:
            return self.celery_task.status
        return _(u'Not Started')

    @property
    def media(self):
        if self.host == MediaHost.HOST_UOLMAIS:
            if hasattr(self, 'uolmais_video'):
                return self.uolmais_video
            elif hasattr(self, 'uolmais_audio'):
                return self.uolmais_audio
        elif self.host == MediaHost.HOST_YOUTUBE:
            return self.youtube_video

    @property
    def api(self):
        if self.host == MediaHost.HOST_UOLMAIS:
            return UOLMais()
        elif self.host == MediaHost.HOST_YOUTUBE:
            return Youtube()

    def upload(self):
        if self.celery_task or self.host_id:
            self.update()
        else:
            result = upload_media.delay(self)
            taskmeta = TaskMeta.objects.get_or_create(task_id=result.id)[0]
            self.celery_task = taskmeta
            self.save()

    def update(self, force=False):
        # If the upload wasn't done yet we don't have to update anything
        if self.upload_status != 'SUCCESS' and not force:
            return

        media_info = self.api.get_info(self.host_id)

        changed = False
        if media_info['status'] and media_info['status'] != self.status:
            self.status = media_info['status']
            changed = True

        if media_info['status_msg'] != self.status_message:
            self.status_message = media_info['status_msg']
            changed = True

        if media_info['url'] != self.url:
            self.url = media_info['url']
            changed = True

        if media_info['embed'] and media_info['embed'] != self.embed:
            self.embed = media_info['embed']
            changed = True

        if changed:
            self.save()


def upload_dest(instance, filename):
    return os.path.join(instance.TYPE, filename)


class Media(Article):

    TYPE = None

    uolmais = models.OneToOneField(
        MediaHost, verbose_name=_(u'UOL Mais'),
        related_name=u'uolmais_%(class)s',
        blank=True,
        null=True
    )
    media_file = models.FileField(_(u'File'), upload_to=upload_dest,
                                  help_text=_(('Temporary file stored '
                                               'until it\'s not sent to '
                                               'final hosting server '
                                               '(ie: Youtube)')))

    posts = models.ManyToManyField(
        'articles.Post',
        verbose_name=_(u'Posts'),
        related_name=u'%(class)s',
        null=True, blank=True,
    )

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'{}'.format(self.title)

    def save(self, *args, **kwargs):
        if not self.published:
            self.published = True

        super(Media, self).save(*args, **kwargs)

        # We have to save before uploading the media because
        #   the file is only available on filesystem after
        #   the first save.
        # If there is a way to use the temp_path outside the form
        # we could save just one time.
        # @author: Sergio Oliveira <sergio@tracy.com.br>

        save_again = False

        if hasattr(self, 'youtube') and not self.youtube:
            self.youtube = MediaHost.objects.create(host=MediaHost.HOST_YOUTUBE)
            save_again = True

        if not self.uolmais:
            self.uolmais = MediaHost.objects.create(host=MediaHost.HOST_UOLMAIS)
            save_again = True

        if save_again:
            self.save()

        if hasattr(self, 'youtube'):
            self.youtube.upload()

        self.uolmais.upload()

    def get_absolute_url(self):
        return reverse(
            u'{0}:{1}_detail'.format(app_namespace, self.TYPE),
            kwargs={
                'channel__long_slug': self.channel.long_slug,
                'slug': self.slug
            }
        )

    def get_http_absolute_url(self):
        return 'http://{0}{1}'.format(self.site.domain,
                                      self.get_absolute_url())


class Video(Media):
    TYPE = 'video'

    youtube = models.OneToOneField(
        MediaHost,
        verbose_name=_(u'Youtube'),
        related_name=u'youtube_video',
        blank=True,
        null=True
    )


class Audio(Media):
    TYPE = 'audio'


# OPPS RELATION MODELS
class MediaBox(BaseBox):

    audios = models.ManyToManyField(
        'multimedias.Audio',
        null=True, blank=True,
        related_name='mediabox_audios',
        through='multimedias.MediaBoxAudios'
    )

    videos = models.ManyToManyField(
        'multimedias.Video',
        null=True, blank=True,
        related_name='mediabox_videos',
        through='multimedias.MediaBoxVideos'
    )

    @property
    def medias(self):
        """
        Return a single set of all medias in the BaseBox
        """
        return list(self.videos.all()) + list(self.audios.all())


class MediaBoxAudios(models.Model):
    mediabox = models.ForeignKey(
        'multimedias.MediaBox',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='mediaboxaudios_mediaboxes',
        verbose_name=_(u'Media Box'),
    )
    audio = models.ForeignKey(
        'multimedias.Audio',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='mediaboxaudios_audios',
        verbose_name=_(u'Audio'),
    )

    order = models.PositiveIntegerField(_(u'Order'), default=0)

    def __unicode__(self):
        return u"{0}-{1}".format(self.mediabox.slug, self.audio.slug)


class MediaBoxVideos(models.Model):
    mediabox = models.ForeignKey(
        'multimedias.MediaBox',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='mediaboxvideos_mediaboxes',
        verbose_name=_(u'Media Box'),
    )
    video = models.ForeignKey(
        'multimedias.Video',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='mediaboxvideos_videos',
        verbose_name=_(u'Video'),
    )

    order = models.PositiveIntegerField(_(u'Order'), default=0)

    def __unicode__(self):
        return u"{0}-{1}".format(self.mediabox.slug, self.video.slug)


class MediaConfig(BaseConfig):

    audio = models.ForeignKey(
        'multimedias.Audio',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='mediaconfig_audios',
        verbose_name=_(u'Audio'),
    )

    video = models.ForeignKey(
        'multimedias.Video',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='mediaconfig_videos',
        verbose_name=_(u'Video'),
    )

    class Meta:
        permissions = (("developer", "Developer"),)
        unique_together = ("key_group", "key", "site",
                           "channel", "article", "audio", "video")
