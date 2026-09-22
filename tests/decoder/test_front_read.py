"""Tests for the front reading, which maps fixed digit slices onto attributes."""

import pytest

from maeyomi.decoder.front_read import read_front
from maeyomi.decoder.read_type import classify_read_type
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType


def test_a_fighter_maps_every_slice() -> None:
    character = read_front("0401207237501")

    assert character.read_type is ReadType.FRONT
    assert (character.hp, character.st, character.df) == (4000, 1200, 700)
    assert character.race is Race.AQUATIC
    assert character.job == 3
    assert character.speed == 7
    assert character.special.code == 50


def test_a_warrior_carries_no_magic_points_and_five_power_points() -> None:
    character = read_front("0401207237501")

    assert (character.pp, character.mp) == (5, 0)


def test_a_magician_starts_with_ten_magic_points() -> None:
    character = read_front("0341011384506")

    assert character.job == 8
    assert character.mp == 10


@pytest.mark.parametrize(
    ("code", "race", "st", "df"),
    [
        ("0000600602017", Race.WEAPON, 600, 0),
        ("0001400500022", Race.SINGLE_USE_WEAPON, 1400, 0),
        ("0000010802212", Race.ARMOUR, 0, 1000),
        ("0000019700328", Race.SINGLE_USE_ARMOUR, 0, 1900),
    ],
)
def test_weapons_and_armour_carry_a_single_modifier(
    code: str, race: Race, st: int, df: int
) -> None:
    item = read_front(code)

    assert item.race is race
    assert (item.st, item.df) == (st, df)


def test_a_support_item_with_a_low_sub_type_carries_hit_points() -> None:
    item = read_front("0120000905140")

    assert item.race is Race.SUPPORT_ITEM
    assert item.hp == 1200


def test_a_support_item_sub_type_seven_carries_power_points() -> None:
    item = read_front("0000300970140")

    assert (item.pp, item.hp, item.st) == (3, 0, 0)


def test_a_support_item_sub_type_eight_carries_magic_points() -> None:
    item = read_front("0000005980123")

    assert (item.mp, item.hp, item.df) == (5, 0, 0)


@pytest.mark.parametrize("code", ["0000019700328"])
def test_an_item_whose_ability_flips_its_sign_is_flagged_as_volatile(code: str) -> None:
    item = read_front(code)

    assert item.special.code == 32
    assert item.sign_is_volatile


def test_an_item_has_no_speed() -> None:
    item = read_front("0000600602017")

    assert item.speed is None


def test_race_two_above_the_high_hp_threshold_gains_one_hundred_on_both_stats() -> None:
    character = read_front("2091010255007")

    assert character.hp == 20900
    assert (character.st, character.df) == (11000, 11000)


def test_a_high_hp_front_read_needs_the_marker_so_its_third_digit_is_always_nine() -> None:
    assert classify_read_type("2091010255007") is ReadType.FRONT
