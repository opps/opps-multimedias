#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import random

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from opps.articles.models import Article
from opps.core.managers import PublishableManager
from .mediaapi import Youtube, UOLMais

app_namespace = getattr(
    settings,
    'OPPS_MULTIMEDIAS_URL_NAMESPACE',
    'multimedias'
)


class MediaHost(models.Model):

    STATUS_OK = u'ok'
    STAUTS_PROCESSING = u'processing'
    STATUS_ERROR = u'error'
    STATUS_SENDING = u'sending'
    STATUS_DELETED = u'deleted'
    STATUS_NOT_UPLOADED = u'notuploaded'
    STATUS_ENCODING = u'encoding'
    STATUS_NOT_ENCODED = u'not encoded'
    STATUS_CHOICES = (
        (STATUS_OK, _(u'OK')),
        (STATUS_SENDING, _(u'Sending')),
        (STAUTS_PROCESSING, _(u'Processing')),
        (STATUS_ERROR, _(u'Error')),
        (STATUS_DELETED, _(u'Deleted')),
        (STATUS_NOT_UPLOADED, _(u'Not Uploaded')),
        (STATUS_ENCODING, _(u'Encoding')),
        (STATUS_NOT_ENCODED, _(u'Not Encoded')),
    )

    HOST_YOUTUBE = u'youtube'
    HOST_UOLMAIS = u'uolmais'
    HOST_LOCAL = u'local'
    HOST_CHOICES = (
        (HOST_YOUTUBE, u'Youtube'),
        (HOST_UOLMAIS, u'UOL Mais'),
        (HOST_LOCAL, u'Local'),
    )
    host = models.CharField(
        _(u'Host'),
        max_length=16,
        choices=HOST_CHOICES,
        default=HOST_LOCAL,
        help_text=_(u'Provider that will store the media')
    )
    status = models.CharField(
        _(u'Status'),
        max_length=16,
        choices=STATUS_CHOICES,
        default=STATUS_NOT_UPLOADED
    )
    host_id = models.CharField(_(u'Host ID'), max_length=64, null=True)
    url = models.URLField(max_length=255, null=True)
    embed = models.TextField(default=u'')
    updated = models.BooleanField(_(u'Updated'), default=False)
    status_message = models.CharField(
        _(u'Detailed Status Message'),
        max_length=150,
        null=True
    )
    retries = models.PositiveSmallIntegerField(_(u'Retries'), default=0)

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
        elif self.host == MediaHost.HOST_LOCAL:
            return self.local_video

    @property
    def api(self):
        if self.host == MediaHost.HOST_UOLMAIS:
            return UOLMais()
        elif self.host == MediaHost.HOST_YOUTUBE:
            return Youtube()
        elif self.host == MediaHost.HOST_LOCAL:
            return Local()

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

        if changed:
            self.save()

    class Meta:
        verbose_name = _(u'Media Host')
        verbose_name_plural = _(u'Media Hosts')


def upload_dest(instance, filename):
    ext = filename.split('.')[-1]
    filename = u"{0}-{1}.{2}".format(random.getrandbits(32),
                                     instance.slug[:50], ext)
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
        help_text=_(u'Temporary file stored until it\'s not sent to final '
                    u'hosting server (ie: Youtube)')
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
        verbose_name = _(u'Media')
        verbose_name_plural = _(u'Medias')

    def __unicode__(self):
        return u'{}'.format(self.title)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.published = False

        if hasattr(self, 'youtube') and not self.youtube:
            self.youtube = MediaHost.objects.create(
                host=MediaHost.HOST_YOUTUBE
            )

        if hasattr(self, 'local') and not self.local:
            self.youtube = MediaHost.objects.create(
                host=MediaHost.HOST_LOCAL
            )

        if not self.uolmais:
            self.uolmais = MediaHost.objects.create(
                host=MediaHost.HOST_UOLMAIS
            )

        super(Media, self).save(*args, **kwargs)


class Video(Media):
    TYPE = u'video'

    youtube = models.OneToOneField(
        MediaHost,
        verbose_name=_(u'Youtube'),
        related_name=u'youtube_video',
        blank=True,
        null=True
    )

    video_file = models.FileField(
        _(u'File'),
        upload_to=upload_dest,
        help_text=_(u'Local video file storage')
        blank=True,
        null=True
    )

    objects = PublishableManager()

    @property
    def player(self):
        if self.uolmais.host_id and self.uolmais.status == MediaHost.STATUS_OK:
            player = u'http://player.mais.uol.com.br/embed_v2.swf?mediaId={}'
            return player.format(self.uolmais.host_id)
        if self.youtube.host_id and self.youtube.status == MediaHost.STATUS_OK:
            player = u'http://www.youtube.com/embed/{}'
            return player.format(self.youtube.host_id)
        return u''

    class Meta:
        ordering = ['-date_available', 'title', 'channel_long_slug']
        verbose_name = _(u'Video')
        verbose_name_plural = _(u'Videos')


class Audio(Media):
    TYPE = u'audio'

    objects = PublishableManager()

    class Meta:
        ordering = ['-date_available', 'title', 'channel_long_slug']
        verbose_name = _(u'Audio')
        verbose_name_plural = _(u'Audios')
