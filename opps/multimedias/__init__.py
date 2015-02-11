
import pkg_resources

pkg_resources.declare_namespace(__name__)

VERSION = (0, 5, 0)

__version__ = ".".join(map(str, VERSION))
__status__ = "Development"
__description__ = u"Multimedia App for Opps CMS"

__author__ = u"Sergio Oliveira"
__credits__ = ['Jean Rodrigues']
__email__ = u"sergio@tracy.com.br"
__copyright__ = u"Copyright 2014, Opps Project"
