HTTPPROXY_ENABLED = True
HTTPPROXY_AUTH_ENCODING = 'latin-1'

# ------------------------------------------------------------------------------
# PROXY IN ENVIRONMENT
# ------------------------------------------------------------------------------

HTTPPROXY_STORAGE = 'scrapy_httpproxy.storage.environment.EnvironmentStorage'

# ------------------------------------------------------------------------------
# PROXY IN SETTINGS
# ------------------------------------------------------------------------------

# HTTPPROXY_STORAGE = 'scrapy_httpproxy.storage.settings.SettingsStorage'
# HTTPPROXY_PROXIES = {
#     'http': ['http://127.0.0.1:8080'],
#     'https': ['https://127.0.0.1:8080'],
# }
