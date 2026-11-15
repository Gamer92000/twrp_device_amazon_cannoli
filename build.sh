#!/bin/bash
set -eo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd)
: "${TWRP_TREE:=$ROOT/work/twrp}"
: "${JOBS:=4}"
: "${STOCK_IMAGES:?Set STOCK_IMAGES to the extracted 8349 images directory}"
if [ ! -d "$TWRP_TREE/.repo" ]; then
 mkdir -p "$TWRP_TREE"
 mkdir -p "$ROOT/work/manifest"
 cp "$ROOT/manifests/pinned.xml" "$ROOT/work/manifest/default.xml"
 git -C "$ROOT/work/manifest" init -q
 git -C "$ROOT/work/manifest" add default.xml
 git -C "$ROOT/work/manifest" -c user.name=Builder -c user.email=builder@localhost commit -qm 'Pinned TWRP source'
 (cd "$TWRP_TREE" && repo init -u "$ROOT/work/manifest" --depth=1 && repo sync -c -j"$JOBS")
fi
python3 "$ROOT/verify_sources.py" "$TWRP_TREE"
for mapping in 'build/make:build-make.patch' 'build/soong:build-soong.patch' 'bootable/recovery:headless.patch'; do
 target=${mapping%:*};patch=${mapping#*:}
 if git -C "$TWRP_TREE/$target" apply --check "$ROOT/patches/$patch"; then
  git -C "$TWRP_TREE/$target" apply "$ROOT/patches/$patch"
 else
  git -C "$TWRP_TREE/$target" apply --reverse --check "$ROOT/patches/$patch"
 fi
done
mkdir -p "$TWRP_TREE/device/amazon/cannoli/prebuilts" "$TWRP_TREE/.host-compat/lib"
DEVICE_TREE="$TWRP_TREE/device/amazon/cannoli"
if [ "$ROOT" != "$(cd "$DEVICE_TREE" && pwd)" ]; then
 for file in AndroidProducts.mk BoardConfig.mk omni_cannoli.mk vendorsetup.sh; do
  cp -a "$ROOT/$file" "$DEVICE_TREE/$file"
 done
 cp -a "$ROOT/recovery/." "$DEVICE_TREE/recovery/"
fi
python3 - "$ROOT" "$TWRP_TREE" "$STOCK_IMAGES" <<'PY'
import sys
from pathlib import Path
root,tree,images=map(Path,sys.argv[1:]);sys.path.insert(0,str(root))
from cannoli_twrp.fit import Fit
from cannoli_twrp.images import verified, STOCK
boot=Fit(verified(images/'boot.img', STOCK['boot.img']))
(tree/'device/amazon/cannoli/prebuilts/zImage').write_bytes(boot.prop('/images/kernel-1','data'))
PY
for library in tinfo ncurses; do
 ln -sfn "$TWRP_TREE/prebuilts/gcc/linux-x86/host/x86_64-linux-glibc2.15-4.8/sysroot/usr/lib/lib${library}.so.5.9" "$TWRP_TREE/.host-compat/lib/lib${library}.so.5"
done
export LD_LIBRARY_PATH="$TWRP_TREE/.host-compat/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LC_ALL=C
if [ ! -x "$TWRP_TREE/.host-compat/python2/bin/python2.7" ]; then
 curl -fL https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz \
  -o "$TWRP_TREE/.host-compat/Python-2.7.18.tgz"
 (cd "$TWRP_TREE/.host-compat" && \
  echo 'da3080e3b488f648a3d7a4560ddee895284c3380b11d6de75edb986526b9a814  Python-2.7.18.tgz' | sha256sum -c - && \
  tar xzf Python-2.7.18.tgz && cd Python-2.7.18 && \
  CFLAGS="-O2 -std=gnu99" ./configure --prefix="$TWRP_TREE/.host-compat/python2" --without-ensurepip && \
  make -j"$JOBS" && make install)
fi
export PATH="$TWRP_TREE/.host-compat/python2/bin:$PATH"
python2.7 -c 'import zlib'
cd "$TWRP_TREE"
source build/envsetup.sh
lunch omni_cannoli-eng
make -j"$JOBS" "$ANDROID_PRODUCT_OUT/ramdisk-recovery.img" \
 "$ANDROID_PRODUCT_OUT/system/lib/libminuitwrp.so"
printf '\nRecovery built. Run python3 -m cannoli_twrp.pack with artifacts from %s.\n' "$ANDROID_PRODUCT_OUT"
