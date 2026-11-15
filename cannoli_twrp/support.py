import hashlib


class FatalError(ValueError):
    def __init__(self, *, message):
        super().__init__(message)


def digest(*, kind, path):
    value = hashlib.new(kind)
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def passed(*, message):
    print(message)
