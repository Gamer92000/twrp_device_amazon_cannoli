# Validation

Validated on x86-64 Linux on 2026-11-13 during extraction from Firebreak PR #1.

- The OS preparer downloaded the 8349 OTA through the live FTVDB record and
  verified its SHA-256, all extracted stock images, NDK, Magisk policy tool
  and emulator ADB daemon. This used a new input directory.
- The TWRP preparer independently extracted and verified the boot image from
  a local copy of that pinned OTA.
- `build.sh` verified all 226 source-project HEADs against the pinned manifest
  and compiled the recovery ramdisk and headless graphics library into a
  fresh `OUT_DIR`. It reused the existing synced source checkout and cached
  Python 2.7 toolchain; a new network sync was not exercised.
- Recovery packaging produced `boot_b.img` and its serial/hash manifest.
  The OS builder accepted that artifact and built the full nine-image bundle
  with a synthetic validation serial, using the documented root build command.
- Firebreak's actual `load_bundle` accepted the finished format-1 bundle.
- Recovery and all five loader images matched the original builder byte for
  byte when given the same freshly compiled inputs and serial. The OS patch
  implementation is AST-identical to the PR head apart from import paths.
- Python 3.10 tests passed: 52 in the OS builder and 46 in the TWRP builder.
  Ruff checks/formatting and TWRP shell syntax checks passed.
- Firebreak's Linux Python 3.9.25 suite passed 1,372 tests, with four platform
  skips and the Apple-specific floor test deselected. All 57 covered runtime
  modules exceeded 90% line coverage (minimum 92.59%). Lint and package builds
  passed. The exact Apple Python 3.9.6 check belongs to Firebreak's macOS CI.

This validates the repository split and artifact handoff. No device was
flashed during this extraction. Prior hardware validation belongs to the
original Firebreak PR; this does not extend that hardware coverage or certify
generic TWRP operations on Cannoli NAND.

## R0rt1z2 layout follow-up

The recovery device tree was moved to the repository root to follow
R0rt1z2's Echo trees. All six device configuration files remain byte-identical
to the preceding commit and to the files staged by the revised build wrapper.
The wrapper completed an incremental recovery build from the same pinned
sources, packaging passed, and the OS builder accepted the resulting recovery
manifest and image. Recovery tests (46), lint and shell syntax passed.
Firebreak's documentation lint passed after updating the repository links.
No device was flashed for this layout change.
