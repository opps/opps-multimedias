# -*- coding: utf-8 -*-

from opps.multimedias.models import Video, Audio
from opps.containers.views import ContainerDetail, ContainerList


class VideoDetail(ContainerDetail):
    model = Video
    type = 'multimedias'


class AudioDetail(ContainerDetail):
    model = Audio
    type = 'multimedias'


class VideoList(ContainerList):
    model = Video
    type = 'video'


class AudioList(ContainerList):
    model = Audio
    type = 'audio'
