# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page

from .views import (VideoDetail, AudioDetail, VideoList, AudioList,
                    AllVideoList, AllAudioList)


urlpatterns = patterns(
    '',
    url(r'^audio/(?P<channel__long_slug>[\w//-]+)/(?P<slug>[\w-]+)$',
        cache_page(60 * 15)(AudioDetail.as_view()), name='audio_detail'),
    url(r'^video/(?P<channel__long_slug>[\w//-]+)/(?P<slug>[\w-]+)$',
        cache_page(60 * 15)(VideoDetail.as_view()), name='video_detail'),

    url(r'^video/(?P<channel__long_slug>[\w\b//-]+)/$',
        VideoList.as_view(), name='video_list'),
    url(r'^audio/(?P<channel__long_slug>[\w\b//-]+)/$',
        AudioList.as_view(), name='audio_list'),

    url(r'^videos/$',
        AllVideoList.as_view(), name='videos_list'),
    url(r'^audios/$',
        AllAudioList.as_view(), name='audios_list'),
)
