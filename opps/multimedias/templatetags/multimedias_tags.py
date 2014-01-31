#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.utils import timezone

from django.db.models import Count, Max
from opps.core.templatetags.box_tags import get_box, get_all_box

from ..models import Audio, Video


register = template.Library()


@register.simple_tag(takes_context=True)
def get_active_multimedias(context, number=5, channel_slug=None,
                           template_name='multimedias/actives.html',
                           type=None):
    """
    Type can be 'audio' or 'video'
    in template check for
    for media in active_multimedias:
        media.TYPE == 'video'
        media.TYPE == 'audio'
    """
    active_multimedias = []

    cache_key = u'ActiveMultimedias-{}-{}-{}'.format(number, channel_slug,
                                                     template_name)

    exists = cache.get(cache_key)
    if exists:
        return exists

    if not type or type == 'audio':
        active_audios = Audio.objects.all_published()
        if channel_slug:
            active_audios = active_audios.filter(
                channel__long_slug=channel_slug
            ).distinct()
        active_audios = active_audios[:number]
        active_multimedias.extend(active_audios)

    if not type or type == 'video':
        active_videos = Video.objects.all_published()
        if channel_slug:
            active_videos = active_videos.filter(
                channel__long_slug=channel_slug
            ).distinct()
        active_videos = active_videos[:number]
        active_multimedias.extend(active_videos)

    t = template.loader.get_template(template_name)

    render = t.render(template.Context({'active_multimedias': active_multimedias,
                                      'channel_slug': channel_slug,
                                      'number': number}))
    cache.set(cache_key, render, 60 * 60)
    return render


@register.simple_tag(takes_context=True)
def get_mediabox(context, slug, template_name=None):
    return get_box(context, 'multimedias', slug, template_name)


@register.simple_tag(takes_context=True)
def get_all_mediabox(context, channel_slug, template_name=None):
    return get_all_box(context, 'multimedias', channel_slug, template_name)


@register.assignment_tag(takes_context=True)
def get_all_channel(context):
    site = Site.objects.get(id=settings.SITE_ID)

    cachekey = '{}-{}-{}-{}'.format(u'get_all_channel', 'multime', site.domain,
                                    u'multimedia')
    getcache = cache.get(cachekey)

    if getcache:
        return getcache

    _list = Video.objects.values(
        'channel_name',
        'channel_long_slug'
    ).filter(
        published=True,
        date_available__lte=timezone.now(),
        site=site
    ).annotate(
        count=Count('channel_long_slug'),
        date=Max('date_available')).order_by('-date')
    cache.set(cachekey, _list, 3600)

    return _list


@register.assignment_tag()
def get_multimedias(number=5, channel_slug=None, type=None,
                    include_subchannels=False):
    """
    Type can be 'audio' or 'video'
    for media in active_multimedias:
        media.TYPE == 'video'
        media.TYPE == 'audio'

    If include_subchannels = True the queryset will look into the subchannels
    for multimedias as well
    """
    active_multimedias = []

    if not type or type == 'audio':
        active_audios = Audio.objects.all_published()
        if channel_slug:
            lookup = {'channel__slug': channel_slug}
            if include_subchannels:
                lookup = {'channel__long_slug__contains': channel_slug}
            active_audios = active_audios.filter(
                **lookup
            ).distinct()
        active_audios = active_audios[:number]
        active_multimedias.extend(active_audios)

    if not type or type == 'video':
        active_videos = Video.objects.all_published()
        if channel_slug:
            lookup = {'channel__slug': channel_slug}
            if include_subchannels:
                lookup = {'channel__long_slug__contains': channel_slug}
            active_videos = active_videos.filter(
                **lookup
            ).distinct()
        active_videos = active_videos[:number]
        active_multimedias.extend(active_videos)
    return active_multimedias
