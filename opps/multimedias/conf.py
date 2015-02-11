#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tempfile import gettempdir

from django.conf import settings
from appconf import AppConf


TEMP_DIR = gettempdir() or '/tmp'


class OppsMultimediasConf(AppConf):
    # Example: If you have this channel structure:
    #  videos/
    #   animals
    # And configure put opps-multimedias to serve the channels on the url
    # /videos/ the channel animals of the example will be served on url
    # /videos/videos/animals
    # This is not good, so if you are also working with a root channel that
    # has the same url/slug of OPPS_MULTIMEDIAS_VIDEO_CHANNEL like the example
    # just enable this option.

    PREPEND_AUDIO_CHANNEL = \
        getattr(settings, "OPPS_MULTIMEDIAS_PREPEND_AUDIO_CHANNEL", False)

    PREPEND_VIDEO_CHANNEL = \
        getattr(settings, "OPPS_MULTIMEDIAS_PREPEND_VIDEO_CHANNEL", False)

    VIDEO_CHANNEL = getattr(
        settings, 'OPPS_MULTIMEDIAS_VIDEO_CHANNEL', 'videos')

    AUDIO_CHANNEL = getattr(
        settings, 'OPPS_MULTIMEDIAS_AUDIO_CHANNEL', 'audios')

    ENGINES = getattr(
        settings, 'OPPS_MULTIMEDIAS_ENGINES', [u'local'])

    AUDIO_ENGINES = getattr(
        settings, 'OPPS_MULTIMEDIAS_AUDIO_ENGINES', [u'local'])

    FFMPEG = getattr(settings, 'OPPS_MULTIMEDIAS_FFMPEG', '/usr/bin/ffmpeg')

    LOCAL_TEMP_DIR = getattr(
        settings, 'OPPS_MULTIMEDIAS_LOCAL_TEMP_DIR', TEMP_DIR)

    LOCAL_MAX_PARALLEL = getattr(
        settings, 'OPPS_MULTIMEDIAS_LOCAL_MAX_PARALLEL', 1)

    UPLOAD_MEDIA_INTERVAL = getattr(
        settings, 'OPPS_MULTIMEDIAS_UPLOAD_MEDIA_INTERVAL', 5)

    UPDATE_MEDIAHOST_INTERVAL = getattr(
        settings, 'OPPS_MULTIMEDIAS_UPDATE_MEDIAHOST_INTERVAL', 2)

    LOCAL_FORMATS = getattr(
        settings, 'OPPS_MULTIMEDIAS_LOCAL_FORMATS', {
            "flv": {
                "quality": "720p",
                "cmd": "{exec} -i {from} -acodec libmp3lame -ac 2 -ar 11025 "
                       "-vcodec libx264 -r 15 -s 720x400 -aspect 720:400 "
                       "-sn -f flv -y {to}",
                "ext": "flv",
            },
            "mp4_sd": {
                "quality": "480p",
                "cmd": "{exec} -i {from} -filter:v scale=640:360,setsar=1/1 "
                       "-pix_fmt yuv420p -c:v libx264 -preset:v slow "
                       "-profile:v baseline -x264opts level=3.0:ref=1 "
                       "-b:v 500k -r:v 25/1 -force_fps -movflags +faststart "
                       "-b:a 80k -async 1 -vsync 1 -y {to}",
                "ext": "mp4",
            },
            "mp4_hd": {
                "quality": "720p",
                "cmd": "{exec} -i {from} -filter:v scale=640:360,setsar=1/1 "
                       "-pix_fmt yuv420p -c:v libx264 -preset:v slow "
                       "-profile:v baseline -x264opts level=3.0:ref=1 "
                       "-b:v 1000k -r:v 25/1 -force_fps -movflags +faststart "
                       "-b:a 128k -async 1 -vsync 1 -y {to}",
                "ext": "mp4",
            },
            "thumb": {
                "cmd": "{exec} -y -i {from} -an -ss 00:00:03 -an -r 1 "
                       "-vframes 1 {to}",
                "ext": "jpg",
            },
        })

    USE_CONTENT_FIELD = getattr(
        settings, 'OPPS_MULTIMEDIAS_USE_CONTENT_FIELD', False
    )

    class Meta:
        prefix = 'opps_multimedias'
