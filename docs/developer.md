# Contributing and developing

## Reporting issues

Report issues on the [Cabby issue tracker](https://github.com/MISP/cabby/issues).

## Obtaining the source code

Download or clone the [Cabby repository](https://github.com/MISP/cabby).

## Layout

The Cabby repository has the following layout:

- `docs/` contains the [documentation](https://misp.github.io/cabby/).
- `cabby/` contains the library and command-line tools.
- `tests/` contains the test suite.

## Develop with uv

Install uv as described in the [installation](installation.md) guide. From the repository
root, create a virtual environment and install Cabby in editable mode with its
development dependencies:

```sh
uv venv --python 3.12
uv pip install -r requirements-dev.txt -e .
```

Activate the environment before running the tests or CLI commands. In a POSIX
shell, run `. .venv/bin/activate`. In PowerShell, run
`.\.venv\Scripts\Activate.ps1`.

## Running the tests

From the activated environment, run:

```sh
python -m pytest --cov=cabby
python -m flake8
taxii-discovery --help
```

To run the existing tox environments, use `uvx --python 3.12 --with tox-uv tox -e py312,flake8`.

## Generating the documentation

The guides use Markdown. Sphinx builds the site with the MyST parser and
generates the API reference from Cabby's docstrings. From the repository root,
build the HTML site with uv.

```sh
uv run --python 3.12 --extra docs sphinx-build -W -b html docs docs/_build/html
```

Open `docs/_build/html/index.html` to browse the result.

The Documentation workflow checks the site on pull requests and publishes it
to [GitHub Pages](https://misp.github.io/cabby/) on pushes to `master`. For
the initial setup, select **GitHub Actions** as the publishing source under
**Settings → Pages → Build and deployment**. To redeploy, run the workflow
manually from `master`.

## Next steps

Continue to [License](license.md).
