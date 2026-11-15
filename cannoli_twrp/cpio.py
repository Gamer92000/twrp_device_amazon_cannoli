from __future__ import annotations

MAX_NAME = 4096


def align(n: int, boundary: int = 4) -> int:
    return (n + boundary - 1) & ~(boundary - 1)


def read_cpio(blob: bytes) -> list[tuple[str, bytes, bytes]]:
    pos, entries = 0, []
    while pos + 110 <= len(blob):
        header = blob[pos : pos + 110]
        if header[:6] not in {b"070701", b"070702"}:
            msg = f"invalid newc header at {pos}"
            raise ValueError(msg)
        size = int(header[54:62], 16)
        name_size = int(header[94:102], 16)
        name_end = pos + 110 + name_size
        if not 1 <= name_size <= MAX_NAME or name_end > len(blob):
            msg = "invalid newc name"
            raise ValueError(msg)
        name_raw = blob[pos + 110 : name_end]
        if name_raw[-1:] != b"\0":
            msg = "unterminated newc name"
            raise ValueError(msg)
        name = name_raw[:-1].decode()
        start = align(name_end)
        end = start + size
        if end > len(blob):
            msg = "truncated newc data"
            raise ValueError(msg)
        entries.append((name, header, blob[start:end]))
        pos = align(end)
        if name == "TRAILER!!!":
            return entries
    msg = "newc archive has no trailer"
    raise ValueError(msg)


def write_cpio(entries: list[tuple[str, bytes, bytes]]) -> bytes:
    out = bytearray()
    for name, original_header, data in entries:
        encoded = name.encode() + b"\0"
        header = bytearray(original_header)
        header[54:62] = f"{len(data):08x}".encode()
        header[94:102] = f"{len(encoded):08x}".encode()
        out += header + encoded
        out += b"\0" * (-len(out) % 4)
        out += data
        out += b"\0" * (-len(out) % 4)
    out += b"\0" * (-len(out) % 512)
    return bytes(out)
