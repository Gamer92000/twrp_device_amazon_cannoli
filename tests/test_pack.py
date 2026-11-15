import pytest

from cannoli_twrp.images import recovery


def test_recovery_refuses_wrong_stock(tmp_path):
    (tmp_path / "boot.img").write_bytes(b"wrong stock firmware")
    with pytest.raises(ValueError, match="Checksum mismatch"):
        recovery(
            tmp_path, tmp_path / "ramdisk", tmp_path / "graphics", "TEST1234", tmp_path
        )
    assert not (tmp_path / "boot_b.img").exists()


@pytest.mark.parametrize("serial", ["", "a", "bad serial", "x" * 65, "test;reboot"])
def test_recovery_refuses_unsafe_usb_serial(tmp_path, serial):
    with pytest.raises(ValueError, match="Invalid USB serial"):
        recovery(tmp_path, tmp_path, tmp_path, serial, tmp_path)
    assert not (tmp_path / "boot_b.img").exists()
