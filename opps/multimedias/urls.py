# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page
from django.conf import settings

from opps.contrib.feeds.views import ContainerFeed, ChannelFeed

from .views import (VideoDetail, AudioDetail, VideoList, AudioList,
                    AllVideoList, AllAudioList)


urlpatterns = patterns(
    '',
    url(r'^video/(?P<long_slug>[\w\b//-]+)/(rss|feed)$',
        cache_page(settings.OPPS_CACHE_EXPIRE)(
            ChannelFeed()), name='video_list_feed'),
    url(r'^audio/(?P<long_slug>[\w\b//-]+)/(rss|feed)$',
       cache_page(settings.OPPS_CACHE_EXPIRE)(
           ChannelFeed()), name='audio_list_feed'),

    url(r'^audio/(?P<channel__long_slug>[\w//-]+)/(?P<slug>[\w-]+)$',
        cache_page(settings.OPPS_CACHE_EXPIRE)(
            AudioDetail.as_view()), name='audio_detail'),
    url(r'^video/(?P<channel__long_slug>[\w//-]+)/(?P<slug>[\w-]+)$',
        cache_page(settings.OPPS_CACHE_EXPIRE)(
            VideoDetail.as_view()), name='video_detail'),

    url(r'^video/(?P<channel__long_slug>[\w\b//-]+)/$',
        VideoList.as_view(), name='video_list'),
    url(r'^audio/(?P<channel__long_slug>[\w\b//-]+)/$',
        AudioList.as_view(), name='audio_list'),

    url(r'^videos/(rss|feed)$',
        cache_page(settings.OPPS_CACHE_EXPIRE)(
            ContainerFeed('Video')), name='videos_list_feed'),
    url(r'^audios/(rss|feed)$',
        cache_page(settings.OPPS_CACHE_EXPIRE)(
            ContainerFeed('Audio')), name='audios_list_feed'),

    url(r'^videos/$',
        cache_page(settings.OPPS_CACHE_EXPIRE)(
            AllVideoList.as_view()), name='videos_list'),
    url(r'^audios/$',
        cache_page(settings.OPPS_CACHE_EXPIRE)(
            AllAudioList.as_view()), name='audios_list'),
)
