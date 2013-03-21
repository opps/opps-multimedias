from django.db import models
from django.utils.translation import ugettext_lazy as _

from opps.article.models import Article

class Video(Article):
    length = models.PositiveIntegerField(_(u'Length'))
    name = models.CharField(_(u'Name'), max_length='255')
