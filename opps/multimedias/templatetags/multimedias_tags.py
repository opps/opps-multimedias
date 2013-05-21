# -*- coding: utf-8 -*-

from django import template
from opps.multimedias.models import Audio, Video
from opps.core.templatetags.box_tags import get_box, get_all_box


register = template.Library()


@register.simple_tag
def get_active_multimedias(number=5, channel_slug=None,
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

    return t.render(template.Context({'active_multimedias': active_multimedias,
                                      'channel_slug': channel_slug,
                                      'number': number}))


@register.simple_tag
def get_mediabox(slug, template_name=None):
    return get_box('multimedias', slug, template_name)


@register.simple_tag
def get_all_mediabox(channel_slug, template_name=None):
    return get_all_box('multimedias', channel_slug, template_name)
