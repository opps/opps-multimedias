# -*- coding:utf-8 -*-

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
        raise NotImplementedError()


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
        self.authenticate()
        return self._lib.upload_video(
            f=open(video_path, 'rb'),
            pub_date=timezone.now(),
            title=title,
            description=description,
            tags=tags,
            visibility=UOLMaisLib.VISIBILITY_ANYONE,
            comments=UOLMaisLib.COMMENTS_NONE,
            is_hot=False
        )

    def get_info(self, video_id):
        info = self._lib.get_by_id(video_id)
        if info:
            tags = u','.join([tag['description'] for tag in info['tags']])
            return {
                u'id': video_id,
                u'title': info['title'],
                u'description': info['description'],
                u'thumbnail': info['thumbLarge'],
                u'tags': tags,
                u'embed': info['embedCode'],
                u'url': info['url']
            }
        else:
            return None
