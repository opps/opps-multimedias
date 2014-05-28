#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tempfile import gettempdir

from django.conf import settings
from appconf import AppConf


TEMP_DIR = gettempdir() or '/tmp'


class OppsMultimediasConf(AppConf):
    VIDEO_CHANNEL = getattr(
        settings, 'OPPS_MULTIMEDIAS_VIDEO_CHANNEL', 'videos')

    AUDIO_CHANNEL = getattr(
        settings, 'OPPS_MULTIMEDIAS_AUDIO_CHANNEL', 'audios')

    ENGINES = getattr(
        settings, 'OPPS_MULTIMEDIAS_ENGINES', [u'local'])

    FFMPEG = getattr(settings, 'OPPS_MULTIMEDIAS_FFMPEG', '/usr/bin/ffmpeg')

    LOCAL_TEMP_DIR = getattr(
        settings, 'OPPS_MULTIMEDIAS_LOCAL_TEMP_DIR', TEMP_DIR)

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
                "cmd": "{exec} -i {from} -codec:v libx264 -profile:v main "
                       "-preset slow -b:v 500k -maxrate 500k -bufsize 1000k "
                       "-vf scale=-1:480 -threads 0 -b:a 128k -f mp4 -y {to}",
                "ext": "mp4",
            },
            "mp4_hd": {
                "quality": "720p",
                "cmd": "{exec} -i {from} -codec:v libx264 -profile:v main "
                       "-preset slow -b:v 1000k -maxrate 1000k -bufsize 2000k "
                       "-vf scale=-1:480 -threads 0 -b:a 196k -f mp4 -y {to}",
                "ext": "mp4",
            },
            #"ogv": {
            #    "quality": "720p",
            #    "cmd": "{exec} -i {from} -acodec libvorbis -vcodec libtheora "
            #           "-f ogv {to}",
            #    "ext": "ogv",
            #},
            "thumb": {
                "cmd": "{exec} -i {from} -an -ss 00:00:03 -an -r 1 -vframes 1 "
                       "{to}",
                "ext": "jpg",
            },
        })

    class Meta:
        prefix = 'opps_multimedias'
