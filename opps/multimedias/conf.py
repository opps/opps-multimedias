#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings

from appconf import AppConf


class OppsMultimediasConf(AppConf):
    VIDEO_CHANNEL = getattr(settings, 'OPPS_MULTIMEDIAS_VIDEO_CHANNEL',
                            'videos')
    AUDIO_CHANNEL = getattr(settings, 'OPPS_MULTIMEDIAS_AUDIO_CHANNEL',
                            'audios')
    ENGINES = getattr(settings, 'OPPS_MULTIMEDIAS_ENGINES',
                      [u'local'])
    AUDIO_ENGINES = getattr(settings, 'OPPS_MULTIMEDIAS_AUDIO_ENGINES',
                            [u'local'])

    FFMPEG = getattr(settings, 'OPPS_MULTIMEDIAS_FFMPEG', '/usr/bin/ffmpeg')

    # Example: If you have this channel structure:
    #  videos/
    #   animals
    # And configure put opps-multimedias to serve the channels on the url
    # /videos/ the channel animals of the example will be served on url
    # /videos/videos/animals
    # This is not good, so if you are also working with a root channel that
    # has the same url/slug of OPPS_MULTIMEDIAS_VIDEO_CHANNEL like the example
    # just enable this option.

    PREPEND_AUDIO_CHANNEL = \
        getattr(settings, "OPPS_MULTIMEDIAS_PREPEND_AUDIO_CHANNEL", False)

    PREPEND_VIDEO_CHANNEL = \
        getattr(settings, "OPPS_MULTIMEDIAS_PREPEND_VIDEO_CHANNEL", False)

    class Meta:
        prefix = 'opps_multimedias'
