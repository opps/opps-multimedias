# -*- coding:utf-8 -*-

import pytz
import gdata.youtube.service

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from uolmais_lib import UOLMaisLib
from gdata.service import BadAuthentication, RequestError


class VideoAPIError(Exception):
    pass


class VideoAPI(object):

    def authenticate(self):
        raise NotImplementedError()

    def upload(self, video_path, title, description, tags):
        raise NotImplementedError()

    def delete(self, video_id):
        raise NotImplementedError()

    def get_info(self, video_id):
        return dict.fromkeys([u'id', u'title', u'description', u'thumbnail',
                             u'tags', u'embed', u'url', u'status'])


class UOLMais(VideoAPI):

    def __init__(self):
        super(UOLMais, self).__init__()
        self._lib = UOLMaisLib()

    def authenticate(self):
        try:
            username = settings.UOLMAIS_USERNAME
        except AttributeError:
            raise Exception(_('Settings UOLMAIS_USERNAME is not set'))

        try:
            password = settings.UOLMAIS_PASSWORD
        except AttributeError:
            raise Exception(_('Settings UOLMAIS_PASSWORD is not set'))

        self._lib.authenticate(username, password)

    def upload(self, video_path, title, description, tags):
        tags = tags or []
        tags.append('virgula')

        self.authenticate()

        saopaulo_tz = pytz.timezone('America/Sao_Paulo')
        video_id = self._lib.upload_video(
            f=open(video_path, 'rb'),
            pub_date=timezone.localtime(timezone.now(), saopaulo_tz),
            title=title,
            description=description,
            tags=tags,
            visibility=UOLMaisLib.VISIBILITY_ANYONE,
            comments=UOLMaisLib.COMMENTS_NONE,
            is_hot=False
        )
        return self.get_info(video_id)

    def get_info(self, video_id):
        result = super(UOLMais, self).get_info(video_id)
        result['id'] = video_id

        info = self._lib.get_by_id(video_id)

        if info:
            tags = u','.join([tag['description'] for tag in info['tags']])
            result.update({
                u'title': info['title'],
                u'description': info['description'],
                u'thumbnail': info['thumbLarge'],
                u'tags': tags,
                u'embed': info['embedCode'],
                u'url': info['url']
            })
        return result


class Youtube(VideoAPI):

    def __init__(self):
        self.yt_service = gdata.youtube.service.YouTubeService()

    def authenticate(self):
        try:
            username = settings.YOUTUBE_AUTH_EMAIL
        except AttributeError:
            raise Exception(_('Settings YOUTUBE_AUTH_EMAIL is not set'))

        try:
            password = settings.YOUTUBE_AUTH_PASSWORD
        except AttributeError:
            raise Exception(_('Settings YOUTUBE_AUTH_PASSWORD is not set'))

        try:
            self.yt_service.developer_key = settings.YOUTUBE_DEVELOPER_KEY
        except AttributeError:
            raise Exception(_('Settings YOUTUBE_DEVELOPER_KEY is not set'))

        self.yt_service.email = settings.YOUTUBE_AUTH_EMAIL
        self.yt_service.password = settings.YOUTUBE_AUTH_PASSWORD

        try:
            self.yt_service.ProgrammaticLogin()
        except BadAuthentication:
            raise Exception(_('Incorrect Youtube username or password'))

        # Turn on HTTPS/SSL access.
        # Note: SSL is not available at this time for uploads.
        self.yt_service.ssl = False

    def upload(self, video_path, title, description, tags):
        tags = tags or []
        tags.append('virgula')

        self.authenticate()

        # prepare a media group object to hold our video's meta-data
        my_media_group = gdata.media.Group(
            title=gdata.media.Title(text=title),
            description=gdata.media.Description(description_type='plain',
                                                text=description),
            category=[gdata.media.Category(
                text='Entertainment',
                scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
                label='Entertainment')],
            keywords=gdata.media.Keywords(text=','.join(tags)),
            #private=gdata.media.Private(),
        )

        video_entry = gdata.youtube.YouTubeVideoEntry(media=my_media_group)
        video_entry = self.yt_service.InsertVideoEntry(video_entry, video_path)
        video_id = video_entry.id.text.split('/')[-1]

        return self.get_info(video_id)

    def get_info(self, video_id):
        result = super(Youtube, self).get_info(video_id)
        result['id'] = video_id
        result['url'] = u'http://www.youtube.com/watch?v={}'.format(video_id)

        try:
            video_entry = self.yt_service.GetYouTubeVideoEntry(video_id=video_id)
        except RequestError as reqerr:
            if reqerr.message.get('reason') == 'Forbidden':
                result.update({'status': 'forbidden'})
            elif reqerr.message.get('reason') == 'Not Found':
                result.update({'status': 'deleted'})
            else:
                result.update({'status': 'error'})
        else:
            if video_entry:
                #TODO: tags = ???
                result.update({
                #    u'title': info['title'],
                #    u'description': info['description'],
                #    u'thumbnail': info['thumbLarge'],
                #    u'tags': tags,
                #    u'embed': info['embedCode'],
                })
        return result
