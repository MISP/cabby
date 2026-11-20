===========================
Contributing and developing
===========================

.. _cabby project page: https://github.com/MISP/cabby


Reporting issues
================

Cabby uses Github's issue tracker. See the `Cabby project page`_ on Github.


Obtaining the source code
=========================

The Cabby source code can be found on Github. See the `Cabby project page`_ on
Github.

Layout
======

The Cabby repository has the following layout:

* ``docs/`` - used to build the `documentation <http://cabby.readthedocs.org>`_;
* ``cabby/`` - source code;
* ``tests/`` - tests.


Develop with uv
===============

Install uv as described in the :doc:`installation` guide. From the repository
root, create a virtual environment and install Cabby in editable mode with its
development dependencies::

    uv venv --python 3.12
    uv pip install -r requirements-dev.txt -e .

Activate the environment before running the tests or CLI commands. In a POSIX
shell, run ``. .venv/bin/activate``. In PowerShell, run
``.\.venv\Scripts\Activate.ps1``.

Running the tests
=================

From the activated environment, run::

    python -m pytest --cov=cabby
    python -m flake8
    taxii-discovery --help

To run the existing tox environments, use ``uvx --python 3.12 --with tox-uv tox -e py312,flake8``.


Generating the documentation
============================

The documentation is written in `ReStructuredText <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html>`_ (reST) format and processed
using `Sphinx <http://sphinx-doc.org/>`_. To build HTML documentation, go to ``docs`` and type ``make html``.

.. rubric:: Next steps

Continue to :doc:`License <license>`.

.. vim: set spell spelllang=en:
