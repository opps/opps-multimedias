from django.db import models
from django.utils.translation import ugettext_lazy as _

from opps.article.models import Article

class Video(Article):

    HOST_YOUTUBE = 'youtube'
    HOST_UOLMAIS = 'uolmais'
    HOST_CHOICES = (
        (HOST_YOUTUBE, 'Youtube'),
        (HOST_UOLMAIS, 'UOL Mais'),
    )

    length = models.PositiveIntegerField(_(u'Length'),
                                         help_text=_('Video lenght in seconds'))
    name = models.CharField(_(u'Name'), max_length='255')
    video_file = models.FileField(_(u'Video File'), upload_to='videos',
                                  help_text=_(('Temporary file stored '
                                               'until it\'s not sent to '
                                               'final hosting server '
                                               '(ie: Youtube)')))
    host = models.CharField(_('Host'), max_length=16, choices=HOST_CHOICES,
                            default=HOST_UOLMAIS,
                            help_text=_('Provider that will store the video'))
