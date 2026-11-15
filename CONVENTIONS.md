# Repository conventions

R0rt1z2's Amazon Echo repositories are the reference for this layout.
The comparison below was checked against his GitHub sources on 2026-11-13.

| His example | Cannoli implementation |
| --- | --- |
| [`twrp_device_amazon_cronos`][cronos] and `twrp_device_amazon_biscuit` name device-specific recovery repos. | `twrp_device_amazon_cannoli` uses the same naming pattern. |
| Cronos has `AndroidProducts.mk`, `BoardConfig.mk`, `omni_cronos.mk`, `vendorsetup.sh` and `recovery/` at the repo root. | Cannoli has the corresponding files at its root, staged into `device/amazon/cannoli`. |
| Cronos selects `omni_cronos-eng` and `RECOVERY_VARIANT := twrp`. | Cannoli retains `omni_cannoli-eng` and its verified TWRP settings. |
| [`amonet`][amonet] keeps the unlock chain separate from recovery trees. | Firebreak installs; the recovery repo builds TWRP; `cannoli-os-builder` assembles rooted Fire OS. |
| The amonet README lists devices, codenames and device-specific XDA installation links. | Both READMEs list the supported device/build and link to the Firebreak installation guide. No Cannoli XDA thread exists in this project yet. |
| His [LineageOS release script][ota] uploads artifacts to GitHub Releases and tracks download metadata separately. | Source stays in Git; future release notes will identify source revisions, artifacts and checksums. No release is published by the build command. |

## Device-specific differences

The naming and root tree layout follow his example; hardware configuration
must remain Cannoli-specific. His Cronos tree targets MT8163 with a screen
and an amonet boot chain. Cannoli uses MT8519, NAND UBI and headless recovery.
Copying Cronos partition sizes, kernel offsets, display flags, `TW_AMONET`
or installation commands would be incorrect.

The Cronos tree includes a prebuilt kernel. Cannoli instead extracts its
hash-verified kernel from the stock OTA linked by FTVDB. `prebuilts/` is
ignored. The pinned manifest and offline packaging helpers remain alongside
our device tree because Cannoli needs a stock FIT with a replacement ramdisk.
This is an unofficial port; it is not maintained or endorsed by R0rt1z2.

The OS repository is a stock Fire OS repacker, not a LineageOS device tree.
His LineageOS OTA script is evidence for separating releases from source,
not a compatible build or update implementation for Cannoli. Its automatic
upload and OTA behavior is not copied. Device-specific recovery serials and
host public ADB keys make our completed bundles local build outputs.

Each builder runs independently. `recovery.json` carries the serial, build,
size and hash between them; Firebreak consumes the final format-1 bundle.
Small FIT/CPIO and OTA helpers remain vendored so a build does not require
an installer checkout or a private Git package dependency.

## Supporting references

[TeamWin's compilation FAQ][teamwin] describes minimal manifests and device
trees. Its [maintainer process][maintainer] requires a device tree and
working-device validation for official inclusion. The
[OmniROM compilation guide][omni] documents the source-manifest approach.

R0rt1z2's amonet README directly links his
[Cronos XDA thread][xda]. Direct forum access returned 502 during this
review, so the comparison uses his GitHub code and documentation. We are
following his observed example, not claiming an XDA-wide mandatory standard.
See [the release process](RELEASING.md) for future publication.

[cronos]: https://github.com/R0rt1z2/twrp_device_amazon_cronos/tree/20f00d86d36fc1e80a232c3b3e037755ccc14462
[amonet]: https://github.com/R0rt1z2/amonet/tree/d6179b8a2ba45fb641acc38b1cf3e848e8ff235d
[ota]: https://github.com/R0rt1z2/OTA/blob/e94ec6b117f534eaf2c799fe47d00076b9603cd9/scripts/release.sh
[teamwin]: https://twrp.me/faq/howtocompiletwrp.html
[maintainer]: https://twrp.me/faq/OfficialMaintainer.html
[omni]: https://github.com/omnirom/android_bootable_recovery/wiki/%5BDEV%5DHow-to-compile-TWRP-touch-recovery
[xda]: https://xdaforums.com/t/unlock-root-twrp-unbrick-amazon-echo-show-5-2nd-gen-2021-cronos.4772596/
