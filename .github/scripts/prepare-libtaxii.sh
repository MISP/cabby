#!/usr/bin/env bash
set -euo pipefail

# Use normal index resolution as soon as the MISP distribution is published.
status=$(curl --silent --show-error --retry 3 --max-time 30 --output /dev/null \
    --write-out '%{http_code}' https://pypi.org/simple/misp-libtaxii/)
case "$status" in
    200) exit 0 ;;
    404) ;;
    *) echo "Could not check misp-libtaxii on PyPI (HTTP $status)." >&2; exit 1 ;;
esac

revision=1c4bfa13731eb22c8fd6b674c2f5f0d48be72820
wheels=$(mktemp -d "$RUNNER_TEMP/libtaxii-wheels.XXXXXX")
echo "Building misp-libtaxii from MISP/libtaxii@$revision until its first PyPI release."
uvx --from pip pip wheel --no-deps --wheel-dir "$wheels" \
    "misp-libtaxii @ git+https://github.com/MISP/libtaxii.git@$revision"
printf 'UV_FIND_LINKS=%s\n' "$wheels" >> "$GITHUB_ENV"
