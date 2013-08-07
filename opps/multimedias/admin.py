from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.html import escape

from .models import (MediaHost, Audio, Video, MediaBox, MediaBoxAudios,
                     MediaBoxVideos, MediaConfig)
from .forms import VideoAdminForm, AudioAdminForm
from opps.core.admin import PublishableAdmin
from opps.core.admin import apply_opps_rules
from opps.articles.admin import ArticleAdmin


@apply_opps_rules('multimedias')
class MediaAdmin(ArticleAdmin):
    add_form_template = 'admin/change_form.html'
    change_form_template = 'multimedias/admin/change_form.html'

    readonly_fields = ArticleAdmin.readonly_fields[:]
    readonly_fields += ['published', 'date_available']

    change_readonly_fields = ArticleAdmin.readonly_fields[:]
    change_readonly_fields += ['published', 'date_available', 'media_file']

    actions = ArticleAdmin.actions[:]
    actions += ['resend_uolmais', ]

    fieldsets = (
        (_(u'Identification'), {
            'fields': ('site', 'title', 'slug', 'get_http_absolute_url',
                       'short_url', ('main_image', 'image_thumb'))}),
        (_(u'Content'), {
            'fields': ('short_title', 'hat',
                       'headline', 'media_file', 'tags')}),
        (_(u'Relationships'), {
            'fields': ('channel', )}),
        (_(u'Publication'), {
            'classes': ('extrapretty'),
            'fields': ('published', 'date_available',
                       'show_on_root_channel')}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.change_readonly_fields
        return self.readonly_fields

    def resend_uolmais(self, request, queryset):
        for media in queryset.select_related('uolmais'):
            media.uolmais.host_id = None
            media.uolmais.url = None
            media.uolmais.embed = ''
            media.uolmais.status = MediaHost.STATUS_NOT_UPLOADED
            media.uolmais.status_message = ''
            media.uolmais.save()

            media.published = False
            media.save()
    resend_uolmais.short_description = _("Resend UOLMais media")


@apply_opps_rules('multimedias')
class VideoAdmin(MediaAdmin):
    form = VideoAdminForm
    actions = MediaAdmin.actions[:]
    actions += ['resend_youtube', ]

    def get_list_display(self, request):
        list_display = self.list_display
        pop = request.GET.get('pop')
        if pop == 'oppseditor':
            list_display = ['opps_editor_select'] + list(list_display)
        return list_display

    def opps_editor_select(self, obj):
        return u'''
        <a href="#" onclick="window.parent.tinymce.activeEditor.selection.setContent('{0}');window.parent.tinymce.activeEditor.windowManager.close(window);">{1}</a>
        '''.format(escape(obj.uolmais.embed) ,'Select')
    opps_editor_select.short_description = _(u'Select')
    opps_editor_select.allow_tags = True

    def resend_youtube(self, request, queryset):
        for media in queryset.select_related('youtube'):
            media.youtube.host_id = None
            media.youtube.url = None
            media.youtube.embed = ''
            media.youtube.status = MediaHost.STATUS_NOT_UPLOADED
            media.youtube.status_message = ''
            media.youtube.save()
    resend_youtube.short_description = _("Resend Youtube video")


@apply_opps_rules('multimedias')
class AudioAdmin(MediaAdmin):
    form = AudioAdminForm


#OPPS RELATIONS
class MediaBoxAudiosInline(admin.TabularInline):
    model = MediaBoxAudios
    fk_name = 'mediabox'
    raw_id_fields = ['audio']
    actions = None
    extra = 1
    fieldsets = [(None, {
        'classes': ('collapse',),
        'fields': ('audio', 'order', 'date_available', 'date_end')})]


class MediaBoxVideosInline(admin.TabularInline):
    model = MediaBoxVideos
    fk_name = 'mediabox'
    raw_id_fields = ['video']
    actions = None
    extra = 1
    fieldsets = [(None, {
        'classes': ('collapse',),
        'fields': ('video', 'order', 'date_available', 'date_end')})]


class MediaBoxAdmin(PublishableAdmin):
    prepopulated_fields = {"slug": ["name"]}
    list_display = ['name', 'date_available', 'published']
    list_filter = ['date_available', 'published']
    inlines = [MediaBoxVideosInline, MediaBoxAudiosInline]
    exclude = ('user',)
    raw_id_fields = ['channel', 'article']

    fieldsets = (
        (_(u'Identification'), {
            'fields': ('site', 'name', 'slug')}),
        (_(u'Relationships'), {
            'fields': (('channel', 'article'),)}),
        (_(u'Publication'), {
            'classes': ('extrapretty'),
            'fields': ('published', 'date_available')}),
    )

    def clean_ended_entries(self, request, queryset):
        now = timezone.now()
        for box in queryset:
            endedaudios = box.mediaboxaudios_mediaboxes.filter(
                date_end__lt=now
            )
            endedvideos = box.mediaboxvideos_mediaboxes.filter(
                date_end__lt=now
            )
            if endedaudios:
                endedaudios.delete()
            if endedvideos:
                endedvideos.delete()
    clean_ended_entries.short_description = _(u'Clean ended media')

    actions = ('clean_ended_entries',)


class MediaConfigAdmin(PublishableAdmin):
    list_display = ['key', 'key_group', 'channel', 'date_insert',
                    'date_available', 'published']
    list_filter = ["key", 'key_group', "channel", "published"]
    search_fields = ["key", "key_group", "value"]
    raw_id_fields = ['audio', 'video', 'channel', 'article']
    exclude = ('user',)


admin.site.register(Video, VideoAdmin)
admin.site.register(Audio, AudioAdmin)
admin.site.register(MediaBox, MediaBoxAdmin)
admin.site.register(MediaConfig, MediaConfigAdmin)
