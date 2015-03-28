#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import random
from importlib import import_module
import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _

from opps.articles.models import Article
from opps.core.managers import PublishableManager
from .conf import settings

app_namespace = getattr(
    settings,
    'OPPS_MULTIMEDIAS_URL_NAMESPACE',
    'multimedias'
)

# Get an instance of a logger
logger = logging.getLogger(__name__)


class MediaHost(models.Model):

    STATUS_OK = 'ok'
    STATUS_PROCESSING = 'processing'
    STATUS_ERROR = 'error'
    STATUS_SENDING = 'sending'
    STATUS_DELETED = 'deleted'
    STATUS_NOT_UPLOADED = 'notuploaded'
    STATUS_ENCODING = 'encoding'
    STATUS_NOT_ENCODED = 'not encoded'
    STATUS_CHOICES = (
        (STATUS_OK, _('OK')),
        (STATUS_SENDING, _('Sending')),
        (STATUS_PROCESSING, _('Processing')),
        (STATUS_ERROR, _('Error')),
        (STATUS_DELETED, _('Deleted')),
        (STATUS_NOT_UPLOADED, _('Not Uploaded')),
        (STATUS_ENCODING, _('Encoding')),
        (STATUS_NOT_ENCODED, _('Not Encoded')),
    )

    HOST_VIMEO = 'vimeo'
    HOST_YOUTUBE = 'youtube'
    HOST_UOLMAIS = 'uolmais'
    HOST_LOCAL = 'local'
    HOST_CHOICES = (
        (HOST_VIMEO, 'Vimeo'),
        (HOST_YOUTUBE, 'Youtube'),
        (HOST_UOLMAIS, 'UOL Mais'),
        (HOST_LOCAL, 'Local'),
    )

    HOST_CONFIG = {
        HOST_VIMEO: {
            'fields': ['vimeo_video'], 'api': 'Vimeo'},
        HOST_YOUTUBE: {
            'fields': ['youtube_video'], 'api': 'Youtube'},
        HOST_UOLMAIS: {
            'fields': ['uolmais_video', 'uolmais_audio'], 'api': 'UOLMais'},
        HOST_LOCAL: {
            'fields': ['local_video', 'local_audio'], 'api': 'Local'},
    }

    host = models.CharField(
        _('Host'),
        max_length=16,
        choices=HOST_CHOICES,
        default=HOST_LOCAL,
        help_text=_('Provider that will store the media')
    )

    status = models.CharField(
        _('Status'),
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_NOT_UPLOADED
    )

    host_id = models.CharField(_('Host ID'), max_length=64, blank=True, null=True)
    url = models.URLField(max_length=255, null=True)
    embed = models.TextField(default='')
    updated = models.BooleanField(_('Updated'), default=False)

    status_message = models.CharField(
        _('Detailed Status Message'),
        max_length=150,
        null=True
    )

    retries = models.PositiveSmallIntegerField(_('Retries'), default=0)

    def __unicode__(self):
        return '{}'.format(self.get_host_display())

    @property
    def media(self):
        if self.host in self.HOST_CONFIG:
            for prop in self.HOST_CONFIG[self.host]['fields']:
                if hasattr(self, prop):
                    return getattr(self, prop)
        raise Exception('Host {0} doest no exists'.format(self.host))

    @property
    def api(self):
        media_api = import_module('opps.multimedias.mediaapi')
        cls = getattr(media_api, self.HOST_CONFIG[self.host]['api'])
        return cls(self)

    def update(self):
        # If the upload wasn't done yet we don't have to update anything
        media_info = self.api.get_info(self.host_id)

        changed = False
        if media_info.get('status') != self.status:
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

        if media_info.get('embed') != self.embed:
            self.embed = media_info['embed']
            changed = True

        if media_info['duration'] and not self.media.duration:
            self.media.duration = media_info['duration']
            self.media.save()

        if changed:
            self.save()

    def to_delete(self):
        self.status = self.STATUS_DELETED
        self.save()

    class Meta:
        verbose_name = _('Media Host')
        verbose_name_plural = _('Media Hosts')


def upload_dest(instance, filename):
    ext = filename.split('.')[-1]
    filename = "{0}-{1}.{2}".format(random.getrandbits(32),
                                    instance.slug[:50], ext)
    return os.path.join(instance.TYPE, filename)


class Media(Article):

    TYPE = None

    content = models.TextField(_(u"Content"), null=True, blank=True)
    uolmais = models.OneToOneField(
        MediaHost, verbose_name=_('UOL Mais'),
        related_name='uolmais_%(class)s',
        blank=True,
        null=True
    )

    local = models.OneToOneField(
        MediaHost, verbose_name=_('Local'),
        related_name='local_%(class)s',
        blank=True,
        null=True
    )

    media_file = models.FileField(
        _('File'),
        upload_to=upload_dest,
        help_text=_('Temporary file stored until it\'s not sent to final '
                    'hosting server (ie: Youtube)'),
        blank=True,
        null=True
    )

    ffmpeg_file_flv = models.FileField(
        _('File'),
        upload_to=upload_dest,
        help_text=_('Local video file storage'),
        blank=True,
        null=True
    )

    ffmpeg_file_mp4_sd = models.FileField(
        _('File'),
        upload_to=upload_dest,
        help_text=_('Local video file storage'),
        blank=True,
        null=True
    )

    ffmpeg_file_mp4_hd = models.FileField(
        _('File'),
        upload_to=upload_dest,
        help_text=_('Local video file storage'),
        blank=True,
        null=True
    )

    ffmpeg_file_ogv = models.FileField(
        _('File'),
        upload_to=upload_dest,
        help_text=_('Local video file storage'),
        blank=True,
        null=True
    )

    ffmpeg_file_thumb = models.FileField(
        _('File'),
        upload_to=upload_dest,
        help_text=_('Local video file storage'),
        blank=True,
        null=True
    )

    ffmpeg_file_mp3_128 = models.FileField(
        _('File'),
        upload_to=upload_dest,
        help_text=_('Local audio file storage'),
        blank=True,
        null=True
    )

    duration = models.TimeField(
        verbose_name=_('Duration'),
        help_text=_('Media duration in the following format HH:MM:SS'),
        blank=True,
        null=True
    )

    posts = models.ManyToManyField(
        'articles.Post',
        verbose_name=_('Posts'),
        related_name='%(class)s',
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
        verbose_name = _('Media')
        verbose_name_plural = _('Medias')

    def __unicode__(self):
        return '{}'.format(self.title)

    def get_related_mediahost_fields(self):
        mediahosts = []
        for i in self._meta.fields:
            if isinstance(i, models.OneToOneField) \
                    and i.related.parent_model is MediaHost:
                mediahosts.append(i.name)
        return mediahosts

    def get_media_embed(self):
        if self.uolmais:
            return self.uolmais.embed
        elif self.local:
            return self.local.embed
        else:
            return "<p>TODO</p>"

    def cleanup_mediahost(self):
        related_mh = self.get_related_mediahost_fields()
        for i in related_mh:
            field = getattr(self, i, None)
            if field:
                field.to_delete()
                setattr(self, i, None)

    def save(self, *args, **kwargs):
        def available(mh):
            available_hosts = settings.OPPS_MULTIMEDIAS_ENGINES or ['local']
            return mh in available_hosts

        if not self.pk:
            self.published = False

        related_mh = self.get_related_mediahost_fields()
        updated_media = False

        if self.pk:
            old_media = self.__class__.objects.get(pk=self.pk)
            updated_media = old_media.media_file != self.media_file
            if updated_media:
                self.cleanup_mediahost()

        if updated_media:
            self.published = False

        if hasattr(self, 'youtube') and available(MediaHost.HOST_YOUTUBE):
            if not self.youtube or updated_media:
                self.youtube = MediaHost.objects.create(
                    host=MediaHost.HOST_YOUTUBE
                )

        if hasattr(self, 'vimeo') and available(MediaHost.HOST_VIMEO):
            if not self.vimeo or updated_media:
                self.vimeo = MediaHost.objects.create(
                    host=MediaHost.HOST_VIMEO
                )

        if hasattr(self, 'uolmais') and available(MediaHost.HOST_UOLMAIS):
            if not self.uolmais or updated_media:
                self.uolmais = MediaHost.objects.create(
                    host=MediaHost.HOST_UOLMAIS
                )

        super(Media, self).save(*args, **kwargs)

        if not self.local and \
                MediaHost.HOST_LOCAL in (settings.OPPS_MULTIMEDIAS_ENGINES
                                         or [u'local']):
            self.local = MediaHost.objects.create(
                host=MediaHost.HOST_LOCAL,
                host_id=self.pk
            )
            self.save()



class Video(Media):
    TYPE = 'video'

    youtube = models.OneToOneField(
        MediaHost,
        verbose_name=_('Youtube'),
        related_name='youtube_video',
        blank=True,
        null=True
    )

    vimeo = models.OneToOneField(
        MediaHost,
        verbose_name=_('Vimeo'),
        related_name='vimeo_video',
        blank=True,
        null=True
    )

    related_posts = models.ManyToManyField(
        'containers.Container',
        null=True, blank=True,
        related_name='video_relatedposts'
    )

    objects = PublishableManager()

    @property
    def player(self):
        if self.uolmais.host_id and self.uolmais.status == MediaHost.STATUS_OK:
            player = 'http://player.mais.uol.com.br/embed_v2.swf?mediaId={}'
            return player.format(self.uolmais.host_id)
        if self.youtube.host_id and self.youtube.status == MediaHost.STATUS_OK:
            player = 'http://www.youtube.com/embed/{}'
            return player.format(self.youtube.host_id)
        return ''

    class Meta:
        ordering = ['-date_available', 'title', 'channel_long_slug']
        verbose_name = _('Video')
        verbose_name_plural = _('Videos')


class Audio(Media):
    TYPE = 'audio'

    related_posts = models.ManyToManyField(
        'containers.Container',
        null=True, blank=True,
        related_name='audio_relatedposts'
    )

    objects = PublishableManager()

    class Meta:
        ordering = ['-date_available', 'title', 'channel_long_slug']
        verbose_name = _('Audio')
        verbose_name_plural = _('Audios')


def prepare_delete(sender, instance, *args, **kwargs):
    """
    Cleanup all mediahosts and move to delete queue
    """
    instance.cleanup_mediahost()
    instance.save()

models.signals.pre_delete.connect(prepare_delete, sender=Video)
models.signals.pre_delete.connect(prepare_delete, sender=Audio)
