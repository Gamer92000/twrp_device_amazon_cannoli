#!/sbin/sh
exec >>/tmp/cannoli-usb.log 2>&1
echo "Binding Cannoli TWRP ADB"
for udc in /sys/class/udc/*; do
    [ -e "$udc" ] || continue
    echo "${udc##*/}" > /config/usb_gadget/g1/UDC
done
