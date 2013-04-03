# -*- coding:utf-8 -*-


class VideoAPIError(exception):
    pass


class VideoAPI(object):

    def __init__(self, video_id=None):
        self.video_id = video_id
        self.authenticate()

    def authenticate(self):
        raise NotImplementedError()

    def upload(self, video_path, title, description, tags):
        if self.video_id:
            raise VideoAPIError('Video already uploaded')

    def delete(self):
        if not self.video_id:
            raise VideoAPIError('Video has not been found')

    def get_info(self):
        if not self.video_id:
            raise VideoAPIError('Video has not been found')
