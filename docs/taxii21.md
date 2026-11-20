# TAXII 2.1

Use `cabby.Client` for TAXII 2.1. The existing `create_client()`
factory still defaults to 1.1 and accepts explicit versions `"1.0"`,
`"1.1"` and `"2.1"`. The original TAXII 1.x commands and XML entity
APIs continue to work with their existing arguments.

## Discover and read

Supply an HTTPS origin to use the standard discovery path, `/taxii2/`,
or pass the full discovery URL. Discovery returns a JSON resource as a
Python dictionary. Choose one of the advertised API roots. Servers may
omit the default root or the entire list of roots. If you already know
an API root URL, you can call `client.api_root(url)` directly.

```python
from cabby import Client

with Client("https://cti.example.org", timeout=20) as client:
    discovery = client.discover()
    roots = discovery.get("api_roots", [])
    if roots:
        root = client.api_root(discovery.get("default", roots[0]))
        for collection in root.get_collections().get("collections", []):
            if collection["can_read"]:
                for page in root.object_pages(collection["id"], limit=100,
                                              match={"type": "indicator"}):
                    for obj in page.get("objects", []):
                        print(obj["id"])
```

Use `client.set_auth(username=user, password=password)` for HTTP Basic
authentication. The client verifies server certificates by default. Pass
`ca_cert` for a private CA, or `cert_file` and `key_file` for a client
certificate and unencrypted key. Use the constructor's `headers` argument
for a bearer token. Each client is scoped to one HTTPS origin. To use an
advertised root on another origin, construct a separate client for its URL
and configure its credentials explicitly.

## Core and Collections operations

The client implements the Core and Collections endpoints in sections 4
and 5 of the [OASIS TAXII 2.1 Standard](https://docs.oasis-open.org/cti/taxii/v2.1/os/taxii-v2.1-os.html).

| Method                    | Result                                                 |
|---------------------------|--------------------------------------------------------|
| `client.discover()`       | Discovery resource                                     |
| `root.info()`             | API root information, including `max_content_length`   |
| `root.get_collections()`  | Collections resource                                   |
| `root.get_collection(c)`  | Metadata for collection ID or alias `c`                |
| `root.manifest_pages(c)`  | Iterator of manifest resources                         |
| `root.object_pages(c)`    | Iterator of object envelopes, optionally by object ID  |
| `root.version_pages(c,i)` | Iterator of version resources for object ID `i`        |
| `root.add_objects(c,obs)` | Submission status for an iterable of STIX dictionaries |
| `root.get_status(id)`     | Current submission status                              |
| `root.delete_object(c,i)` | Delete an object, optionally with a version filter     |

Each page preserves the complete JSON resource, including custom properties.
The page iterators accept `limit`, `added_after`, `next_token`, and
`match`. The limit applies per request. Supply a UTC TAXII timestamp or
an aware Python datetime for `added_after`. Use strings or lists of strings
for match values, such as `match={"type": ["indicator", "identity"]}`.
Use the filters defined for the selected endpoint in section 5. For example,
`root.object_pages(c, object_id=i, match={"version": "all"})` retrieves
versions of one object. Iteration follows the server's opaque continuation
token or its last-added timestamp until the final page.

When adding objects, size the submission to the API root's advertised
`max_content_length`. A successful HTTP 202 returns the status resource.
If its `status` is `"pending"`, poll `root.get_status(status["id"])` at
an interval appropriate for the server. Inspect the final counts and any
per-object failures even when the status is `"complete"`.

HTTP errors raise `requests.HTTPError`. Its `response` retains the status
code, headers, and body, including any TAXII error resource. Unexpected
successful response codes, incorrect media types, or malformed JSON raise
`cabby.exceptions.InvalidResponseError`. Server selection uses the URL
you provide. DNS SRV lookup is optional for clients and is not implemented.

## Command line

`taxii-21` takes a discovery URL for `discover` and an API root URL
for collection operations. It prints JSON, one resource per line. With
`--user`, the command prompts for the Basic authentication password.

```console
$ taxii-21 https://cti.example.org discover
$ taxii-21 https://cti.example.org/team/ --user analyst collections
$ taxii-21 https://cti.example.org/team/ objects COLLECTION_ID --match type=indicator
$ taxii-21 https://cti.example.org/team/ add COLLECTION_ID envelope.json
$ taxii-21 https://cti.example.org/team/ status STATUS_ID
```

Use `taxii-21 --help` or a subcommand's `--help` for its arguments.
