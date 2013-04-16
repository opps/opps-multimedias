from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from opps.articles.admin import ArticleAdmin

from .models import Audio, Video


class MediaAdminForm(forms.ModelForm):

    headline = forms.CharField(_(u"Headline"), widget=forms.Textarea,
                               required=True)


class VideoAdminForm(MediaAdminForm):
    class Meta:
        model = Video


class AudioAdminForm(MediaAdminForm):
    class Meta:
        model = Audio


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


class AudioAdmin(MediaAdmin):
    form = AudioAdminForm


admin.site.register(Video, VideoAdmin)
admin.site.register(Audio, AudioAdmin)
