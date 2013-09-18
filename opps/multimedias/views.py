# -*- coding: utf-8 -*-
from django.contrib.sites.models import get_current_site
from django.utils import timezone
from django.conf import settings
from django.views.generic import ListView

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


class ListAll(ListView):

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
        self.site = get_current_site(self.request)

        filters = {}
        filters['site_domain'] = self.site.domain
        filters['date_available__lte'] = timezone.now()
        filters['published'] = True
        filters['show_on_root_channel'] = True
        queryset = self.model.objects.filter(**filters)

        return queryset._clone()


class AllVideoList(ListAll):
    model = Video
    type = 'video'


class AllAudioList(ListAll):
    model = Audio
    type = 'audio'
