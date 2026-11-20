from datetime import UTC, datetime
import json
import sys
import ssl
from threading import Thread
from urllib.parse import parse_qs, urlsplit

import pytest
import requests
import responses
import trustme
from werkzeug.serving import make_server

from cabby import Client, Client21, create_client
from cabby.cli.taxii21 import main
from cabby.client10 import Client10
from cabby.client11 import Client11
from cabby.exceptions import InvalidResponseError

ORIGIN = "https://taxii.example"
DISCOVERY = ORIGIN + "/taxii2/"
ROOT = ORIGIN + "/team/"
MEDIA = "application/taxii+json;version=2.1"
COLLECTION = "91a7b528-80eb-42ed-a74d-c6fbd5a26116"
CID = ROOT + f"collections/{COLLECTION}/"
OID = "identity--01d0f1c0-12d6-4f5b-a0ee-9d75e052b10f"
STAMP = "2025-04-01T00:00:00.000000Z"


def resource(method, url, body, status=200, headers=None):
    responses.add(method, url, json=body, status=status, content_type=MEDIA, headers=headers)


def test_entry_points():
    assert isinstance(create_client(), Client11)
    assert isinstance(create_client(version="1.0"), Client10)
    assert isinstance(Client(ORIGIN), Client21)
    assert create_client("taxii.example", version="2.1").discovery_url == DISCOVERY
    assert create_client("[::1]", port=8443, version="2.1").discovery_url == "https://[::1]:8443/taxii2/"
    assert create_client(discovery_url=DISCOVERY, version="2.1").discovery_url == DISCOVERY


@responses.activate
def test_discovery_collections_and_basic_auth():
    discovery = {"title": "Example", "default": "/team/", "api_roots": ["/team/"], "x_note": "example"}
    info = {"title": "Team", "versions": [MEDIA], "max_content_length": 1024}
    collection = {"id": COLLECTION, "title": "Example", "can_read": True, "can_write": True}
    resource("GET", DISCOVERY, discovery)
    resource("GET", ROOT, info)
    resource("GET", ROOT + "collections/", {"collections": [collection]})
    resource("GET", CID, collection)
    with Client(DISCOVERY, headers={"X-Example": "team"}) as client:
        client.set_auth(username="reader", password="secret")
        result = client.discover()
        assert result == discovery
        root = client.api_root(result["default"])
        assert root.info() == info
        assert root.get_collections()["collections"] == [collection]
        assert root.get_collection(COLLECTION) == collection
    for call in responses.calls:
        assert call.request.headers["Accept"] == MEDIA
        assert call.request.headers["X-Example"] == "team"
        assert call.request.headers["Authorization"] == "Basic cmVhZGVyOnNlY3JldA=="
        assert call.request.headers["User-Agent"].startswith("Cabby/")


@pytest.mark.parametrize(("operation", "suffix"), [
    (lambda r, **kw: r.object_pages(COLLECTION, **kw), "objects/"),
    (lambda r, **kw: r.object_pages(COLLECTION, OID, **kw), f"objects/{OID}/"),
    (lambda r, **kw: r.version_pages(COLLECTION, OID, **kw), f"objects/{OID}/versions/"),
    (lambda r, **kw: r.manifest_pages(COLLECTION, **kw), "manifest/"),
])
@responses.activate
def test_paged_resources(operation, suffix):
    url = CID + suffix
    pages = [{"more": True, "next": "state+/="}, {"more": True, "next": "state+/="},
             {"more": True}, {}]
    for page in pages:
        resource("GET", url, page, headers={"X-TAXII-Date-Added-Last": STAMP})
    with Client(DISCOVERY) as client:
        root = client.api_root(ROOT)
        assert list(operation(root, limit=1, match={"spec_version": ["2.0", "2.1"]},
                              added_after=datetime(2024, 1, 1, tzinfo=UTC))) == pages
    base = {"limit": ["1"], "match[spec_version]": ["2.0,2.1"], "added_after": ["2024-01-01T00:00:00.000000Z"]}
    queries = [parse_qs(urlsplit(call.request.url).query) for call in responses.calls]
    assert queries == [base, dict(base, next=["state+/="]), dict(base, next=["state+/="]),
                       dict(base, added_after=[STAMP])]
    expected_media = {MEDIA, "application/stix+json;version=2.1"} if suffix == "manifest/" else {MEDIA}
    for call in responses.calls:
        assert {item.strip() for item in call.request.headers["Accept"].split(",")} == expected_media


@responses.activate
def test_write_status_and_delete():
    status_id = "2d086da7-4bdc-4f91-900e-d77486753710"
    pending = {"id": status_id, "status": "pending", "total_count": 1, "success_count": 0,
               "pending_count": 1, "failure_count": 0}
    complete = dict(pending, status="complete", success_count=1, pending_count=0)
    resource("POST", CID + "objects/", pending, status=202)
    resource("GET", ROOT + f"status/{status_id}/", complete)
    responses.delete(CID + f"objects/{OID}/", status=200, content_type=MEDIA)
    obj = {"id": OID, "type": "identity", "spec_version": "2.1", "name": "Example"}
    with Client(DISCOVERY) as client:
        root = client.api_root("/team")
        result = root.add_objects(COLLECTION, [obj])
        assert result == pending
        assert root.get_status(result["id"]) == complete
        assert root.delete_object(COLLECTION, OID, match={"version": "first"}) is None
    post = responses.calls[0].request
    assert post.headers["Accept"] == post.headers["Content-Type"] == MEDIA
    assert json.loads(post.body) == {"objects": [obj]}
    assert parse_qs(urlsplit(responses.calls[-1].request.url).query) == {"match[version]": ["first"]}


@responses.activate
def test_error_resource_and_invalid_responses():
    resource("GET", DISCOVERY, {"title": "Not available", "x_reason": "test"}, status=403)
    responses.get(DISCOVERY, body="<xml/>", content_type="application/xml")
    responses.get(DISCOVERY, body="bad", content_type=MEDIA)
    responses.get(DISCOVERY, status=302, headers={"Location": "http://other.example/"})
    with Client(DISCOVERY) as client:
        with pytest.raises(requests.HTTPError) as err:
            client.discover()
        assert err.value.response.status_code == 403
        assert err.value.response.json()["x_reason"] == "test"
        for _ in range(3):
            with pytest.raises(InvalidResponseError):
                client.discover()
    assert len(responses.calls) == 4


@responses.activate
def test_invalid_continuation_and_request_parameters():
    resource("GET", CID + "objects/", {"more": True})
    with Client(DISCOVERY) as client:
        root = client.api_root(ROOT)
        with pytest.raises(InvalidResponseError, match="no continuation"):
            list(root.object_pages(COLLECTION))
        with pytest.raises(ValueError, match="limit"):
            list(root.object_pages(COLLECTION, limit=0))
        with pytest.raises(ValueError, match="timestamp"):
            list(root.object_pages(COLLECTION, added_after=["today", "yesterday"]))
        with pytest.raises(ValueError, match="versions"):
            list(root.object_pages(COLLECTION, match={"version": ["all", "last"]}))
        with pytest.raises(ValueError, match="resource identifier"):
            root.get_collection("..")
        with pytest.raises(ValueError):
            root.add_objects(COLLECTION, [])
    assert len(responses.calls) == 1


@pytest.mark.parametrize("url", [
    "http://taxii.example/", "//other.example/root/", "https://other.example/root/", "/root/?name=x", "../team/",
])
def test_reject_unsafe_root(url):
    with Client(DISCOVERY) as client, pytest.raises(ValueError):
        client.api_root(url)


@responses.activate
def test_cli_outputs_json_pages_and_propagates_errors(monkeypatch, capsys):
    url = CID + "objects/"
    resource("GET", url, {"objects": [{"id": OID}], "more": True, "next": "2"})
    resource("GET", url, {})
    monkeypatch.setattr(sys, "argv", ["taxii-21", ROOT, "objects", COLLECTION, "--match", "type=identity"])
    assert main() == 0
    pages = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert pages == [{"objects": [{"id": OID}], "more": True, "next": "2"}, {}]
    assert parse_qs(urlsplit(responses.calls[0].request.url).query) == {"match[type]": ["identity"]}
    resource("GET", DISCOVERY, {"title": "Unauthorized"}, status=401)
    monkeypatch.setattr(sys, "argv", ["taxii-21", DISCOVERY, "discover"])
    assert main() == 1
    assert "401" in capsys.readouterr().err


def test_https_basic_auth_with_private_ca(tmp_path):
    ca = trustme.CA()
    trust_file = tmp_path / "ca.pem"
    ca.cert_pem.write_to_path(str(trust_file))
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = context.maximum_version = ssl.TLSVersion.TLSv1_2
    ca.issue_cert("127.0.0.1").configure_cert(context)

    def discovery(environ, start_response):
        assert environ["PATH_INFO"] == "/taxii2/"
        assert environ["HTTP_ACCEPT"] == MEDIA
        if environ.get("HTTP_AUTHORIZATION") != "Basic dXNlcjpwYXNz":
            start_response("401 Unauthorized", [("WWW-Authenticate", 'Basic realm="test"')])
            return [b""]
        start_response("200 OK", [("Content-Type", MEDIA)])
        return [b'{"title":"TLS test"}']

    with make_server("127.0.0.1", 0, discovery, ssl_context=context) as server:
        thread = Thread(target=server.serve_forever)
        thread.start()
        try:
            with Client(f"https://127.0.0.1:{server.server_port}/", timeout=5) as client:
                with pytest.raises(requests.exceptions.SSLError):
                    client.discover()
                client.set_auth(ca_cert=str(trust_file))
                with pytest.raises(requests.HTTPError) as err:
                    client.discover()
                assert err.value.response.status_code == 401
                client.set_auth(username="user", password="pass", ca_cert=str(trust_file))
                assert client.discover() == {"title": "TLS test"}
        finally:
            server.shutdown()
            thread.join()
