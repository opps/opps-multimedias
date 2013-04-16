# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page

from .views import VideoDetail, AudioDetail


urlpatterns = patterns(
    '',
    url(r'^audio/(?P<channel__long_slug>[\w//-]+)/(?P<slug>[\w-]+)$',
        cache_page(60 * 15)(AudioDetail.as_view()), name='audio_detail'),
    url(r'^video/(?P<channel__long_slug>[\w//-]+)/(?P<slug>[\w-]+)$',
        cache_page(60 * 15)(VideoDetail.as_view()), name='video_detail')
)
