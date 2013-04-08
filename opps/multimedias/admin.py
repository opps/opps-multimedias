
import ffvideo

from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.files import FieldFile

from opps.articles.admin import ArticleAdmin

from .models import Video, MediaHost


class MediaAdminForm(forms.ModelForm):

    headline = forms.CharField(_(u"Headline"), widget=forms.Textarea,
                               required=True)

    def _get_media_path(self):
        media_file = self.cleaned_data.get('media_file')
        if not media_file:
            return

        if isinstance(media_file, FieldFile):
            return media_file.path

        return media_file.temporary_file_path()


class VideoAdminForm(MediaAdminForm):
    class Meta:
        model = Video

    def clean_media_file(self):
        media_file = self.cleaned_data['media_file']
        try:
            vs = ffvideo.VideoStream(self._get_media_path())
        except ffvideo.DecoderError:
            raise forms.ValidationError(_('Invalid media format'))
        return media_file


class MediaAdmin(ArticleAdmin):
    add_form_template = 'admin/change_form.html'
    change_form_template = 'multimedias/admin/change_form.html'
    readonly_fields = ArticleAdmin.readonly_fields[:]
    readonly_fields += ['published', 'date_available']

    fieldsets = (
        (_(u'Identification'), {
            'fields': ('site', 'title', 'slug', 'get_http_absolute_url',
                       'short_url')}),
        (_(u'Content'), {
            'fields': ('short_title', 'headline', 'media_file')}),
        (_(u'Relationships'), {
            'fields': ('channel', )}),
        (_(u'Publication'), {
            'classes': ('extrapretty'),
            'fields': ('published', 'date_available')}),
    )


class VideoAdmin(MediaAdmin):
    form = VideoAdminForm


admin.site.register(Video, VideoAdmin)
