class ClientException(Exception):
    pass


class HTTPError(ClientException):

    def __init__(self, status_code):
        super().__init__(f'HTTP Error: status code {status_code}')


class InvalidResponseError(ClientException):
    pass


class UnsuccessfulStatusError(ClientException):

    def __init__(self, taxii_status, *args, **kwargs):
        msg = f"Server Error: {_status_to_message(taxii_status)}"
        super().__init__(msg, *args, **kwargs)

        self.status = taxii_status.status_type
        self.text = taxii_status.to_text()
        self.raw = taxii_status


class AmbiguousServicesError(ClientException):
    pass


class ServiceNotFoundError(ClientException):
    pass


class NoURIProvidedError(ValueError):
    pass


class NotSupportedError(ClientException):

    def __init__(self, version, *args, **kwargs):
        super().__init__(f"Not supported in version {version}", *args, **kwargs)


def _status_to_message(status):
    details = []

    if status.status_detail:
        details.append(_dict_to_pairs(status.status_detail))

    if status.extended_headers:
        details.append(_dict_to_pairs(status.extended_headers))

    if status.message:
        details.append(status.message)

    return "{}: {}".format(status.status_type, "; ".join(details))


def _dict_to_pairs(details):
    return ", ".join(f"{key}={value}" for key, value in details.items())
