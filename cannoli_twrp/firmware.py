"""Resolve the pinned firmware through its FTVDB record."""

import hashlib
import shutil
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

OTA_PAGE = "https://ftvdb.com/echo/firmware/com.amazon.cannoli.android.os/0bf96b3cd8fca30fdd12f61208e44d76-13323246980-fire-os-6-5-7-5-ns6575-8349-2026-10-27/"
OTA_NAME = "update-kindle-cannoli-NS6575_user_8349_0013323246980.bin"
OTA_SHA = "a55e7223383ec0c3987b0bcdda4105049a5433b11b1ef3d0053566b10f5996d9"


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(path, expected):
    if checksum(path) != expected:
        raise ValueError(f"Checksum mismatch: {path}")


def resolve(html):
    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.urls = set()

        def handle_starttag(self, tag, attrs):
            if tag != "a":
                return
            url = urljoin(OTA_PAGE, dict(attrs).get("href", ""))
            parts = urlsplit(url)
            if (
                parts.scheme == "https"
                and parts.hostname
                and not parts.username
                and not parts.password
                and parts.path.rsplit("/", 1)[-1] == OTA_NAME
            ):
                self.urls.add(url)

    parser = Links()
    parser.feed(html)
    if len(parser.urls) != 1:
        raise ValueError(
            "FTVDB must link exactly one matching 8349 OTA; use --ota with a verified local download"
        )
    return parser.urls.pop()


def download(url, target, expected=None):
    if target.exists():
        if expected:
            verify(target, expected)
        return
    partial = target.with_suffix(".partial")
    with (
        urllib.request.urlopen(url, timeout=60) as source,
        partial.open("wb") as output,
    ):
        shutil.copyfileobj(source, output, 1024 * 1024)
    if expected:
        verify(partial, expected)
    partial.replace(target)


def firmware(work, local=None):
    if local is not None:
        verify(local, OTA_SHA)
        return local
    target = work / "stock.zip"
    if target.exists():
        verify(target, OTA_SHA)
        return target
    request = urllib.request.Request(
        OTA_PAGE, headers={"User-Agent": "CannoliBuilder/0.1"}
    )
    with urllib.request.urlopen(request, timeout=60) as page:
        html = page.read(2 * 1024 * 1024).decode("utf-8")
    download(resolve(html), target, OTA_SHA)
    return target
