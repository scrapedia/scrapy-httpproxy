import base64
try:
    from urllib2 import _parse_proxy
except ImportError:
    from urllib.request import _parse_proxy

from six.moves.urllib.parse import urlunparse, unquote

from scrapy.utils.python import to_bytes


def basic_auth_header(username, password, auth_encoding):
    user_pass = to_bytes(
        '%s:%s' % (unquote(username), unquote(password)),
        encoding=auth_encoding)
    return b'Basic ' + base64.b64encode(user_pass).strip()


def get_proxy(url, orig_type, auth_encoding):
    proxy_type, user, password, hostport = _parse_proxy(url)
    proxy_url = urlunparse((proxy_type or orig_type, hostport, '', '', '', ''))

    if user:
        creds = basic_auth_header(user, password, auth_encoding)
    else:
        creds = None

    return creds, proxy_url
