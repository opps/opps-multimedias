#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.utils import timezone

from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization
from tastypie.constants import ALL

from opps.api import MetaBase

from .models import Audio as AudioModel
from .models import Video as VideoModel


class Audio(ModelResource):
    class Meta(MetaBase):
        queryset = AudioModel.objects.filter(
            published=True,
            date_available__lte=timezone.now()
        )


class Video(ModelResource):
    class Meta(MetaBase):
        queryset = VideoModel.objects.filter(
            published=True,
            date_available__lte=timezone.now()
        )
