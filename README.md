# TWRP device tree for Amazon Cannoli

Build headless TWRP and package a slot B recovery FIT for the Echo Dot
(5th Generation), codename **Cannoli**, on stock **NS6575/8349**.
This is an unofficial recovery builder. It never connects
to or flashes a device and does not depend on Firebreak or the OS builder.

## Supported device

| Device | Codename | Stock build | Installation |
| --- | --- | --- | --- |
| Echo Dot (5th Generation) | cannoli | NS6575/8349 | [Firebreak guide][install] |

The root device-tree layout follows
[R0rt1z2's Echo recovery trees][example]. `AndroidProducts.mk`,
`BoardConfig.mk`, `omni_cannoli.mk`, `vendorsetup.sh` and `recovery/`
map directly to `device/amazon/cannoli` in an Android source checkout.
Our pinned manifest and packaging helpers live alongside that tree.

## Build on x86-64 Linux

Use Python 3.10 or later and a dedicated TWRP tree. Allow about 26 GB.
Run these commands from this repository root:

```sh
sudo apt install python3 git repo build-essential unzip curl rsync bc bison \
  flex libssl-dev libxml2-utils xsltproc zlib1g-dev gcc-multilib g++-multilib lib32z1
python3 -m cannoli_twrp.prepare "$PWD/work/inputs"
export STOCK_IMAGES="$PWD/work/inputs/images"
export TWRP_TREE="$PWD/work/twrp"
bash build.sh
```

The preparer resolves [FTVDB's Cannoli 8349 record][firmware], verifies the
pinned OTA SHA-256 and extracts/verifies the stock boot FIT. To use a local
OTA, add `--ota /absolute/path/to/update.bin`. There is no hardcoded CDN
fallback. An existing verified `boot.img` from the OS preparer can instead
be used by setting `STOCK_IMAGES` to its `images` directory.

`build.sh` syncs `manifests/pinned.xml` and checks all 226 project revisions
before building. It stages the root device-tree files at `device/amazon/cannoli`,
extracts the stock kernel, and applies the headless graphics and host build
patches. A hash-pinned Python 2.7.18 is built locally for legacy Android build
tools; the Python modules in this repository use Python 3. `JOBS` defaults
to 4. Android's `OUT_DIR` can select a fresh output directory.

On WSL, keep `TWRP_TREE` on the Linux ext4 filesystem (`~/twrp-cannoli`),
not on the Windows drive: the 9p bridge onto a case-insensitive NTFS target
hangs the source sync around the 20 GB mark. One Ubuntu 22.04 reporter also
needed the `en_US.UTF-8` locale generated first
(`sudo locale-gen en_US.UTF-8`); if a clean build fails on a locale error,
this is the cause.

Package the build for the target USB serial:

```sh
CANNOLI_SERIAL=REPLACE_WITH_USB_SERIAL
PRODUCT="$TWRP_TREE/out/target/product/cannoli"
python3 -m cannoli_twrp.pack \
  --images "$STOCK_IMAGES" \
  --ramdisk "$PRODUCT/ramdisk-recovery.img" \
  --graphics "$PRODUCT/system/lib/libminuitwrp.so" \
  --serial "$CANNOLI_SERIAL" \
  --output "$PWD/work/recovery"
```

If using `OUT_DIR`, set `PRODUCT` to `$OUT_DIR/target/product/cannoli`.
Use a new output directory. The result is `boot_b.img` plus `recovery.json`,
which records the serial, build, image hash/size and input artifact hashes.
Packaging retains the stock kernel/device tree and checks that each signed
FIT stream is unchanged. It requires the headless graphics library and
rejects oversized images.

Pass this directory to [cannoli-os-builder][os] with `--recovery`; that
builder adds the loaders, rooted OS and UBI writer for Firebreak. The
recovery image alone is not a complete Firebreak bundle.

## Layout and limitations

- Root `*.mk`, `vendorsetup.sh` and `recovery/`: Android device tree.
- `manifests/pinned.xml`: commit-pinned upstream source projects.
- `patches/`: headless recovery and host build compatibility changes.
- `cannoli_twrp/`: stock preparation and FIT/ramdisk packaging.
- `tests/`: OTA extraction, firmware resolution and packaging checks.

Cannoli has no screen. Recovery provides an unauthenticated root USB ADB
shell using configfs/FunctionFS. Generic TWRP wipe, format, GUI, encryption
and ZIP installation are not validated for its NAND UBI layout. Use the
[Firebreak Cannoli route][install] for installation and restoration.

```sh
uv run --with pytest python -m pytest -q
uvx ruff check .
uvx ruff format --check .
bash -n build.sh
```

See [repository conventions](CONVENTIONS.md), [release process](RELEASING.md),
[source provenance](NOTICE.md)
and [validation](VALIDATION.md). No firmware, kernel binary, generated image,
private key or synced Android source tree is committed.

[firmware]: https://ftvdb.com/echo/firmware/com.amazon.cannoli.android.os/0bf96b3cd8fca30fdd12f61208e44d76-13323246980-fire-os-6-5-7-5-ns6575-8349-2026-10-27/
[os]: https://github.com/Gamer92000/cannoli-os-builder
[install]: https://github.com/Gamer92000/firebreak/blob/main/docs/cannoli.md

[example]: https://github.com/R0rt1z2/twrp_device_amazon_cronos/tree/20f00d86d36fc1e80a232c3b3e037755ccc14462
