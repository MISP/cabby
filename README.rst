cabby
=====

Python TAXII client implementation from `EclecticIQ <https://www.eclecticiq.com>`_.

:Source: https://github.com/MISP/cabby
:Documentation: http://cabby.readthedocs.org
:Information: https://www.eclecticiq.com
:Download: https://pypi.python.org/pypi/cabby/

|travis badge| |coveralls.io badge| |docs badge| |requirements badge|

.. |travis badge| image:: https://travis-ci.org/eclecticiq/cabby.svg?branch=master
   :target: https://travis-ci.org/eclecticiq/cabby
   :alt: Build Status
.. |coveralls.io badge| image:: https://coveralls.io/repos/eclecticiq/cabby/badge.svg
   :target: https://coveralls.io/r/eclecticiq/cabby
   :alt: Coverage Status
.. |docs badge| image:: https://readthedocs.org/projects/cabby/badge/?version=latest
   :alt: Documentation Status
   :scale: 100%
   :target: https://readthedocs.org/projects/cabby/
.. |requirements badge| image:: https://requires.io/github/eclecticiq/cabby/requirements.svg?branch=master
   :target: https://requires.io/github/eclecticiq/cabby/requirements/?branch=master
   :alt: Requirements Status

Use ``cabby.Client`` and ``taxii-21`` for TAXII 2.1 discovery and collections.
See the `TAXII 2.1 guide <docs/taxii21.rst>`_ for examples.
Existing ``create_client()`` calls default to TAXII 1.1.


Install with uv
---------------

With `uv <https://docs.astral.sh/uv/getting-started/installation/>`_ installed,
run the following to install this fork's TAXII commands and check the installation::

    uv tool install --python 3.12 git+https://github.com/MISP/cabby.git
    taxii-discovery --help

See the `installation guide <docs/installation.rst>`_ for setup instructions
and for adding Cabby to a Python project.

Docker
--------

To run cabby using docker, execute the following:

  docker run --rm eclecticiq/cabby taxii-discovery --path https://test.taxiistand.com/read-only/services/discovery

Feedback
--------

You are encouraged to provide feedback by commenting on open issues or sending us 
email at cabby@eclecticiq.com

