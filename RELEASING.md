# Release process

Building does not publish sources, create
a GitHub release or post to XDA. The model for eventual publication is
R0rt1z2's separation of device sources, downloadable artifacts and
[device-specific installation threads](https://github.com/R0rt1z2/amonet/tree/mt8163-echo-show).

When preparing a public source release, identify the exact source commit
and pinned manifest, supported device and stock build, build commands,
known limitations and validation results. Link the matching recovery source,
OS source, Firebreak installer and FTVDB stock record. Retain existing
licenses and credits. Record changes against the preceding release.

If downloadable artifacts are later released, attach them to the matching
GitHub release with their sizes and SHA-256 checksums; keep them out of Git.
Publish only artifacts intentionally built for distribution. Current recovery
images contain a target USB serial and OS bundles contain a trusted host's
public ADB key, so a maintainer's local bundle is not a generic release image.

An eventual XDA opening post should identify Cannoli/NS6575/8349, point to
those exact sources and downloads, and link the installation and restore
guide. Include what works, untested operations, changes and credits. The
current guide documents the replacement of B before backup and the limits
of restoring A. Link the real thread from the supported-device table once
one is published; until then the Firebreak guide is the installation entry.

This describes future publication. No XDA thread or binary release is
claimed by the current source repositories.
