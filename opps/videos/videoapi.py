# -*- coding:utf-8 -*-

import pytz

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from uolmais_lib import UOLMaisLib


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
                             u'tags', u'embed', u'url'])


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
    pass
