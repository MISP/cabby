"""Command-line access to TAXII 2.1 resources."""

import argparse
from getpass import getpass
import json
import sys

from requests import RequestException

from cabby import Client
from cabby.exceptions import InvalidResponseError


def _parser():
    parser = argparse.ArgumentParser(description="Read and write TAXII 2.1 JSON resources")
    parser.add_argument("url", help="HTTPS discovery URL for discover, or API root URL for other commands")
    parser.add_argument("--user", help="HTTP Basic username (prompts for password)")
    parser.add_argument("--ca-cert", help="trusted CA bundle")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("discover", "info", "collections"):
        commands.add_parser(name)
    commands.add_parser("status").add_argument("status_id")
    for name in ("collection", "objects", "manifest", "versions", "add", "delete"):
        command = commands.add_parser(name)
        command.add_argument("collection_id")
        if name == "objects":
            command.add_argument("--object-id")
        if name in ("versions", "delete"):
            command.add_argument("object_id")
        if name in ("objects", "manifest", "versions"):
            command.add_argument("--limit", type=int, help="maximum number per page")
            command.add_argument("--added-after", help="UTC TAXII timestamp")
        if name in ("objects", "manifest", "versions", "delete"):
            command.add_argument("--match", action="append", default=[], metavar="FIELD=VALUE",
                                 help="TAXII match filter, e.g. type=indicator,malware")
        if name == "add":
            command.add_argument("file", help="JSON file containing a TAXII envelope")
    return parser


def _resources(client, args):
    if args.command == "discover":
        yield client.discover()
        return
    root = client.api_root(args.url)
    match = {}
    for item in getattr(args, "match", ()):
        key, separator, value = item.partition("=")
        if not separator or not key or not value or key in match:
            raise ValueError("Supply each --match FIELD=VALUE once")
        match[key] = value
    if args.command == "info":
        yield root.info()
    elif args.command == "collections":
        yield root.get_collections()
    elif args.command == "collection":
        yield root.get_collection(args.collection_id)
    elif args.command == "status":
        yield root.get_status(args.status_id)
    elif args.command == "add":
        with open(args.file, encoding="utf-8") as source:
            envelope = json.load(source)
        if not isinstance(envelope, dict) or not isinstance(envelope.get("objects"), list):
            raise ValueError("Expected a TAXII envelope with an objects array")
        yield root.add_objects(args.collection_id, envelope)
    elif args.command == "delete":
        root.delete_object(args.collection_id, args.object_id, match=match)
    else:
        filters = dict(limit=args.limit, added_after=args.added_after, match=match)
        if args.command == "objects":
            yield from root.object_pages(args.collection_id, args.object_id, **filters)
        elif args.command == "manifest":
            yield from root.manifest_pages(args.collection_id, **filters)
        elif args.command == "versions":
            yield from root.version_pages(args.collection_id, args.object_id, **filters)


def main():
    args = _parser().parse_args()
    try:
        with Client(args.url) as client:
            password = getpass() if args.user is not None else None
            client.set_auth(username=args.user, password=password, ca_cert=args.ca_cert)
            for resource in _resources(client, args):
                print(json.dumps(resource))
    except (RequestException, InvalidResponseError, ValueError, OSError) as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0
