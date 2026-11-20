import ssl
import threading
from urllib.error import URLError

import pytest
import trustme
import werkzeug.serving
import werkzeug.wrappers
from cryptography.hazmat.primitives import serialization

import cabby
import fixtures11


@pytest.fixture
def httpsserver(tmp_path, monkeypatch):
    # Requests gives environment CA bundles precedence over the session bundle.
    monkeypatch.delenv('REQUESTS_CA_BUNDLE', raising=False)
    monkeypatch.delenv('CURL_CA_BUNDLE', raising=False)
    ca = trustme.CA()
    server_cert = ca.issue_cert('127.0.0.1')
    client_cert = ca.issue_cert('cabby-test-client')

    ca_path = tmp_path / 'ca.pem'
    cert_path = tmp_path / 'client.pem'
    key_path = tmp_path / 'client.key'
    encrypted_key_path = tmp_path / 'client-encrypted.key'
    ca.cert_pem.write_to_path(str(ca_path))
    client_cert.cert_chain_pems[0].write_to_path(str(cert_path))
    client_cert.private_key_pem.write_to_path(str(key_path))

    key_password = b'cabby-test'
    key = serialization.load_pem_private_key(client_cert.private_key_pem.bytes(), password=None)
    encrypted_key_path.write_bytes(key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.BestAvailableEncryption(key_password),
    ))

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_cert.configure_cert(context)
    ca.configure_trust(context)
    context.verify_mode = ssl.CERT_REQUIRED
    server = werkzeug.serving.make_server(
        host='127.0.0.1',
        port=0,
        app=remote_taxii_app,
        threaded=True,
        passthrough_errors=True,
        ssl_context=context)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    try:
        yield server, str(key_path), dict(
            ca_cert=str(ca_path),
            cert_file=str(cert_path),
            key_file=str(encrypted_key_path),
            key_password=key_password,
        )
    finally:
        server.shutdown()
        server_thread.join()
        server.server_close()


def remote_taxii_app(env, start_response):
    path = env['PATH_INFO']

    if path == '/auth':
        body = b'{"token": "123"}'
        headers = [('Content-Type', 'application/json')]
    elif path == fixtures11.DISCOVERY_PATH:
        body = fixtures11.DISCOVERY_RESPONSE.encode()
        headers = [
            ('Content-Type', 'application/xml'),
            ('X-TAXII-Content-Type', 'urn:taxii.mitre.org:message:xml:1.1'),
        ]
    else:
        raise Exception('Unknown test path')

    headers.append(('Content-Length', str(len(body))))
    start_response('200 OK', headers)
    return [body]


def test_set_auth_ssl(httpsserver):
    server, unencrypted_key, tls_params = httpsserver
    host, port = server.server_address
    client = cabby.create_client(
        host=host,
        port=port,
        use_https=True,
        discovery_path=fixtures11.DISCOVERY_PATH)
    client.timeout = 5

    auth_params = dict(
        tls_params,
        username='cabby',
        password='test',
        jwt_auth_url='/auth',
        verify_ssl=True)

    # Test client certificate with key_password.
    # This doesn't use the requests library, instead
    # it uses urllib.request through the 'request_with_key_password' function:
    client.set_auth(**auth_params)
    services = client.discover_services()
    assert len(services) == 4

    # Test we get the correct error when forgetting a key_password:
    missing_key_password = dict(auth_params, key_password=None)
    client.set_auth(**missing_key_password)
    error_msg = "Key file is encrypted but key password was not provided"
    with pytest.raises(ValueError, match=error_msg):
        client.discover_services()

    # Test that server certificate authentication can fail:
    invalid_server_ca_cert = dict(auth_params, ca_cert=None)
    client.set_auth(**invalid_server_ca_cert)
    error_msg = "certificate verify failed"
    with pytest.raises(URLError, match=error_msg):
        client.discover_services()

    # Test that verify_ssl=False ignores the invalid certificate:
    invalid_server_ca_cert_no_verify = dict(
        auth_params, ca_cert=None, verify_ssl=False)
    client.set_auth(**invalid_server_ca_cert_no_verify)
    services = client.discover_services()
    assert len(services) == 4

    # An unencrypted client key uses requests.
    client_key_without_passphrase = dict(
        auth_params, key_file=unencrypted_key, key_password=None)
    client.set_auth(**client_key_without_passphrase)
    services = client.discover_services()
    assert len(services) == 4


def test_encrypted_client_key_verifies_server_hostname(httpsserver):
    server, _, tls_params = httpsserver
    client = cabby.create_client(
        host='localhost',
        port=server.server_port,
        use_https=True,
        discovery_path=fixtures11.DISCOVERY_PATH)
    client.timeout = 5
    client.set_auth(**tls_params)

    with pytest.raises(URLError, match='[Hh]ostname'):
        client.discover_services()
