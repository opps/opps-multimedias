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

    class Meta:
        prefix = 'opps_multimedias'
