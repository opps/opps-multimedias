#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url, include

from tastypie.api import Api

from .conf import settings
from opps.api.conf import settings as apiset
from .api import Audio, Video


A = lambda channel: Api(
    api_name=u"{}/{}".format(apiset.OPPS_API_NAME, channel))


audio_api = A(settings.OPPS_MULTIMEDIAS_AUDIO_CHANNEL)
audio_api.register(Audio())

video_api = A(settings.OPPS_MULTIMEDIAS_VIDEO_CHANNEL)
video_api.register(Video())

urlpatterns = patterns(
    '',
    url(r'^api/', include(audio_api.urls)),
    url(r'^api/', include(video_api.urls)),
)
