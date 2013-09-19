#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings

from appconf import AppConf


class OppsLiveBloggingConf(AppConf):
    VIDEO_CHANNEL = getattr(settings, 'OPPS_MULTIMEDIAS_VIDEO_CHANNEL', 'video')
    AUDIO_CHANNEL = getattr(settings, 'OPPS_MULTIMEDIAS_AUDIO_CHANNEL', 'audio')
    class Meta:
        prefix = 'opps_multimedias'
