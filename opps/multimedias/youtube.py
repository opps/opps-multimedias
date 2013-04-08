
import gdata.youtube.service

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from gdata.service import BadAuthentication


class VideoEntryNotAvailable(Exception):
    pass


class Youtube(object):

    def __init__(self, video):
        self.yt_service = gdata.youtube.service.YouTubeService()
        self.yt_service.email = settings.YOUTUBE_AUTH_EMAIL
        self.yt_service.password = settings.YOUTUBE_AUTH_PASSWORD
        self.video = video
        self._video_entry = None

        try:
            self.yt_service.ProgrammaticLogin()
        except BadAuthentication:
            raise Exception(_('Incorrect Youtube username or password'))

        try:
            self.yt_service.developer_key = settings.YOUTUBE_DEVELOPER_KEY
        except AttributeError:
            raise Exception(_('Settings YOUTUBE_DEVELOPER_KEY is not set'))

        # Turn on HTTPS/SSL access.
        # Note: SSL is not available at this time for uploads.
        self.yt_service.ssl = False

    def upload(self):
        # prepare a media group object to hold our video's meta-data
        my_media_group = gdata.media.Group(
            title=gdata.media.Title(text=self.video.title),
            description=gdata.media.Description(description_type='plain',
                                                text=self.video.headline),
            category=[gdata.media.Category(
                text='Entertainment',
                scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
                label='Entertainment')],
            #private=gdata.media.Private(),
            #keywords=gdata.media.Keywords(text=','.join(keywords)),
        )

        video_entry = gdata.youtube.YouTubeVideoEntry(media=my_media_group)
        return self.yt_service.InsertVideoEntry(video_entry,
                                                self.video.video_file.path)

    @property
    def video_entry(self):
        if not self._video_entry and self.video.host_id:
            self._video_entry = self.yt_service.GetYouTubeVideoEntry(
                                                video_id=self.video.host_id)

        if not self._video_entry:
            raise VideoEntryNotAvailable()

        return self._video_entry

    def publish(self):
        """Youtube API does not work for updates"""
        #self.yt_service.UpdateVideoEntry(self.video_entry)
        #self.video_entry.media.extension_elements = None
        pass

    def unpublish(self):
        """Youtube API does not work for updates"""
        #self.video_entry.media.extension_elements = None
        #self.yt_service.UpdateVideoEntry(self.video_entry)
        pass
