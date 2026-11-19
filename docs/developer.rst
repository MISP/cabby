===========================
Contributing and developing
===========================

.. _cabby project page: https://github.com/EclecticIQ/cabby


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


Compiling from source
=====================

From the repository root, with a Python 3.12 virtual environment active, run::

   $ python -m pip install -r requirements-dev.txt -e .


Running the tests
=================

Run the unit tests with ``python -m pytest``. To run the Python 3.12 test suite and lint checks in isolated environments, install `tox <https://tox.wiki/>`_ and run ``tox -e py312,flake8``.


Generating the documentation
============================

The documentation is written in `ReStructuredText <http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html>`_ (reST) format and processed
using `Sphinx <http://sphinx-doc.org/>`_. To build HTML documentation, go to ``docs`` and type ``make html``.

.. rubric:: Next steps

Continue to :doc:`License <license>`.

.. vim: set spell spelllang=en:
