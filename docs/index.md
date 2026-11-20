# Cabby

The [MISP Project](https://www.misp-project.org/) maintains this fork of Cabby,
a Python TAXII client originally developed by [EclecticIQ](https://www.eclecticiq.com).

TAXII (Trusted Automated eXchange of Indicator Information) defines services and
message exchanges for sharing cyber threat intelligence. See the [TAXII homepage](http://taxii.mitre.org/).

Cabby provides a Python library and command-line tools for TAXII 1.0 and 1.1
services and TAXII 2.1 Core and Collections endpoints. The TAXII 1.x clients
return version-agnostic entities and stream Poll Response messages so callers can
process the first content block while the rest of the response arrives.

## Documentation contents

- [Installation guide](installation.md)
- [TAXII 2.1](taxii21.md)
- [User guide](user.md)
- [Cabby API documentation](api.md)
- [Contributing and developing](developer.md)
- [Changelog](changes.md)
- [License](license.md)

```{toctree}
:hidden:
:maxdepth: 1

installation
taxii21
user
api
developer
changes
license
```

## External links

- [Cabby documentation on GitHub Pages](https://misp.github.io/cabby/)
- [Source code and issue tracker on GitHub](https://github.com/MISP/cabby/)
- [misp-cabby releases on PyPI](https://pypi.org/project/misp-cabby/)
- [EclecticIQ](https://www.eclecticiq.com)
