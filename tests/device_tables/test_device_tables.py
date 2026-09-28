"""Tests for the per-device tables the command line prints."""

from maeyomi.cli.device_tables import (
    ability_lines,
    kind_lines,
    official_lines,
    official_sets,
    product_lines,
)
from maeyomi.models.device import Device
from maeyomi.official.catalogue import OfficialSet
from maeyomi.products.japan import japanese_products


def test_only_the_second_barcode_battler_describes_its_race_bonuses() -> None:
    assert any(line.startswith("   Machines.") for line in kind_lines(Device.BB2))
    assert not any(line.startswith("   Machines.") for line in kind_lines(Device.BB1))


def test_the_double_says_a_seven_read_card_has_no_race() -> None:
    assert "7-read" in kind_lines(Device.DOUBLE)[-1]


def test_the_first_barcode_battler_prints_flags_not_powers() -> None:
    assert "18  Hero" in ability_lines(Device.BB1)


def test_every_table_has_a_line_per_code() -> None:
    assert len(ability_lines(Device.BB2)) == 100
    assert len(ability_lines(Device.DOUBLE)) == 100


def test_a_product_line_uses_the_devices_reading() -> None:
    lines = product_lines(japanese_products()[:3], Device.DATACH_DBZ)

    assert lines[-1] == "3 product(s)"
    assert "Robot" not in "".join(lines)


def test_no_device_means_every_set() -> None:
    assert official_sets(None) == tuple(OfficialSet)
    assert official_lines(None)[len(OfficialSet)].strip().startswith("1336")


def test_a_product_the_game_cannot_read_says_so_in_its_line() -> None:
    shelf = [p for p in japanese_products() if p.barcode == "4974111777266"]

    lines = product_lines(shelf, Device.DATACH_DBZ)

    assert lines[0].endswith("The game's reader cannot read this barcode")


def test_a_datach_game_lists_every_card_it_reads_by_number_and_kind() -> None:
    lines = kind_lines(Device.DATACH_ULTRAMAN)

    assert len(lines) == 51
    assert "  3  fighter  Zoffy / ゾフィー" in lines
    assert " 33  item     Father of Ultra / ウルトラのちち" in lines


def test_a_datach_game_says_it_has_no_code_table() -> None:
    assert ability_lines(Device.DATACH_ULTRAMAN) == [
        "Datach Ultraman Club has no two-digit code; its cards carry no special ability"
    ]
