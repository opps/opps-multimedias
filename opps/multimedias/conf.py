#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings

from appconf import AppConf


class OppsLiveBloggingConf(AppConf):
    VIDEO_CHANNEL = getattr(settings, 'OPPS_MULTIMEDIAS_VIDEO_CHANNEL',
                            'videos')
    AUDIO_CHANNEL = getattr(settings, 'OPPS_MULTIMEDIAS_AUDIO_CHANNEL',
                            'audios')
    class Meta:
        prefix = 'opps_multimedias'
