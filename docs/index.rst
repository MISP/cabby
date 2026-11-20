=====
Cabby
=====

Cabby is Python TAXII client implementation from `EclecticIQ <https://www.eclecticiq.com>`_.

TAXII (Trusted Automated eXchange of Indicator Information) is a collection of specifications defining a set of services and message exchanges used for sharing cyber threat intelligence information between parties. Check `TAXII homepage <http://taxii.mitre.org/>`_ to get more information.


Cabby is designed from the ground up to act as a Python library and as a command line tool, it's key features are:

* **Rich feature set**:
  supports TAXII 1.0 and 1.1 services and the TAXII 2.1 Core and Collections endpoints.

* **Version agnostic**:
  abstracts specific implementation details and returns version agnostic entities.

* **Stream parsing**:
  heavy TAXII Poll Response messages are parsed on the fly, reducing memory footprint and time until first content block is available.


.. rubric:: Documentation contents

.. toctree::
   :maxdepth: 1

   installation
   taxii21
   user
   api
   developer
   changes
   license

.. rubric:: External links

* `Online documentation <https://cabby.readthedocs.org/>`_ (Read the docs)
* `Project page <https://github.com/EclecticIQ/cabby/>`_ with source code and issue tracker (Github)
* `Python Package Index (PyPI) page <http://pypi.python.org/pypi/cabby/>`_ with released tarballs
* `EclecticIQ <https://www.eclecticiq.com>`_
