import os
from copy import deepcopy
from unittest import TestCase

from scrapy import Spider
from scrapy.settings import Settings

from scrapy_httpproxy import get_proxy
from scrapy_httpproxy.settings import default_settings
from scrapy_httpproxy.storage.environment import EnvironmentStorage
from scrapy_httpproxy.storage.settings import SettingsStorage


class StorageTest(TestCase):
    def setUp(self):
        self.spider = Spider('foo')
        self.settings = Settings()
        self.settings.setmodule(default_settings)

    def tearDown(self):
        pass

    def test_environment(self):
        oldenv = os.environ.copy()

        os.environ['http_proxy'] = http_proxy = 'https://proxy.for.http:3128'
        os.environ['https_proxy'] = https_proxy = 'http://proxy.for.https:8080'
        os.environ.pop('file_proxy', None)

        settings = deepcopy(self.settings)
        storage = EnvironmentStorage(settings)

        storage.open_spider(self.spider)

        self.assertTrue(storage, True)

        self.assertIn('http', storage)
        self.assertIn('https', storage)
        self.assertNotIn('file_proxy', storage)
        self.assertSequenceEqual(
            storage['http'],
            get_proxy(http_proxy, 'http', storage.auth_encoding))
        self.assertSequenceEqual(
            storage['https'],
            get_proxy(https_proxy, 'https', storage.auth_encoding))

        storage.close_spider(self.spider)
        os.environ = oldenv

    def test_settings(self):
        http_proxy_1 = 'https://proxy.for.http.1:3128'
        http_proxy_2 = 'https://proxy.for.http.2:3128'
        https_proxy_1 = 'http://proxy.for.https.1:8080'
        https_proxy_2 = 'http://proxy.for.https.2:8080'

        local_settings = {
            'HTTPPROXY_ENABLED': True,
            'HTTPPROXY_PROXIES': {'http': [http_proxy_1, http_proxy_2],
                                  'https': [https_proxy_1, https_proxy_2]}
        }
        settings = deepcopy(self.settings)
        settings.setdict(local_settings)
        storage = SettingsStorage(settings)

        storage.open_spider(self.spider)

        self.assertTrue(storage, True)

        self.assertIn('http', storage)
        self.assertIn('https', storage)

        self.assertSequenceEqual(
            storage['http'],
            get_proxy(http_proxy_1, 'http', storage.auth_encoding)
        )
        storage.close_spider(self.spider)
