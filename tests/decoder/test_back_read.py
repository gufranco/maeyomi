"""Tests for the back reading, which rotates digits rather than slicing them."""

import itertools

import pytest

from barcode_battler.decoder.back_read import read_back
from barcode_battler.models.race import Race
from barcode_battler.models.read_type import ReadType


def code_with(**digits: int) -> str:
    body = ["0"] * 13
    for index, value in digits.items():
        body[int(index.removeprefix("d"))] = str(value)
    return "".join(body)


def test_a_fighter_is_decoded_from_the_rotated_digits() -> None:
    character = read_back(code_with(d12=3, d11=9, d10=4, d9=2, d8=1, d5=7))

    assert character.read_type is ReadType.BACK
    assert character.race is Race.BIRD
    assert character.hp == 44200
    assert character.st == 11700
    assert character.df == 9800
    assert character.job == 7


def test_a_magician_job_grants_ten_magic_points() -> None:
    character = read_back(code_with(d12=3, d5=7))

    assert character.mp == 10
    assert character.pp == 5


def test_hit_points_never_exceed_the_published_back_read_ceiling() -> None:
    peak = max(read_back(code_with(d12=0, d11=high, d10=9, d9=9)).hp for high in range(10))

    assert peak == 49900


def test_strength_never_exceeds_the_published_back_read_ceiling() -> None:
    peak = max(
        read_back(code_with(d12=0, d10=mid, d9=low)).st
        for mid, low in itertools.product(range(10), repeat=2)
    )

    assert peak == 11900


def test_defence_never_exceeds_the_published_back_read_ceiling() -> None:
    peak = max(
        read_back(code_with(d12=0, d9=low, d8=lower)).df
        for low, lower in itertools.product(range(10), repeat=2)
    )

    assert peak == 9900


@pytest.mark.parametrize(
    ("mid_digit", "expected_tens"),
    [(0, 7), (2, 9), (3, 10), (4, 11), (5, 2), (9, 6)],
)
def test_the_strength_tens_digit_wraps_above_eleven_not_above_nine(
    mid_digit: int, expected_tens: int
) -> None:
    character = read_back(code_with(d12=0, d10=mid_digit))

    assert character.st // 1000 == expected_tens


@pytest.mark.parametrize(
    ("selector", "offset"),
    [(0, 0), (3, 0), (4, 10), (7, 10), (8, 20), (9, 20)],
)
def test_the_special_ability_prefix_follows_the_selector_digit(selector: int, offset: int) -> None:
    character = read_back(code_with(d12=0, d8=selector, d10=7))

    assert character.special.code == offset + 7


def test_a_back_read_special_ability_never_exceeds_twenty_nine() -> None:
    peak = max(
        read_back(code_with(d12=0, d8=selector, d10=value)).special.code
        for selector, value in itertools.product(range(10), repeat=2)
    )

    assert peak == 29


def test_an_eight_digit_code_uses_the_shifted_layout_and_a_fixed_job() -> None:
    character = read_back("49123456")

    assert character.read_type is ReadType.BACK
    assert character.race is Race.WEAPON
    assert character.job == 0


def test_an_eight_digit_fighter_carries_the_fixed_job_of_four() -> None:
    character = read_back("00000000")

    assert character.race is Race.MECHANICAL
    assert character.job == 4


def test_a_weapon_prefix_is_selected_by_its_marker_digit() -> None:
    prefixes = {marker: read_back(code_with(d12=6, d10=marker)).st // 1000 for marker in range(10)}

    assert prefixes == {0: 2, 1: 2, 2: 2, 3: 3, 4: 3, 5: 1, 6: 1, 7: 1, 8: 1, 9: 2}


def test_armour_with_a_bare_marker_has_no_tens_digit() -> None:
    character = read_back(code_with(d12=8, d9=3, d8=0))

    assert character.df == 700
