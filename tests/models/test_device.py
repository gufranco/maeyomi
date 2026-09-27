"""Tests for the devices a card can be made for."""

from maeyomi.models.device import Device


def test_every_device_has_a_short_key_and_a_name_in_both_languages() -> None:
    for device in Device:
        assert device.value.isascii()
        assert device.english
        assert device.japanese


def test_the_second_device_is_the_default_key() -> None:
    assert Device("bb2") is Device.BB2


def test_a_device_name_fits_a_menu() -> None:
    assert max(len(device.english) for device in Device) <= 30
