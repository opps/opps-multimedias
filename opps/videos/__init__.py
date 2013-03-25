
import pkg_resources
from django.utils.translation import ugettext_lazy as _

pkg_resources.declare_namespace(__name__)

trans_app_label = _(u'Videos')

VERSION = (0, 1, 1)

__version__ = ".".join(map(str, VERSION))
__status__ = "Development"
__description__ = u"Videos App for Opps CMS"

__author__ = u"Sergio Oliveira"
__credits__ = []
__email__ = u"sergio@tracy.com.br"
__copyright__ = u"Copyright 2013, YACOWS"
