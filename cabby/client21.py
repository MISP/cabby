"""HTTPS client for the OASIS TAXII 2.1 Core and Collections APIs."""

from datetime import UTC, datetime
from email.message import Message
from urllib.parse import quote, urljoin, urlsplit

import requests

from ._version import __version__
from .exceptions import InvalidResponseError


MEDIA_TYPE = "application/taxii+json;version=2.1"
MANIFEST_ACCEPT = f"{MEDIA_TYPE}, application/stix+json;version=2.1"


def _https_url(url):
    parts = urlsplit(url)
    if (parts.scheme != "https" or not parts.hostname or parts.username is not None
            or parts.query or parts.fragment or "\\" in url or any(c.isspace() for c in url)):
        raise ValueError("Expected an absolute HTTPS endpoint without credentials, query or fragment")
    return parts


def _segment(value):
    if not isinstance(value, str) or value in ("", ".", ".."):
        raise ValueError("Expected a nonempty resource identifier")
    return quote(value, safe="")


def _params(match):
    params = {}
    for field, value in (match or {}).items():
        values = [value] if isinstance(value, str) else list(value)
        if not values or any(not isinstance(v, str) or not v for v in values):
            raise ValueError(f"Expected strings for match[{field}]")
        if field == "version":
            versions = ",".join(values).split(",")
            if len(set(versions)) != len(versions) or ("all" in versions and len(versions) > 1):
                raise ValueError("Duplicate versions and combinations with 'all' are invalid")
        params[f"match[{field}]"] = ",".join(values)
    return params


class Client21:
    """TAXII 2.1 client bound to the HTTPS origin of a discovery URL."""

    def __init__(self, discovery_url, *, headers=None, timeout=30):
        url = _https_url(discovery_url)
        self.discovery_url = url._replace(path=(url.path.rstrip("/") or "/taxii2") + "/").geturl()
        self._origin = (url.hostname, url.port or 443)
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers["User-Agent"] = f"Cabby/{__version__}"
        self.session.headers.update(headers or {})

    def set_auth(self, *, username=None, password=None, ca_cert=None, cert_file=None, key_file=None):
        """Configure HTTP Basic authentication, a trusted CA bundle or a client certificate."""
        if (username is None) != (password is None):
            raise ValueError("Supply both username and password for Basic authentication")
        if key_file and not cert_file:
            raise ValueError("A client key requires a certificate")
        self.session.auth = (username, password) if username is not None else None
        self.session.verify = ca_cert or True
        self.session.cert = (cert_file, key_file) if key_file else cert_file

    def close(self):
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _request(self, method, url, *, params=None, envelope=None, accept=MEDIA_TYPE):
        headers = {"Accept": accept}
        if envelope is not None:
            headers["Content-Type"] = MEDIA_TYPE
        response = self.session.request(
            method, url, params=params, json=envelope, headers=headers, timeout=self.timeout,
            verify=self.session.verify, allow_redirects=False,
        )
        response.raise_for_status()
        expected = 202 if method == "POST" else 200
        if response.status_code != expected:
            raise InvalidResponseError(f"Expected HTTP {expected}, received {response.status_code}")
        content_type = Message()
        content_type["Content-Type"] = response.headers.get("Content-Type", "")
        if content_type.get_content_type() != "application/taxii+json" or content_type.get_param("version") != "2.1":
            raise InvalidResponseError("Expected a TAXII 2.1 JSON response")
        if method == "DELETE":
            return None, response.headers
        try:
            body = response.json()
        except ValueError as exc:
            raise InvalidResponseError("Invalid TAXII JSON response") from exc
        if not isinstance(body, dict):
            raise InvalidResponseError("Expected a TAXII JSON resource")
        return body, response.headers

    def discover(self):
        """Return the discovery resource, including any advertised API roots."""
        return self._request("GET", self.discovery_url)[0]

    def api_root(self, url):
        """Select an absolute HTTPS or server-relative API root on this origin."""
        if url.startswith("/") and not url.startswith("//"):
            url = urljoin(self.discovery_url, url)
        return ApiRoot21(self, url)


class ApiRoot21:
    """Core and Collections operations within one selected API root."""

    def __init__(self, client, url):
        root = _https_url(url)
        if (root.hostname, root.port or 443) != client._origin:
            raise ValueError("Create a separate Client21 for an API root on another origin")
        self._client = client
        self.url = url.rstrip("/") + "/"

    def info(self):
        return self._client._request("GET", self.url)[0]

    def get_status(self, status_id):
        return self._client._request("GET", self.url + f"status/{_segment(status_id)}/")[0]

    def get_collections(self):
        return self._client._request("GET", self.url + "collections/")[0]

    def get_collection(self, collection_id):
        return self._client._request("GET", self._collection(collection_id))[0]

    def _collection(self, collection_id):
        return self.url + f"collections/{_segment(collection_id)}/"

    def _pages(self, url, accept=MEDIA_TYPE, /, *, limit=None, added_after=None, match=None, next_token=None):
        params = _params(match)
        if limit is not None:
            if not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0:
                raise ValueError("limit must be a positive integer")
            params["limit"] = limit
        if isinstance(added_after, datetime):
            if added_after.utcoffset() is None:
                raise ValueError("added_after must include a timezone")
            added_after = added_after.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        if added_after is not None:
            if not isinstance(added_after, str) or len(added_after) != 27:
                raise ValueError("Expected a UTC added_after timestamp with six fractional digits")
            datetime.strptime(added_after, "%Y-%m-%dT%H:%M:%S.%fZ")
            params["added_after"] = added_after
        if next_token is not None:
            if not isinstance(next_token, str) or not next_token:
                raise ValueError("next_token must be a nonempty string")
            params["next"] = next_token
        while True:
            page, headers = self._client._request("GET", url, params=params, accept=accept)
            more = page.get("more", False)
            next_token = page.get("next")
            if not isinstance(more, bool) or (next_token is not None and not isinstance(next_token, str)):
                raise InvalidResponseError("Invalid TAXII pagination metadata")
            yield page
            if not more:
                return
            if next_token:
                params["next"] = next_token
            elif headers.get("X-TAXII-Date-Added-Last"):
                last = headers["X-TAXII-Date-Added-Last"]
                if params.get("added_after") is not None and last <= params["added_after"]:
                    raise InvalidResponseError("TAXII pagination timestamp did not advance")
                params.pop("next", None)
                params["added_after"] = last
            else:
                raise InvalidResponseError("TAXII page has more results but no continuation")

    def object_pages(self, collection_id, object_id=None, **filters):
        """Yield complete envelopes, optionally for a single object ID."""
        url = self._collection(collection_id) + "objects/"
        if object_id is not None:
            url += _segment(object_id) + "/"
        return self._pages(url, **filters)

    def manifest_pages(self, collection_id, **filters):
        """Yield manifest resources, preserving each entry and custom property."""
        return self._pages(self._collection(collection_id) + "manifest/", MANIFEST_ACCEPT, **filters)

    def version_pages(self, collection_id, object_id, **filters):
        """Yield versions resources for an object."""
        url = self._collection(collection_id) + f"objects/{_segment(object_id)}/versions/"
        return self._pages(url, **filters)

    def add_objects(self, collection_id, objects):
        """Submit an envelope or an iterable of STIX dictionaries and return the status resource."""
        envelope = objects if isinstance(objects, dict) else {"objects": list(objects)}
        items = envelope.get("objects")
        if not isinstance(items, list) or not items or not all(isinstance(obj, dict) for obj in items):
            raise ValueError("Supply one or more JSON objects")
        url = self._collection(collection_id) + "objects/"
        return self._client._request("POST", url, envelope=envelope)[0]

    def delete_object(self, collection_id, object_id, *, match=None):
        """Delete the specified object or versions."""
        url = self._collection(collection_id) + f"objects/{_segment(object_id)}/"
        self._client._request("DELETE", url, params=_params(match))
