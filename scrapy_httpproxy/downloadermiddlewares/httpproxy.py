try:
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache
try:
    from urllib2 import _parse_proxy
except ImportError:
    from urllib.request import _parse_proxy

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.settings import SETTINGS_PRIORITIES
from scrapy.utils.httpobj import urlparse_cached
from scrapy.utils.misc import load_object
from six.moves.urllib.request import proxy_bypass

from scrapy_httpproxy import get_proxy
from scrapy_httpproxy.settings import unfreeze_settings, default_settings

cached_proxy_bypass = lru_cache(maxsize=1024)(proxy_bypass)


class HttpProxyMiddleware(object):

    def __init__(self, settings):
        self.settings = settings
        self.auth_encoding = settings.get('HTTPPROXY_AUTH_ENCODING')
        self.proxies = load_object(settings['HTTPPROXY_STORAGE']).from_middleware(self)

    @classmethod
    def from_crawler(cls, crawler):
        with unfreeze_settings(crawler.settings) as settings:
            settings.setmodule(
                module=default_settings, priority=SETTINGS_PRIORITIES['default']
            )
        if not crawler.settings.getbool('HTTPPROXY_ENABLED'):
            raise NotConfigured
        o = cls(crawler.settings)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        self.proxies.open_spider(spider)

    def spider_closed(self, spider):
        self.proxies.close_spider(spider)

    def process_request(self, request, spider):
        # ignore if proxy is already set
        if 'proxy' in request.meta:
            if request.meta['proxy'] is None:
                return
            # extract credentials if present
            creds, proxy_url = get_proxy(request.meta['proxy'], '',
                                         self.auth_encoding)
            request.meta['proxy'] = proxy_url
            if creds and not request.headers.get('Proxy-Authorization'):
                request.headers['Proxy-Authorization'] = creds
            return
        elif not self.proxies:
            return

        parsed = urlparse_cached(request)
        scheme = parsed.scheme

        # 'no_proxy' is only supported by http schemes
        if scheme in ('http', 'https') and cached_proxy_bypass(parsed.hostname):
            return

        if scheme in self.proxies:
            self._set_proxy(request, scheme)

    def _set_proxy(self, request, scheme):
        creds, proxy = self.proxies[scheme]
        request.meta['proxy'] = proxy
        if creds:
            request.headers['Proxy-Authorization'] = creds
