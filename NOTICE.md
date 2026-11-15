# Source provenance

This tooling was developed alongside the Cannoli rooting route in
[firebreak](https://github.com/Gamer92000/firebreak).
The original BSD-2-Clause notice is retained in `LICENSE.txt`.
The OTA extractor and its tests are adapted from Firebreak with standalone
hash/error/reporting helpers. The FIT/CPIO code retains its original behavior.

TeamWin, OmniROM, AOSP and
[minimal-manifest-twrp](https://github.com/minimal-manifest-twrp/platform_manifest_twrp_omni)
provide recovery sources and build infrastructure under their own licenses.
Patches to those sources retain the licensing of their respective upstreams;
the repository-level license does not relicense downloaded sources or binaries.
The pinned recovery manifest identifies exact upstream revisions.
Google supplies the NDK and emulator ADB daemon; topjohnwu's Magisk supplies
`magiskpolicy`. Amazon supplies the stock firmware and kernel through the
FTVDB-linked download. Their original terms and notices continue to apply.

The loader FIT construction follows the U-Boot/libfdt signed-region model
and the unsigned `hashed-nodes` issue described in
[CVE-2026-46728](https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves/2026/46xxx/CVE-2026-46728.json).
[The upstream fix](https://github.com/u-boot/u-boot/commit/2092322b31cc8b1f8c9e2e238d1043ae0637b241)
credits Apple SEAR, Simon Glass and Tom Rini. Firebreak and R0rt1z2's unlocks
informed the recovery-then-root flow; Bjoern Kerler's mtkclient and 981213's
mtk_uartboot supplied MediaTek protocol references.

The recovery repository name and root device-tree layout follow
[R0rt1z2's Cronos example](https://github.com/R0rt1z2/twrp_device_amazon_cronos/tree/20f00d86d36fc1e80a232c3b3e037755ccc14462).
This is structural guidance, not a claim that his device code supports
Cannoli or that he maintains this port. Cannoli's existing configuration
and license are retained.
