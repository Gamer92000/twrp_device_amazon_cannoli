"""Package source-built headless TWRP as a Cannoli slot B FIT."""

import argparse
import json
from pathlib import Path

from cannoli_twrp.images import recovery, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("images", "ramdisk", "graphics", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    parser.add_argument("--serial", required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    recovery(args.images, args.ramdisk, args.graphics, args.serial, args.output)
    image = args.output / "boot_b.img"
    manifest = {
        "format": 1,
        "product": "cannoli",
        "build": "NS6575/8349",
        "serial": args.serial,
        "image": {
            "name": image.name,
            "size": image.stat().st_size,
            "sha256": sha(image.read_bytes()),
        },
        "sources": {
            "ramdisk_sha256": sha(args.ramdisk.read_bytes()),
            "graphics_sha256": sha(args.graphics.read_bytes()),
            "manifest_sha256": sha(
                (
                    Path(__file__).resolve().parents[1] / "manifests/pinned.xml"
                ).read_bytes()
            ),
        },
    }
    (args.output / "recovery.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("Recovery ready in", args.output)


if __name__ == "__main__":
    main()
