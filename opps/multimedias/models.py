import os
import random

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from djcelery.models import TaskMeta
from opps.articles.models import Article

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
    STAUTS_PROCESSING = 'processing'
    STATUS_ERROR = 'error'
    STATUS_SENDING = 'sending'
    STATUS_DELETED = 'deleted'
    STATUS_NOT_UPLOADED = 'notuploaded'
    STATUS_CHOICES = (
        (STATUS_OK, _('OK')),
        (STATUS_SENDING, _('Sending')),
        (STAUTS_PROCESSING, _('Processing')),
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
    host = models.CharField(
        _('Host'),
        max_length=16,
        choices=HOST_CHOICES,
        default=HOST_UOLMAIS,
        help_text=_('Provider that will store the media')
    )
    status = models.CharField(
        _('Status'),
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_NOT_UPLOADED
    )
    host_id = models.CharField(_('Host ID'), max_length=64, null=True)
    url = models.URLField(max_length=255, null=True)
    embed = models.TextField(default='')
    celery_task = models.OneToOneField(
        'djcelery.TaskMeta',
        null=True,
        verbose_name=_('Celery Task ID')
    )
    updated = models.BooleanField(_('Updated'), default=False)
    status_message = models.CharField(
        _('Detailed Status Message'),
        max_length=64,
        null=True
    )

    def __unicode__(self):
        return u'{} - {}'.format(self.get_host_display(), self.media)

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

    def update(self):
        # If the upload wasn't done yet we don't have to update anything
        media_info = self.api.get_info(self.host_id)

        changed = False
        if media_info['status'] and media_info['status'] != self.status:
            self.status = media_info['status']
            if self.status == self.STATUS_OK:
                self.media.published = True
                self.media.save()
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
    ext = filename.split('.')[-1]
    filename = u"{0}-{1}.{2}".format(random.getrandbits(32),
                                     instance.slug, ext)
    return os.path.join(instance.TYPE, filename)


class Media(Article):

    TYPE = None

    uolmais = models.OneToOneField(
        MediaHost, verbose_name=_(u'UOL Mais'),
        related_name=u'uolmais_%(class)s',
        blank=True,
        null=True
    )
    media_file = models.FileField(
        _(u'File'),
        upload_to=upload_dest,
        help_text=_(('Temporary file stored until it\'s not sent to '
                     'final hosting server (ie: Youtube)'))
    )

    posts = models.ManyToManyField(
        'articles.Post',
        verbose_name=_(u'Posts'),
        related_name=u'%(class)s',
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
        ordering = ['-date_available', 'title', 'channel_long_slug']

    def __unicode__(self):
        return u'{}'.format(self.title)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.published = False

        if hasattr(self, 'youtube') and not self.youtube:
            self.youtube = MediaHost.objects.create(
                host=MediaHost.HOST_YOUTUBE
            )

        if not self.uolmais:
            self.uolmais = MediaHost.objects.create(
                host=MediaHost.HOST_UOLMAIS
            )

        super(Media, self).save(*args, **kwargs)

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

    @property
    def player(self):
        if self.uolmais.host_id and self.uolmais.status == MediaHost.STATUS_OK:
            player = 'http://player.mais.uol.com.br/embed_v2.swf?mediaId={}'
            return player.format(self.uolmais.host_id)
        if self.youtube.host_id and self.youtube.status == MediaHost.STATUS_OK:
            player = 'http://www.youtube.com/embed/{}'
            return player.format(self.youtube.host_id)
        return ''


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

    def ordered_audios(self, field='order'):
        now = timezone.now()
        qs = self.audios.filter(
            published=True,
            date_available__lte=now,
            mediaboxaudios_audios__date_available__lte=now
        ).filter(
            models.Q(mediaboxaudios_audios__date_end__gte=now) |
            models.Q(mediaboxaudios_audios__date_end__isnull=True)
        )
        return qs.order_by('mediaboxaudios_audios__order').distinct()

    def ordered_videos(self, field='order'):
        now = timezone.now()
        qs = self.videos.filter(
            published=True,
            date_available__lte=now,
            mediaboxvideos_videos__date_available__lte=now
        ).filter(
            models.Q(mediaboxvideos_videos__date_end__gte=now) |
            models.Q(mediaboxvideos_videos__date_end__isnull=True)
        )
        return qs.order_by('mediaboxvideos_videos__order').distinct()

    @property
    def medias(self):
        """
        Return a single set of all medias in the BaseBox
        """
        return list(self.ordered_videos()) + list(self.ordered_audios())


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
    date_available = models.DateTimeField(_(u"Date available"),
                                          default=timezone.now, null=True)
    date_end = models.DateTimeField(_(u"End date"), null=True, blank=True)

    class Meta:
        ordering = ('order',)
        verbose_name = _('Media box audio')
        verbose_name_plural = _('Media boxes audios')

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
    date_available = models.DateTimeField(_(u"Date available"),
                                          default=timezone.now, null=True)
    date_end = models.DateTimeField(_(u"End date"), null=True, blank=True)

    class Meta:
        ordering = ('order',)
        verbose_name = _('Media box video')
        verbose_name_plural = _('Media boxes videos')

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
