'''
    Cabby, python library for interacting with TAXII servers.
'''
from urllib.parse import urlparse

from ._version import __version__  # noqa: F401 (public package version)
from .client10 import Client10
from .client11 import Client11
from .client21 import Client21

# New code uses the HTTPS/JSON client. The historical factory defaults to 1.1.
Client = Client21


def create_client(host=None, port=None, discovery_path=None, use_https=False,
                  discovery_url=None, version="1.1", headers=None):
    '''Create a client instance (TAXII version specific).

    ``host``, ``port``, ``use_https``, ``discovery_path`` values
    can be overridden per request with ``uri`` argument passed to
    a client's method.

    :param str host: TAXII server hostname
    :param int port: TAXII server port
    :param str discovery_path: Discovery Service relative path
    :param bool use_https: if HTTPS should be used
    :param string discovery_url: URL to infer host, port, discovery_path,
                                 and use_https.
    :param string version: TAXII version (1.0, 1.1, or 2.1)
    :param dict headers: additional headers to pass with TAXII messages

    :return: client instance
    :rtype: :py:class:`cabby.client21.Client21` or
            :py:class:`cabby.client11.Client11` or
            :py:class:`cabby.client10.Client10`
    '''
    if version == '2.1':
        if discovery_url:
            if host is not None or port is not None or discovery_path is not None:
                raise ValueError("Use discovery_url or host/port/discovery_path for TAXII 2.1")
            return Client21(discovery_url, headers=headers)
        if not host:
            raise ValueError("TAXII 2.1 requires a host or HTTPS discovery_url")
        if any(c in host for c in "/?#@"):
            raise ValueError("Expected a hostname")
        authority = f"[{host}]" if ':' in host and not host.startswith('[') else host
        if port is not None:
            authority += f":{port}"
        path = (discovery_path or 'taxii2/').lstrip('/')
        return Client21(f"https://{authority}/{path}", headers=headers)

    if discovery_url:
        parsed = urlparse(discovery_url)
        if not host and parsed.hostname:
            host = parsed.hostname
        if not port and parsed.port:
            port = parsed.port
        if not discovery_path and parsed.path:
            discovery_path = parsed.path
        if parsed.scheme:
            use_https = parsed.scheme == 'https'

    params = dict(
        host=host,
        port=port,
        use_https=use_https,
        discovery_path=discovery_path,
        headers=headers)

    if version == '1.1':
        return Client11(**params)
    elif version == '1.0':
        return Client10(**params)
    else:
        raise ValueError("TAXII version %s is not supported" % version)
