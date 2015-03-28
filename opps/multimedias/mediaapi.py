# -*- coding:utf-8 -*-
import re
import logging
from os import path
import subprocess as sp
from datetime import time
from exceptions import NotImplementedError

import pytz
import gdata.youtube.service
import vimeo
from gdata.service import BadAuthentication, RequestError

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.core.files import File
from .conf import settings

from .models import MediaHost


# Get an instance of a logger
logger = logging.getLogger(__name__)


DEFAULT_TAGS = getattr(settings, 'OPPS_MULTIMEDIAS_DEFAULT_TAGS', [])
LOCAL_VIDEO_FORMATS = getattr(settings,
                              'OPPS_MULTIMEDIAS_LOCAL_VIDEO_FORMATS')
LOCAL_AUDIO_FORMATS = getattr(settings,
                              'OPPS_MULTIMEDIAS_LOCAL_AUDIO_FORMATS')
LOCAL_TEMP_DIR = getattr(settings, 'OPPS_MULTIMEDIAS_LOCAL_TEMP_DIR')


class MediaAPIError(Exception):
    pass


class MediaAPI(object):
    def __init__(self, mediahost):
        if not isinstance(mediahost, MediaHost):
            raise MediaAPIError('{0} is not MediaHost object'.format(
                mediahost))

        if not self.name == mediahost.host:
            raise MediaAPIError('{0} is not {1} instance'.format(
                mediahost, self.name()))

        self.mediahost = mediahost

    @property
    def name(self):
        return self.__NAME__

    def authenticate(self):
        raise NotImplementedError()

    def video_upload(self, *args, **kwargs):
        return self.upload('video', *args, **kwargs)

    def audio_upload(self, *args, **kwargs):
        return self.upload('audio', *args, **kwargs)

    def upload(self, type, *args, **kwargs):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()

    def get_info(self, media_id=None):
        return dict.fromkeys([u'id', u'title', u'description', u'thumbnail',
                              u'tags', u'embed', u'url', u'status',
                              u'status_msg', u'duration'])

    def get_duration(self):
        raise NotImplementedError()


class Local(MediaAPI):
    __NAME__ = MediaHost.HOST_LOCAL

    def audio_upload(self, *args, **kwargs):
        raise NotImplementedError()

    def upload(self, type, tags=None, formats=None, force=False):
        self.tags = tags

        self.mediahost.status = MediaHost.STATUS_PROCESSING
        self.mediahost.save()

        try:
            self.process(self.mediahost, formats, force)
            self.mediahost.media.published = True
            self.mediahost.media.duration = self.get_duration()
            self.mediahost.media.save()
            return self.get_info(self.mediahost)
        except Exception as e:
            self.mediahost.status = MediaHost.STATUS_ERROR
            self.mediahost.media.published = False
            self.mediahost.status_message = str(e)[:150]
            self.mediahost.save()
            raise e

    def process(self, mediahost, formats=None, force=False):
        """
        Process formats declared on config file

        Keyword Args:
            mediahost - Instance of model opps.multimedias.Video
            formats - List of formats do process
            force - Forces to re-process selected formats

        Returns
            None
        """

        media = mediahost.media
        media_file = media.media_file

        if media.TYPE == 'video':
            available_formats = LOCAL_VIDEO_FORMATS
        elif media.TYPE == 'audio':
            available_formats = LOCAL_AUDIO_FORMATS
        else:
            raise Exception('Invalid media type: {}'.format(media.TYPE))

        for i, cnf in available_formats.items():
            if formats and i not in formats:
                continue

            model_field = 'ffmpeg_file_{}'.format(i)

            if getattr(media, model_field) and not force:
                continue

            # ex. /tmp/<media.id>-<format>.<ext>
            tmp_to = path.join(
                LOCAL_TEMP_DIR, "{}-{}.{}".format(media.id, i, cnf['ext']))

            data = {
                'from': media_file.path,
                'to': tmp_to,
                'exec': settings.OPPS_MULTIMEDIAS_FFMPEG, }
            cmd = cnf['cmd'].format(**data)

            output = sp.check_output(cmd, shell=True)

            with open(tmp_to, 'rb') as f:
                if hasattr(media, model_field):
                    setattr(media, model_field, File(f))
                    media.save()

    def get_url(self, mediahost):
        fields = ['ffmpeg_file_ogv', 'ffmpeg_file_flv', 'ffmpeg_file_mp4_sd',
                  'ffmpeg_file_mp4_hd', 'ffmpeg_file_mp3_128']
        url = ''
        for name in fields:
            field = getattr(mediahost.media, name)
            if field:
                url = field.url
        return url

    def get_info(self, mediahost):
        tags = self.tags or [] + DEFAULT_TAGS
        url = self.get_url(mediahost)

        mediahost.status = u'ok'
        mediahost.url = url

        embed_template = 'multimedias/{}_embed.html'.format(
                                                        mediahost.media.TYPE)
        embed_context = {
            'url': url,
            'mediahost': mediahost
        }
        mediahost.embed = render_to_string(embed_template, embed_context)
        mediahost.updated = True
        mediahost.save()

        if mediahost.media.ffmpeg_file_thumb:
            thumbnail = mediahost.media.ffmpeg_file_thumb.url
        elif mediahost.media.main_image:
            thumbnail = mediahost.media.main_image.url
        else:
            thumbnail = ''

        return {'id': mediahost.media.id,
                'title': mediahost.media.title,
                'description': mediahost.media.headline,
                'tags': u','.join(tags),
                'thumbnail': thumbnail,
                'embed': mediahost.embed,
                'url': mediahost.url,
                'status': u'ok',
                'status_msg': u'ok'}

    def get_duration(self):
        cmd = 'ffprobe -i {} -show_entries format=duration -v quiet -of '\
              'csv="p=0"'.format(self.mediahost.media.media_file.path)
        try:
            duration = int(float(sp.check_output(cmd, shell=True).strip()))
        except sp.CalledProcessError as error:
            return None

        split_time = str(timezone.timedelta(seconds=duration)).split(':')
        return time(int(split_time[0]), int(split_time[1]), int(split_time[2]))


class UOLMais(MediaAPI):
    __NAME__ = MediaHost.HOST_UOLMAIS

    SUCCESS_CODES = (10, )
    PROCESSING_CODES = (0, 1, 2, 3, 6, 11, 12, 13, 30, 31, 32, 33)
    REMOVED_CODES = (20, 21, 22, )
    ERROR_CODES = (60, 70, 71, 72, 73, 74, )

    def __init__(self, mediahost):
        super(UOLMais, self).__init__(mediahost)
        from uolmais_lib import UOLMaisLib
        self._lib = UOLMaisLib()

    def authenticate(self):
        try:
            username = settings.UOLMAIS_USERNAME
        except AttributeError:
            raise Exception(_(u'Settings UOLMAIS_USERNAME is not set'))

        try:
            password = settings.UOLMAIS_PASSWORD
        except AttributeError:
            raise Exception(_(u'Settings UOLMAIS_PASSWORD is not set'))

        self._lib.authenticate(username, password)

    def upload(self, type, media_path, title, description, tags):
        tags = tags or []
        tags += DEFAULT_TAGS

        self.authenticate()

        pub_date = timezone.now()
        if settings.USE_TZ:
            local_timezone = pytz.timezone(settings.TIME_ZONE)
            pub_date = timezone.localtime(pub_date, local_timezone)

        with open(media_path, 'rb') as f:
            media_args = {
                'f': f,
                'pub_date': pub_date,
                'title': title,
                'description': description,
                'tags': u','.join(tags),
                'visibility': self._lib.VISIBILITY_ANYONE,
                'comments': self._lib.COMMENTS_NONE,
                'is_hot': False
            }

            if type == u'video':
                media_id = self._lib.upload_video(**media_args)
            elif type == u'audio':
                media_id = self._lib.upload_audio(**media_args)

        return self.get_info(media_id)

    def get_info(self, media_id):
        self.authenticate()
        result = super(UOLMais, self).get_info(media_id)
        result['id'] = media_id

        info = self._lib.get_private_info(media_id)
        public_info = self._lib.get_public_info(media_id)

        # Public information are available only when file are fully processed
        if public_info and public_info.get('duration'):
            duration = public_info['duration'].split(':')

            if len(duration) == 3:
                hours, minutes, seconds = duration
            else:
                minutes, seconds = duration
                hours = 0

            result['duration'] = time(int(hours), int(minutes), int(seconds))

        if info['status'] in self.SUCCESS_CODES:
            # Embed for audio
            if info['mediaType'] == u'P':
                embed = render_to_string(
                    'multimedias/uolmais/audio_embed.html',
                    {'media_id': media_id}
                )
            else:
                embed = info['embedCode']

            result.update({
                u'title': info['title'],
                u'description': info['description'],
                u'thumbnail': info['thumbLarge'],
                u'tags': info['tags'],
                u'embed': embed,
                u'url': info['url'],
                u'status': u'ok',
                u'status_msg': info['status_description']
            })
        elif info['status'] in self.PROCESSING_CODES:
            result.update({
                u'status': u'processing',
                u'status_msg': info['status_description']
            })
        elif info['status'] in self.REMOVED_CODES:
            result.update({
                u'status': u'deleted',
                u'status_msg': info['status_description']
            })
        else:
            result.update({
                u'status': u'error',
                u'status_msg': info['status_description']
            })

        return result


class Youtube(MediaAPI):
    __NAME__ = MediaHost.HOST_YOUTUBE

    def __init__(self, mediahost):
        super(Youtube, self).__init__(mediahost)
        self.yt_service = gdata.youtube.service.YouTubeService()

    def authenticate(self):
        try:
            settings.YOUTUBE_AUTH_EMAIL
        except AttributeError:
            raise Exception(_(u'Settings YOUTUBE_AUTH_EMAIL is not set'))

        try:
            settings.YOUTUBE_AUTH_PASSWORD
        except AttributeError:
            raise Exception(_(u'Settings YOUTUBE_AUTH_PASSWORD is not set'))

        try:
            self.yt_service.developer_key = settings.YOUTUBE_DEVELOPER_KEY
        except AttributeError:
            raise Exception(_(u'Settings YOUTUBE_DEVELOPER_KEY is not set'))

        self.yt_service.email = settings.YOUTUBE_AUTH_EMAIL
        self.yt_service.password = settings.YOUTUBE_AUTH_PASSWORD

        try:
            self.yt_service.ProgrammaticLogin()
        except BadAuthentication:
            raise Exception(_(u'Incorrect Youtube username or password'))
        except:
            # TODO: logging.warning()
            pass  # Silently pass when 403 code is raised

        # Turn on HTTPS/SSL access.
        # Note: SSL is not available at this time for uploads.
        self.yt_service.ssl = False

    def upload(self, type, media_path, title, description, tags):
        tags = tags or []

        self.authenticate()

        # prepare a media group object to hold our video's meta-data
        my_media_group = gdata.media.Group(
            title=gdata.media.Title(text=title),
            description=gdata.media.Description(description_type='plain',
                                                text=description),
            category=[gdata.media.Category(
                text=u'Entertainment',
                scheme=u'http://gdata.youtube.com/schemas/2007/categories.cat',
                label=u'Entertainment')],
            keywords=gdata.media.Keywords(text=','.join(tags)),
            # private=gdata.media.Private(),
        )

        video_entry = gdata.youtube.YouTubeVideoEntry(media=my_media_group)
        video_entry = self.yt_service.InsertVideoEntry(video_entry, media_path)
        return self._get_info(video_entry)

    def _get_video_status(self, video_entry):
        status = self.yt_service.CheckUploadStatus(video_entry)

        if status is None:
            return 'ok', None

        return 'error', status[1]

    def _get_video_embed(self, video_id):
        return render_to_string('multimedias/youtube/video_embed.html',
                                {'video_id': video_id})

    def _get_info(self, video_entry):
        result = {}
        if video_entry:
            video_id = video_entry.id.text.split('/')[-1]
            result.update({
                u'id': video_id,
                u'title': video_entry.media.title.text,
                u'description': video_entry.media.description.text,
                u'thumbnail': video_entry.media.thumbnail[-1].url,
                u'tags': video_entry.media.keywords.text,
                u'embed': self._get_video_embed(video_id),
                u'url': video_entry.media.player.url,
            })

            (result['status'],
             result['status_msg']) = self._get_video_status(video_entry)

        return result

    def get_info(self, video_id):
        self.authenticate()
        result = super(Youtube, self).get_info(video_id)
        result['id'] = video_id

        try:
            video_entry = self.yt_service.GetYouTubeVideoEntry(
                video_id=video_id
            )
        except RequestError as reqerr:
            if reqerr.args[0].get('reason') == u'Not Found':
                result.update({'status': u'deleted'})
            else:
                result.update({'status': u'error'})
        else:
            result.update(self._get_info(video_entry))
        return result


class Vimeo(MediaAPI):
    __NAME__ = MediaHost.HOST_VIMEO

    SUCCESS_CODES = ('available', )
    PROCESSING_CODES = ('uploading', 'transcoding', )
    ERROR_CODES = ('uploading_error', 'transcoding_error', )

    @staticmethod
    def video_uri(id):
        return u'/videos/{id}'.format(id=id)

    @staticmethod
    def video_id(uri):
        try:
            return re.findall('^/videos/([0-9]+)', uri)[0]
        except IndexError:
            return None

    def __init__(self, mediahost):
        super(Vimeo, self).__init__(mediahost)
        self.api = vimeo.VimeoClient(key=settings.VIMEO_API_KEY,
                                     secret=settings.VIMEO_API_SECRET,
                                     token=settings.VIMEO_USER_TOKEN)

    def embed(self, width=420, height=315):
        return render_to_string('multimedias/vimeo/video_embed.html', {
            'video_id': self.mediahost.host_id,
            'width': width, 'height': height})

    def upload(self, *args, **kwargs):
        if not self.mediahost.status == MediaHost.STATUS_NOT_UPLOADED:
            raise MediaAPIError('This MediaHost has been processed')

        self.mediahost.status = MediaHost.STATUS_SENDING
        self.mediahost.status_msg = ''
        self.mediahost.save()

        try:
            media_path = self.mediahost.media.media_file.path
            if not path.exists(media_path):
                raise MediaAPIError('Source file {0} not found.'.format(
                    media_path))

            # Upload a video.
            video_uri = self.api.upload(media_path)
        except Exception as e:
            self.mediahost.status = MediaHost.STATUS_ERROR
            self.mediahost.status_msg = str(e)[:150]
            logger.exception(e.message)
        else:
            self.mediahost.host_id = self.video_id(video_uri)
            self.mediahost.status = MediaHost.STATUS_PROCESSING
            self.mediahost.status_msg = ''
        finally:
            self.mediahost.save()

        if self.mediahost.status == MediaHost.STATUS_PROCESSING:
            self.update()

        return self.get_info()

    def update(self, *args, **kwargs):
        media = self.mediahost.media
        data = {
            'name': media.title,
            'description': media.headline}
        res = self.api.patch(self.video_uri(self.mediahost.host_id), data=data)

        assert res.status_code == 200, '[{0}] {1}'.format(
            res.status_code, res.json().get('error'))

    def delete(self, *args, **kwargs):
        response = self.api.delete(self.video_uri(self.mediahost.host_id))

        if response.status_code != 204:
            raise MediaAPIError(
                'Ocoured an error on delete video [{0}] {1}'.format(
                    response.status_code, response.content))

    def get_info(self, *args, **kwargs):
        media_id = self.mediahost.host_id

        media_uri = self.video_uri(media_id)
        media_info = self.api.get(media_uri)
        content = media_info.json()

        if media_info.status_code == 200:
            data = {
                u'id': media_id,
                u'title': content.get('name'),
                u'description': content.get('description'),
                u'tags': u'',
                u'embed': self.embed(),
                u'url': content.get('link')}

            if content.get('pictures') and content['pictures']['active']:
                data.update({
                    u'thumbnail': content['pictures']['sizes'][-1]['link']})

            if content.get('status') in self.SUCCESS_CODES:
                data.update({
                    u'status': MediaHost.STATUS_OK,
                    u'status_msg': ''})
            elif content.get('status') in self.PROCESSING_CODES:
                data.update({
                    u'status': MediaHost.STATUS_PROCESSING,
                    u'status_msg': ''})
            else:
                data.update({
                    u'status': MediaHost.STATUS_ERROR,
                    u'status_msg':
                    u'Occurred an error on video processing ({0} - {1})'
                    ''.format(
                        content.get('status'), content.get('error'))})
            return data

        if media_info.status_code == 404:
            return {
                u'status': MediaHost.STATUS_DELETED,
                u'status_msg': content.get('error')}

        return {
            u'status': MediaHost.STATUS_ERROR,
            u'status_msg': '[{0}] {1}'.format(
                media_info.status_code, media_info.content)}
