from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import (MediaHost, Audio, Video, MediaBox, MediaBoxAudios,
                     MediaBoxVideos, MediaConfig)


class MediaAdminForm(forms.ModelForm):
    ALLOWED_EXTENSIONS = ()

    headline = forms.CharField(
        _(u"Headline"),
        widget=forms.Textarea,
        required=True
    )

    def clean_media_file(self):
        media_file = self.cleaned_data['media_file']
        if media_file:
            extension = media_file.name.split('.')[-1].upper()
            if extension not in self.ALLOWED_EXTENSIONS:
                raise forms.ValidationError(_('Invalid extension'))
        return media_file


class VideoAdminForm(MediaAdminForm):
    ALLOWED_EXTENSIONS = ('AVI', 'DIVX', 'DV', 'MOV', 'QT', 'MPEG', 'MPG',
                          'MP4', 'ASF', 'WMV', 'FLV')

    class Meta:
        model = Video


class AudioAdminForm(MediaAdminForm):
    ALLOWED_EXTENSIONS = ('MP3', 'WMA', 'WAV', 'AAC')

    class Meta:
        model = Audio
