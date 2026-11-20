from importlib.metadata import version

import libtaxii

import cabby


def test_libtaxii_distribution():
    assert libtaxii.__version__ == version('misp-libtaxii')


def test_url_parse():
    url = 'https://eiq-test.com:1337/path/to/discovery'
    client = cabby.create_client(discovery_url=url)
    assert client.host == 'eiq-test.com'
    assert client.port == 1337
    assert client.use_https is True
    assert client.discovery_path == '/path/to/discovery'
