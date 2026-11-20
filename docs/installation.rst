==================
Installation guide
==================

.. highlight:: sh

Cabby supports Python 3.11 and 3.12. The commands below use Python 3.12.

Install uv
==========

On macOS or Linux, run Astral's installer in a terminal::

    curl -LsSf https://astral.sh/uv/install.sh | sh

On Windows, run the installer in PowerShell::

    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

Open a new terminal and check the installation::

    uv --version

See the `uv installation guide <https://docs.astral.sh/uv/getting-started/installation/>`_
for package-manager alternatives. uv can download Python 3.12 automatically
when a command requests it.

Install the TAXII command-line tools
====================================

Install the MISP fork from GitHub into an isolated tool environment::

    uv tool install --python 3.12 git+https://github.com/MISP/cabby.git
    taxii-discovery --help

If your shell cannot find the command, run ``uv tool update-shell`` and open
a new terminal. Use ``taxii-21 --help`` for the TAXII 2.1 command (see :doc:`taxii21`). The installation also provides ``taxii-collections``,
``taxii-poll``, ``taxii-proxy``, ``taxii-push`` and ``taxii-subscription``.

Use Cabby in a Python project
=============================

From a uv project with a compatible Python requirement (for example,
``requires-python = ">=3.11,<3.13"``), add the MISP fork and verify the import::

    uv add "cabby @ git+https://github.com/MISP/cabby.git"
    uv run python -c "from cabby import create_client; print(create_client.__name__)"

uv records the dependency in ``pyproject.toml`` and the resolved Git commit
in ``uv.lock``. For an editable installation from a local checkout, see
:doc:`developer`.

Install with pip
================

With a Python 3.11 or 3.12 virtual environment active, install the MISP fork
from a checkout with ``python -m pip install .``. To install the published
PyPI release, run ``python -m pip install cabby``.


Versioning
==========

Releases of Cabby are given major.minor.revision version numbers, where major and minor correspond to the roadmap EclecticIQ has. The revision number is used to indicate a bug fix only release.


.. rubric:: Next steps

Continue with the :doc:`User guide <user>` to see how to use Cabby.

.. vim: set spell spelllang=en:
