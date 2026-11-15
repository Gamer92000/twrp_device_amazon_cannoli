from __future__ import annotations

import gzip
import hashlib
import lzma
import re
import struct
from pathlib import Path

from cannoli_twrp.cpio import read_cpio, write_cpio
from cannoli_twrp.fit import Fit

ASSETS = Path(__file__).resolve().parent / "assets"
BOOT_LIMIT = 0xD0B000
STOCK = {"boot.img": "548dd73848cfcc76cb921ec5d8c68438c95886f4fc7187da9fa5f4b7efb8b201"}


def rebuild(fit: Fit, edits: list[tuple[int, int, bytes]]) -> bytes:
    structure = bytearray(fit.struct)
    for start, end, value in sorted(edits, reverse=True):
        structure[start:end] = value
    shift = len(structure) - fit.sz
    header = bytearray(fit.data[: fit.so])
    for offset, value in [
        (4, fit.total + shift),
        (12, fit.st + shift),
        (36, len(structure)),
    ]:
        struct.pack_into(">I", header, offset, value)
    return bytes(header) + structure + fit.data[fit.st : fit.total]


def recovery(  # ruff: ignore[complex-structure]
    images: Path, ramdisk: Path, graphics: Path, serial: str, output: Path
) -> None:
    require(
        re.fullmatch(r"[A-Za-z0-9_-]{4,64}", serial) is not None, "Invalid USB serial"
    )
    fit = Fit(verified(images / "boot.img", STOCK["boot.img"]))
    entries = read_cpio(gzip.decompress(ramdisk.read_bytes()))
    library = graphics.read_bytes()
    require(
        b"headless memory graphics" in library,
        "Build the headless TWRP graphics library",
    )
    headers = {name: header for name, header, _ in entries}
    require(
        {
            "init.recovery.usb.rc",
            "init.recovery.mt8519.rc",
            "prop.default",
            "sbin/libminuitwrp.so",
            "sbin/permissive.sh",
        }.issubset(headers),
        "Incomplete TWRP ramdisk",
    )
    changed = []
    for name, header, original_data in entries:
        data = original_data
        if name == "sbin/libclang_rt.ubsan_standalone-arm-android.so":
            continue
        if name == "init.recovery.usb.rc":
            data = (
                (ASSETS / "usb.rc").read_bytes().replace(b"@SERIAL@", serial.encode())
            )
        elif name == "init.recovery.mt8519.rc":
            data = b"\n"
        elif name == "prop.default":
            data += b"\nro.adb.secure=0\nro.twrp.headless=1\n"
        elif name == "sbin/libminuitwrp.so":
            data = library
        elif name == "TRAILER!!!":
            changed.append(
                (
                    "sbin/cannoli-usb-bind.sh",
                    headers["sbin/permissive.sh"],
                    (ASSETS / "bind.sh").read_bytes(),
                )
            )
        changed.append((name, header, data))
    compressed = lzma.compress(write_cpio(changed), format=lzma.FORMAT_ALONE, preset=9)
    edits = []
    for node, prop, value in [
        ("/images/ramdisk-1", "data", compressed),
        ("/images/ramdisk-1/hash-1", "value", hashlib.sha256(compressed).digest()),
        ("/configurations", "default", b"cannoli-pvt-aluminum-recovery\0"),
    ]:
        replacement, (a, b) = fit.prop_replace(node, prop, value)
        edits.append((a, b, replacement))
    built = rebuild(fit, edits)
    built += b"\0" * (-len(built) % 4096)
    final = Fit(built)
    for node in fit.nodes:
        if node.endswith("/signature-1"):
            require(
                fit.signed_stream(node) == final.signed_stream(node),
                "Boot signature changed",
            )
    require(len(built) <= BOOT_LIMIT, "Recovery image exceeds its volume")
    (output / "boot_b.img").write_bytes(built)


def require(condition: bool, message: str) -> None:  # ruff: ignore[boolean-type-hint-positional-argument]
    if not condition:
        raise ValueError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verified(path: Path, checksum: str | None) -> bytes:
    data = path.read_bytes()
    require(sha(data) == checksum, f"Checksum mismatch: {path}")
    return data
