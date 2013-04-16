# -*- coding: utf-8 -*-

from opps.multimedias.models import Video, Audio
from opps.articles.views.generic import OppsDetail, OppsList


class VideoDetail(OppsDetail):
    model = Video
    type = 'multimedias'


class AudioDetail(OppsDetail):
    model = Audio
    type = 'multimedias'
