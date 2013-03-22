
import ffvideo

from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from opps.article.admin import ArticleAdmin

from .models import Video


class VideoAdminForm(forms.ModelForm):
    class Meta:
        model = Video

    def clean_video_file(self):
        video_file = self.cleaned_data['video_file']
        try:
            vs = ffvideo.VideoStream(video_file.temporary_file_path())
        except ffvideo.DecoderError:
            raise forms.ValidationError(_('Invalid video format'))
        return video_file

    def clean(self):
        video_file = self.cleaned_data.get('video_file')
        if video_file:
            vs = ffvideo.VideoStream(video_file.temporary_file_path())
            self.cleaned_data['length'] = int(vs.duration)
        return self.cleaned_data

class VideoAdmin(ArticleAdmin):
    form = VideoAdminForm

    fieldsets = (
        (_(u'Identification'), {
            'fields': ('title', 'slug', 'get_absolute_url', 'short_url',)}),
        (_(u'Content'), {
            'fields': ('short_title', 'headline', 'video_file', 'main_image')}),
        (_(u'Metadata'), {
            'fields': ('length', 'host')}),
        (_(u'Relationships'), {
            'fields': ('channel',)}),
        (_(u'Publication'), {
            'classes': ('extrapretty'),
            'fields': ('published', 'date_available')}),
    )

admin.site.register(Video, VideoAdmin)

