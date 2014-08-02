# -*- coding: utf-8 -*-
from django.contrib.sites.models import get_current_site
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import ListView

from opps.multimedias.models import Video, Audio
from opps.containers.views import ContainerDetail
from opps.channels.models import Channel

from .conf import settings


class VideoDetail(ContainerDetail):
    model = Video
    type = 'multimedias'


class AudioDetail(ContainerDetail):
    model = Audio
    type = 'multimedias'


class CurrentChannelMixin(object):
    def get_channel_long_slug(self):
        channel_long_slug = self.kwargs.get('channel__long_slug')
        if self.prepend_channel:
                channel_long_slug = \
                    '%s/%s' % (self.multimedias_channel, channel_long_slug)
        return channel_long_slug


class BaseList(CurrentChannelMixin, ListView):
    paginate_by = 20
    prepend_channel = False

    def get_queryset(self):
        queryset = super(BaseList, self).get_queryset()
        default_site = settings.OPPS_CONTAINERS_SITE_ID or 1
        self.site = get_current_site(self.request)

        channel_long_slug = self.get_channel_long_slug()

        channel = get_object_or_404(Channel, long_slug=channel_long_slug)

        filters = {}
        filters['site_domain'] = self.site.domain
        filters['date_available__lte'] = timezone.now()
        filters['published'] = True
        filters['show_on_root_channel'] = True
        if channel.is_root_node():
            filters['channel__slug__contains'] = channel_long_slug
        else:
            filters['channel__long_slug'] = channel_long_slug

        queryset = self.model.objects.filter(**filters)

        if not queryset and self.site.id != default_site:
            del filters['site_domain']

            filters['site_id'] = default_site

            queryset = self.model.objects.filter(**filters)

        return queryset._clone()

    def get_context_data(self, **kwargs):
        context = super(BaseList, self).get_context_data(**kwargs)
        channel_long_slug = self.get_channel_long_slug()
        try:
            channel = Channel.objects.get(long_slug=channel_long_slug)
        except Channel.DoesNotExist:
            channel = Channel.objects.get_homepage(
                site=get_current_site(self.request)
            )
        context['channel'] = channel
        return context


class VideoList(BaseList):
    model = Video
    multimedias_channel = settings.OPPS_MULTIMEDIAS_VIDEO_CHANNEL
    prepend_channel = settings.OPPS_MULTIMEDIAS_PREPEND_VIDEO_CHANNEL
    template_name = 'multimedias/video/list_paginated.html'


class AudioList(BaseList):
    model = Audio
    multimedias_channel = settings.OPPS_MULTIMEDIAS_AUDIO_CHANNEL
    prepend_channel = settings.OPPS_MULTIMEDIAS_PREPEND_AUDIO_CHANNEL
    template_name = 'multimedias/audio/list_paginated.html'


class ListAll(CurrentChannelMixin, ListView):
    paginate_by = 20

    def get_template_names(self):
        templates = []

        domain_folder = 'containers'
        list_name = 'list'

        templates.append('{}/{}/{}.html'.format(
            self.model._meta.app_label,
            self.model._meta.module_name, list_name))

        if self.request.GET.get('page') and\
           self.__class__.__name__ not in\
           settings.OPPS_PAGINATE_NOT_APP:
            templates.append('{}/{}/{}/{}_paginated.html'.format(
                domain_folder, self.model._meta.app_label,
                self.model._meta.module_name, list_name))

        return templates

    def get_queryset(self):
        default_site = settings.OPPS_CONTAINERS_SITE_ID or 1
        self.site = get_current_site(self.request)

        filters = {}
        filters['site_domain'] = self.site.domain
        filters['date_available__lte'] = timezone.now()
        filters['published'] = True
        filters['show_on_root_channel'] = True
        queryset = self.model.objects.filter(**filters)

        if not queryset and self.site.id != default_site:
            del filters['site_domain']

            filters['site_id'] = default_site

            queryset = self.model.objects.filter(**filters)

        return queryset._clone()

    def get_context_data(self, **kwargs):
        context = super(ListAll, self).get_context_data(**kwargs)
        long_slug = self.get_channel_long_slug()

        try:
            channel = Channel.objects.get(long_slug=long_slug)
        except Channel.DoesNotExist:
            channel = Channel.objects.get_homepage(
                site=get_current_site(self.request)
            )
        context['channel'] = channel
        return context


class AllVideoList(ListAll):
    model = Video
    multimedias_channel = settings.OPPS_MULTIMEDIAS_VIDEO_CHANNEL
    prepend_channel = settings.OPPS_MULTIMEDIAS_PREPEND_VIDEO_CHANNEL
    type = 'video'


class AllAudioList(ListAll):
    model = Audio
    multimedias_channel = settings.OPPS_MULTIMEDIAS_AUDIO_CHANNEL
    prepend_channel = settings.OPPS_MULTIMEDIAS_PREPEND_AUDIO_CHANNEL
    type = 'audio'
