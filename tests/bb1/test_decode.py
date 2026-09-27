"""Tests for reading a barcode the way the first Barcode Battler reads it."""

import pytest

from maeyomi.bb1.decode import decode_first
from maeyomi.decoder.errors import CheckDigitError
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType


def test_the_bundled_hero_reads_as_the_wiki_lists_it() -> None:
    card = decode_first("0120401154185")

    assert card.read_type is ReadType.FRONT
    assert (card.hp, card.st, card.df) == (1200, 400, 100)
    assert (card.race, card.job, card.dx) == (Race.ANIMAL, 5, 4)
    assert card.flag.code == 18
    assert card.flag.description == "Hero"


def test_a_front_read_fighter_never_gains_a_high_health_bonus() -> None:
    card = decode_first("1857762298133")

    assert (card.hp, card.st, card.df) == (18500, 7700, 6200)


@pytest.mark.parametrize(
    ("code", "race", "carried"),
    [
        ("0000700610110", Race.WEAPON, (0, 700, 0)),
        ("0000014804007", Race.ARMOUR, (0, 0, 1400)),
        ("0410000900000", Race.SUPPORT_ITEM, (4100, 0, 0)),
    ],
)
def test_an_item_carries_only_its_own_number(
    code: str, race: Race, carried: tuple[int, int, int]
) -> None:
    card = decode_first(code)

    assert card.race is race
    assert (card.hp, card.st, card.df) == carried
    assert card.dx is None


def test_a_high_leading_digit_makes_an_enemy_read_from_the_back() -> None:
    card = decode_first("4902102072618")

    assert card.read_type is ReadType.BACK
    assert (card.hp, card.st, card.df) == (7200, 1600, 100)
    assert (card.race, card.dx, card.job) == (None, None, 2)
    assert card.flag.code == 8


def test_zero_health_and_zero_defence_digits_read_as_their_floors() -> None:
    card = decode_first("4000000000006")

    assert (card.hp, card.st, card.df) == (10000, 1000, 100)


def test_an_eight_digit_code_reads_its_last_five_digits_the_same_way() -> None:
    card = decode_first("05017447")

    assert card.read_type is ReadType.BACK
    assert (card.hp, card.st, card.df) == (1700, 1400, 400)
    assert card.flag.code == 7


def test_a_wrong_check_digit_is_refused_as_on_the_second_device() -> None:
    with pytest.raises(CheckDigitError):
        decode_first("0120401154184")
