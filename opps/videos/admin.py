
import ffvideo

from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.files import FieldFile
from djcelery.models import (TaskState, WorkerState,
                 PeriodicTask, IntervalSchedule, CrontabSchedule)
from opps.article.admin import ArticleAdmin

from .models import Video


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

    def clean(self):
        video_path = self._get_video_path()
        if video_path:
            vs = ffvideo.VideoStream(video_path)
            self.cleaned_data['length'] = int(vs.duration)
        return self.cleaned_data


class VideoAdmin(ArticleAdmin):
    form = VideoAdminForm
    change_form_template = 'videos/admin/change_form.html'

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

    def change_view(self, request, object_id, form_url='', extra_context=None):
        video = Video.objects.get(pk=object_id)

        extra_context = extra_context or {}
        extra_context['upload_status'] = video.celery_result.status

        return super(VideoAdmin, self).change_view(request, object_id,
            form_url, extra_context=extra_context)

admin.site.register(Video, VideoAdmin)


# Removes celery from django admin
admin.site.unregister(TaskState)
admin.site.unregister(WorkerState)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(PeriodicTask)

