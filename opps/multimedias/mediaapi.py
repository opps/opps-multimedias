# -*- coding:utf-8 -*-
import pytz
import gdata.youtube.service
from os import system

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django.core.files import File

from gdata.service import BadAuthentication, RequestError


DEFAULT_TAGS = getattr(settings, 'OPPS_MULTIMEDIAS_DEFAULT_TAGS', [])


class MediaAPIError(Exception):
    pass


class MediaAPI(object):
    def authenticate(self):
        raise NotImplementedError()

    def upload(self, type, media_path, title, description, tags):
        raise NotImplementedError()

    def delete(self, media_id):
        raise NotImpLementedError()

    def get_info(self, media_id):
        return dict.fromkeys([u'id', u'title', u'description', u'thumbnail',
                              u'tags', u'embed', u'url', u'status',
                              u'status_msg'])


class Local(MediaAPI):

    def __init__(self):
        super(Local, self).__init__()

    def video_upload(self, *args, **kwargs):
        return self.upload('video', *args, **kwargs)

    def audio_upload(self, *args, **kwargs):
        raise NotImplementedError()

    def upload(self, mediahost, tags):
        self.tags = tags

        mediahost.status = u'processing'
        mediahost.save()

        # MP4 to FLV
        cmd = "ffmpeg -i {0} -acodec libmp3lame -ac 2 -ar 11025 "\
            "-vcodec libx264 -r 15 -s 720x400 -aspect 720:400 -sn -f {2} -y "\
            "/tmp/{1}.{2}".format(mediahost.media.media_file.path,
                                  mediahost.media.id,
                                  "flv")
        system(cmd)
        with open("/tmp/{}.flv".format(mediahost.media.id), 'rb') as f:
            mediahost.media.ffmpeg_file_flv = File(f)
            mediahost.media.save()

        # MP4 to OGG
        try:
            cmd = "ffmpeg -i {0} -acodec libvorbis -vcodec libtheora -f {2} "\
                "/tmp/{1}.{2}".format(mediahost.media.media_file.path,
                                      mediahost.media.id,
                                      'ogv')
            with open("/tmp/{}.ogv".format(mediahost.media.id), 'rb') as f:
                mediahost.media.ffmpeg_file_ogv = File(f)
                mediahost.media.save()
        except:
            pass

        # Generate thumb
        try:
            cmd = "ffmpeg -i /tmp/{}.flv -an -ss 00:00:03 -an -r 1 -vframes "\
                "1 -y /tmp/{}.jpg".format(mediahost.medid.id)
            system(cmd)
            with open("/tmp/{}.jpg".format(mediahost.media.id),
                      'rb') as img:
                mediahost.media.ffmpeg_file_thumb = File(img)
                mediahost.media.save()
        except:
            pass

        mediahost.media.published = True
        mediahost.media.save()

        return self.get_info(mediahost)

    def get_info(self, mediahost):
        tags = self.tags or [] + DEFAULT_TAGS

        mediahost.status = u'ok'
        mediahost.url = u'{}{}'.format(settings.STATIC_URL[:-1],
                                       mediahost.media.ffmpeg_file_flv.url)
        mediahost.embed = render_to_string(
            'multimedias/video_embed.html',
            {'url': mediahost.media.ffmpeg_file_flv})
        mediahost.updated = True
        mediahost.save()

        return {'id': mediahost.media.id,
                'title': mediahost.media.title,
                'description': mediahost.media.headline,
                'tags': u','.join(tags),
                'thumbnail': mediahost.media.ffmpeg_file_thumb.url,
                'embed': mediahost.embed,
                'url': mediahost.url,
                'status': u'ok',
                'status_msg': u'ok'}


class UOLMais(MediaAPI):

    SUCCESS_CODES = (10, )
    PROCESSING_CODES = (0, 1, 2, 3, 6, 11, 12, 13, 30, 31, 32, 33)
    REMOVED_CODES = (20, 21, 22, )
    ERROR_CODES = (60, 70, 71, 72, 73, 74, )

    def __init__(self):
        super(UOLMais, self).__init__()
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

    def video_upload(self, *args, **kwargs):
        return self.upload('video', *args, **kwargs)

    def audio_upload(self, *args, **kwargs):
        return self.upload('audio', *args, **kwargs)

    def upload(self, type, media_path, title, description, tags):
        tags = tags or []
        tags += DEFAULT_TAGS

        self.authenticate()

        saopaulo_tz = pytz.timezone('America/Sao_Paulo')
        with open(media_path, 'rb') as f:
            media_args = {
                'f': f,
                'pub_date': timezone.localtime(timezone.now(), saopaulo_tz),
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

    def __init__(self):
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
            #private=gdata.media.Private(),
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
