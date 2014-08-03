# -*- coding: utf-8 -*-

from haystack.indexes import Indexable

from opps.containers.search_indexes import ContainerIndex

from .models import Audio, Video


class AudioIndex(ContainerIndex, Indexable):
    def get_model(self):
        return Audio


class VideoIndex(ContainerIndex, Indexable):
    def get_model(self):
        return Video
