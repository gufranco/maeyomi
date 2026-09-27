"""Tests for reading, building and cheating on any device through one entry point."""

import pytest

from maeyomi.bb1.card import FirstBattlerCard
from maeyomi.datach.dbz import DbzCard
from maeyomi.decoder.errors import BarcodeError
from maeyomi.double.card import DoubleCard
from maeyomi.models.card_request import CardRequest
from maeyomi.models.character import BarcodeBattlerCharacter
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType
from maeyomi.registry import DeviceChoice, build_as, cheat_as, device_named, read_as

GOKU = "0022248300117"


@pytest.mark.parametrize(
    ("device", "shape"),
    [
        (Device.BB2, BarcodeBattlerCharacter),
        (Device.BB1, FirstBattlerCard),
        (Device.DOUBLE, DoubleCard),
        (Device.DATACH_DBZ, DbzCard),
    ],
)
def test_one_barcode_reads_as_each_device_reads_it(device: Device, shape: type) -> None:
    assert isinstance(read_as(device, GOKU), shape)


@pytest.mark.parametrize("device", list(Device))
def test_every_device_refuses_a_code_whose_check_digit_is_wrong(device: Device) -> None:
    with pytest.raises(BarcodeError):
        read_as(device, "0022248300118")


def test_a_device_is_named_by_its_key() -> None:
    assert device_named(" DBZ ") is Device.DATACH_DBZ


def test_an_unknown_device_names_the_known_ones() -> None:
    with pytest.raises(ValueError, match="known devices: bb2, bb1, double, dbz"):
        device_named("gameboy")


def test_the_second_barcode_battler_builds_through_the_same_entry_point() -> None:
    outcome = build_as(Device.BB2, CardRequest(hp=Constraint.exactly(5000)), DeviceChoice())

    assert isinstance(outcome.card, BarcodeBattlerCharacter)
    assert outcome.card.hp == 5000


def test_the_second_barcode_battler_builds_a_back_read_when_asked() -> None:
    outcome = build_as(Device.BB2, CardRequest(race=Race.HUMAN), DeviceChoice(back_read=True))

    assert isinstance(outcome.card, BarcodeBattlerCharacter)
    assert outcome.card.read_type is ReadType.BACK


@pytest.mark.parametrize("device", list(Device))
def test_every_device_has_a_cheat(device: Device) -> None:
    assert cheat_as(device, None).name == "Maximus Cheatimus"
