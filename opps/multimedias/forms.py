# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from opps.core.widgets import OppsEditor
from opps.containers.forms import ContainerAdminForm

from .models import Audio, Video, MediaHost


class MediaAdminForm(ContainerAdminForm):
    ALLOWED_EXTENSIONS = ()

    def __init__(self, *args, **kwargs):
        super(MediaAdminForm, self).__init__(*args, **kwargs)
        self.fields['headline'].required = False

    def clean_media_file(self):
        media_file = self.cleaned_data['media_file']
        if media_file:
            extension = media_file.name.split('.')[-1].upper()
            if extension not in self.ALLOWED_EXTENSIONS:
                raise forms.ValidationError(_(u'Invalid extension'))
        return media_file


class VideoAdminForm(MediaAdminForm):
    ALLOWED_EXTENSIONS = ('AVI', 'DIVX', 'DV', 'MOV', 'QT', 'MPEG', 'MPG',
                          'MP4', 'ASF', 'WMV', 'FLV')

    def __init__(self, *args, **kwargs):
        super(VideoAdminForm, self).__init__(*args, **kwargs)
        if self.instance.uolmais:
            if self.instance.uolmais == MediaHost.STATUS_OK:
                self.fields['media_file'].required = False
        else:
            self.fields['media_file'].required = True

    class Meta:
        model = Video

        if not settings.OPPS_MULTIMEDIAS_USE_CONTENT_FIELD:
            exclude = ['content']
        else:
            widgets = {'content': OppsEditor()}


class AudioAdminForm(MediaAdminForm):
    ALLOWED_EXTENSIONS = ('MP3', 'WMA', 'WAV', 'AAC')

    class Meta:
        model = Audio

        if not settings.OPPS_MULTIMEDIAS_USE_CONTENT_FIELD:
            exclude = ['content']
        else:
            widgets = {'content': OppsEditor()}
