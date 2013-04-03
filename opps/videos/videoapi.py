# -*- coding:utf-8 -*-


class VideoAPIError(exception):
    pass


class VideoAPI(object):

    def __init__(self, video_id=None):
        self.video_id = video_id
        self.authenticate()

    def authenticate(self):
        raise NotImplementedError()

    def upload(self, *args, **kwargs):
        if self.video_id:
            raise VideoAPIError('Video already uploaded')
        self.video_id = self._upload(*args, **kwargs)

    def _upload(self, video_path, title, description, tags):
        raise NotImplementedError()

    def delete(self):
        if not self.video_id:
            raise VideoAPIError('Video has not been found')
        self._delete()
        self.video_id = None

    def _delete(self):
        raise NotImplementedError()

    def get_dict(self):
        if not self.video_id:
            raise VideoAPIError('Video has not been found')
        return self._get()

    def _get(self):
        raise NotImplementedError()
