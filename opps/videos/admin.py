
import ffvideo

from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.files import FieldFile

from opps.articles.admin import ArticleAdmin

from .models import Video, VideoHost


class VideoAdminForm(forms.ModelForm):
    class Meta:
        model = Video

    def _get_video_path(self):
        video_file = self.cleaned_data.get('video_file')
        if not video_file:
            return

        if isinstance(video_file, FieldFile):
            return video_file.path

        return video_file.temporary_file_path()

    def clean_video_file(self):
        video_file = self.cleaned_data['video_file']
        try:
            vs = ffvideo.VideoStream(self._get_video_path())
        except ffvideo.DecoderError:
            raise forms.ValidationError(_('Invalid video format'))
        return video_file


class VideoAdmin(ArticleAdmin):
    form = VideoAdminForm
    add_form_template = 'admin/change_form.html'
    change_form_template = 'videos/admin/change_form.html'

    fieldsets = (
        (_(u'Identification'), {
            'fields': ('site', 'title', 'slug', 'get_http_absolute_url',
                       'short_url')}),
        (_(u'Content'), {
            'fields': ('short_title', 'headline', 'video_file')}),
        (_(u'Relationships'), {
            'fields': ('channel', )}),
        (_(u'Publication'), {
            'classes': ('extrapretty'),
            'fields': ('published', 'date_available')}),
    )

admin.site.register(Video, VideoAdmin)
