import logging

from six.moves import UserDict
from six.moves.urllib.request import getproxies

from scrapy_httpproxy import get_proxy
from scrapy_httpproxy.storage import BaseStorage

logger = logging.getLogger(__name__)


class EnvironmentStorage(UserDict, BaseStorage):
    def __init__(self, settings):
        super(EnvironmentStorage, self).__init__()
        self.settings = settings
        self.auth_encoding = settings.get('HTTPPROXY_AUTH_ENCODING')

    def open_spider(self, spider):
        logger.info('%s for httpproxy is used.',
                    self.settings['HTTPPROXY_STORAGE'])
        for type_, url in getproxies().items():
            self[type_] = get_proxy(url, type_, self.auth_encoding)

    def close_spider(self, spider):
        pass
