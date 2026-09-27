"""Tests for the devices a card can be made for."""

import re

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


def test_no_device_name_uses_a_roman_numeral() -> None:
    for device in Device:
        assert not re.search(r"\bII\b|Ⅱ|²", device.english + device.japanese)


def test_only_datach_dragon_ball_z_is_a_game() -> None:
    assert [device for device in Device if device.is_game] == [Device.DATACH_DBZ]


def test_the_machines_are_named_with_arabic_numerals() -> None:
    assert Device.DOUBLE.english == "Barcode Battler 2 Double"
    assert Device.DOUBLE.japanese == "バーコードバトラー2 ダブル"
