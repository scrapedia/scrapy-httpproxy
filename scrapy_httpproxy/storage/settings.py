import logging
import re
from itertools import cycle

from six.moves import UserDict

from scrapy_httpproxy import get_proxy
from scrapy_httpproxy.storage import BaseStorage

logger = logging.getLogger(__name__)


class SettingsStorage(UserDict, BaseStorage):
    def __init__(self, settings):
        super(SettingsStorage, self).__init__()
        self.settings = settings
        self.auth_encoding = settings.get('HTTPPROXY_AUTH_ENCODING')
        self._data = {}

    def open_spider(self, spider):
        logger.info('%s for httpproxy is used.',
                    self.settings['HTTPPROXY_STORAGE'])
        for scheme, proxies in self.settings['HTTPPROXY_PROXIES'].items():
            if scheme != 'no':
                self._data.update({
                    scheme: list(map(
                        lambda x: get_proxy(x, scheme, self.auth_encoding),
                        proxies
                    ))
                })
                self.update({scheme: cycle(self._data[scheme])})
            elif scheme == 'no':
                if isinstance(proxies, list) and '*' in proxies:
                    self._data.update({scheme: '*'})
                elif isinstance(proxies, str) and '*' == proxies:
                    self._data.update({scheme: proxies})
                else:
                    self._data.update({scheme: list(map(
                        lambda x: re.compile(
                            r'(.+\.)?{}$'.format(re.escape(x.lstrip('.'))),
                            flags=re.IGNORECASE
                        ),
                        proxies
                    ))})
                    self.update({scheme: cycle(self._data[scheme])})

    def close_spider(self, spider):
        pass

    def __getitem__(self, key):
        if key in self.data:
            return next(self.data[key])
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)
