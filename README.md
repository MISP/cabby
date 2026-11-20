# Cabby

The [MISP Project](https://www.misp-project.org/) maintains this fork of Cabby,
a Python TAXII client originally developed by [EclecticIQ](https://www.eclecticiq.com).

[Source](https://github.com/MISP/cabby) · [Documentation](https://misp.github.io/cabby/) · [PyPI](https://pypi.org/project/cabby/)

[![Build status](https://github.com/MISP/cabby/actions/workflows/tox.yml/badge.svg)](https://github.com/MISP/cabby/actions/workflows/tox.yml)
[![Coverage status](https://coveralls.io/repos/eclecticiq/cabby/badge.svg)](https://coveralls.io/r/eclecticiq/cabby)
[![Documentation status](https://github.com/MISP/cabby/actions/workflows/docs.yml/badge.svg)](https://github.com/MISP/cabby/actions/workflows/docs.yml)
[![Requirements status](https://requires.io/github/eclecticiq/cabby/requirements.svg?branch=master)](https://requires.io/github/eclecticiq/cabby/requirements/?branch=master)

Use `cabby.Client` and `taxii-21` for TAXII 2.1 discovery and collections.
Existing `create_client()` calls default to TAXII 1.1. See the [TAXII 2.1 guide](https://misp.github.io/cabby/taxii21.html) for examples.

## Install with uv

With [uv](https://docs.astral.sh/uv/getting-started/installation/) installed,
run the following to install this fork's TAXII commands and check the installation.

```sh
uv tool install --python 3.12 git+https://github.com/MISP/cabby.git
taxii-discovery --help
```

See the [installation guide](https://misp.github.io/cabby/installation.html) for setup instructions
and for adding Cabby to a Python project.

## Docker

To run EclecticIQ's Cabby image, use the following command.

```sh
docker run --rm eclecticiq/cabby taxii-discovery --path https://test.taxiistand.com/read-only/services/discovery
```

## Feedback

Report issues and share feedback on the [MISP/cabby issue tracker](https://github.com/MISP/cabby/issues).
