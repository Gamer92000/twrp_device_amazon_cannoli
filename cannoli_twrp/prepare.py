"""Download and extract the pinned stock kernel/FIT for TWRP."""

import argparse
from pathlib import Path

from cannoli_twrp.firmware import firmware
from cannoli_twrp.images import STOCK, verified
from cannoli_twrp.ota import extract


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument(
        "--ota", type=Path, help="Local 8349 OTA downloaded through FTVDB"
    )
    args = parser.parse_args()
    work = args.directory.resolve()
    images = work / "images"
    images.mkdir(parents=True, exist_ok=True)
    extract(update=firmware(work, args.ota), wanted=("boot",), work=images)
    verified(images / "boot.img", STOCK["boot.img"])
    print("Stock images ready in", images)


if __name__ == "__main__":
    main()
