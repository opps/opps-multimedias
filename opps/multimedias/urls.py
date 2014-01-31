# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page

from opps.contrib.feeds.views import ContainerFeed, ChannelFeed

from .views import VideoList, AudioList, AllVideoList, AllAudioList

from .conf import settings

urlpatterns = patterns(
    '',
    # CHANNEL FEED LIST
    url(r'^{}/(?P<long_slug>[\w\b//-]+)/(rss|feed)$'.format(
        settings.OPPS_MULTIMEDIAS_VIDEO_CHANNEL),
        cache_page(settings.OPPS_CACHE_EXPIRE)(ChannelFeed()),
        name='video_list_feed',),
    url(r'^{}/(?P<long_slug>[\w\b//-]+)/(rss|feed)$'.format(
        settings.OPPS_MULTIMEDIAS_AUDIO_CHANNEL),
        cache_page(settings.OPPS_CACHE_EXPIRE)(ChannelFeed()),
        name='audio_list_feed',),
    # CHANNEL LIST
    url(r'^{}/(?P<channel__long_slug>[\w\b//-]+)/$'.format(
        settings.OPPS_MULTIMEDIAS_VIDEO_CHANNEL),
        cache_page(settings.OPPS_CACHE_EXPIRE)(VideoList.as_view()),
        name='video_list'),
    url(r'^{}/(?P<channel__long_slug>[\w\b//-]+)/$'.format(
        settings.OPPS_MULTIMEDIAS_AUDIO_CHANNEL),
        cache_page(settings.OPPS_CACHE_EXPIRE)(AudioList.as_view()),
        name='audio_list'),
    # ALL FEED LIST
    url(r'^{}/(rss|feed)$'.format(settings.OPPS_MULTIMEDIAS_VIDEO_CHANNEL),
        cache_page(settings.OPPS_CACHE_EXPIRE)(ContainerFeed('Video')),
        name='videos_list_feed'),
    url(r'^{}/(rss|feed)$'.format(settings.OPPS_MULTIMEDIAS_AUDIO_CHANNEL),
        cache_page(settings.OPPS_CACHE_EXPIRE)(ContainerFeed('Audio')),
        name='audios_list_feed'),
    # ALL LIST
    url(r'^{}/$'.format(settings.OPPS_MULTIMEDIAS_VIDEO_CHANNEL),
        cache_page(settings.OPPS_CACHE_EXPIRE)(AllVideoList.as_view()),
        name='videos_list',
        kwargs={
            'channel__long_slug': settings.OPPS_MULTIMEDIAS_VIDEO_CHANNEL}),
    url(r'^{}/$'.format(settings.OPPS_MULTIMEDIAS_AUDIO_CHANNEL),
        cache_page(settings.OPPS_CACHE_EXPIRE)(AllAudioList.as_view()),
        name='audios_list',
        kwargs={
            'channel__long_slug': settings.OPPS_MULTIMEDIAS_AUDIO_CHANNEL}),
)
