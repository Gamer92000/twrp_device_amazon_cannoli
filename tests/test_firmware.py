import hashlib
import io

import pytest

from cannoli_twrp import firmware as fw


def test_resolve_duplicate_link_and_html_entities():
    url = "https://downloads.example/" + fw.OTA_NAME + "?a=1&amp;b=2"
    assert fw.resolve(
        f'<a href="{url}">Download</a><a href="{url}">Mirror</a>'
    ) == url.replace("&amp;", "&")


@pytest.mark.parametrize(
    "html",
    [
        "",
        '<a href="https://example/other.bin">wrong build</a>',
        '<a href="http://example/' + fw.OTA_NAME + '">insecure</a>',
        '<a href="https://user:secret@example/' + fw.OTA_NAME + '">credentials</a>',
        '<a href="https://one/'
        + fw.OTA_NAME
        + '">one</a><a href="https://two/'
        + fw.OTA_NAME
        + '">two</a>',
    ],
)
def test_resolve_fails_closed(html):
    with pytest.raises(ValueError, match="exactly one"):
        fw.resolve(html)


def test_firmware_resolves_record_before_download(tmp_path, monkeypatch):
    data = b"stock OTA"
    monkeypatch.setattr(fw, "OTA_SHA", hashlib.sha256(data).hexdigest())
    url = "https://downloads.example/" + fw.OTA_NAME
    calls = []

    def open_url(request, timeout):
        address = request if isinstance(request, str) else request.full_url
        calls.append(address)
        return io.BytesIO(
            (f'<a href="{url}">Download</a>').encode()
            if address == fw.OTA_PAGE
            else data
        )

    monkeypatch.setattr(fw.urllib.request, "urlopen", open_url)
    assert fw.firmware(tmp_path).read_bytes() == data
    assert calls == [fw.OTA_PAGE, url]
    calls.clear()
    fw.firmware(tmp_path)
    assert calls == []
    (tmp_path / "stock.zip").write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="Checksum mismatch"):
        fw.firmware(tmp_path)
    assert calls == []


def test_wrong_download_is_not_promoted(tmp_path, monkeypatch):
    monkeypatch.setattr(
        fw.urllib.request, "urlopen", lambda *a, **k: io.BytesIO(b"wrong")
    )
    target = tmp_path / "stock.zip"
    with pytest.raises(ValueError, match="Checksum mismatch"):
        fw.download("https://example/ota", target, "0" * 64)
    assert not target.exists()


def test_local_ota_must_match_pin(tmp_path):
    local = tmp_path / "download.bin"
    local.write_bytes(b"incorrect firmware")
    with pytest.raises(ValueError, match="Checksum mismatch"):
        fw.firmware(tmp_path, local)
