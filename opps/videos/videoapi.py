# -*- coding:utf-8 -*-


class VideoAPIError(exception):
    pass


class VideoAPI(object):

    def __init__(self):
        self.authenticate()

    def authenticate(self):
        raise NotImplementedError()

    def upload(self, video_path, title, description, tags):
        raise NotImplementedError()

    def delete(self, video_id):
        raise NotImplementedError()

    def get_info(self, video_id):
        raise NotImplementedError()
