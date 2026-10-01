"""Tests for Barcode Taisen Bardigun's barcode reading, against what the game hatched in MAME."""

import json
from pathlib import Path
from typing import Final

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_types import GameEntry, GameOrder
from maeyomi.decoder.check_digit import EAN_8_LENGTH, EAN_13_LENGTH
from maeyomi.decoder.errors import CheckDigitError
from maeyomi.gameboy.bardigun import (
    RANDOM_EGG,
    STAT_KEYS,
    TILE_KEYS,
    bardigun_entries,
    bardigun_named,
    bardigun_text,
    build_bardigun,
    decode_bardigun,
    strongest_bardigun,
)
from maeyomi.gameboy.bardigun_tables import STARTS
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device

FIXTURE: Final = Path(__file__).parent.parent / "fixtures" / "oracle" / "bardigun.json"
RECORDED: Final = json.loads(FIXTURE.read_text(encoding="utf-8"))["cards"]
TABLE_DIGIT: Final = {EAN_13_LENGTH: 10, EAN_8_LENGTH: 2}
FIXED: Final = [
    card for card in RECORDED if card["barcode"][TABLE_DIGIT[len(card["barcode"])]] in "1234567"
]
ANY: Final = Constraint.anything()
TAKORA: Final = "4902370501445"
CHIBISSHII: Final = 97


def order(ident: int | None) -> GameOrder:
    return GameOrder(ident, (ANY, ANY, ANY))


@pytest.mark.parametrize("card", FIXED, ids=lambda card: card["barcode"])
def test_every_fixed_code_hatches_what_the_game_hatched_in_mame(card: dict[str, object]) -> None:
    read = decode_bardigun(str(card["barcode"]))

    assert (read.kind, read.ident) == (GameKind.FIGHTER, card["species"])


@pytest.mark.parametrize("card", FIXED, ids=lambda card: card["barcode"])
def test_a_hatched_creature_starts_with_the_numbers_the_game_gave_it(
    card: dict[str, object],
) -> None:
    record = bytes.fromhex(str(card["record"]))

    read = decode_bardigun(str(card["barcode"]))

    assert tuple(stat.value for stat in read.stats) == tuple(record[17:22])


def test_the_fixture_covers_every_fixed_table_and_check_digit() -> None:
    covered = {
        (card["barcode"][10], card["barcode"][12])
        for card in FIXED
        if len(card["barcode"]) == EAN_13_LENGTH
    }

    assert len(covered) == 70


def test_the_fixture_reads_eight_digit_codes_from_their_third_and_first_digits() -> None:
    eight = [card for card in FIXED if len(card["barcode"]) == EAN_8_LENGTH]

    assert len(eight) == 15


def test_takora_hatches_from_its_barcode() -> None:
    card = decode_bardigun(TAKORA)

    assert bardigun_text(card).name == ("Takora", "タコラ")
    assert tuple(stat.key for stat in card.stats) == TILE_KEYS


@pytest.mark.parametrize("digit", "089")
def test_an_eleventh_digit_outside_the_tables_hatches_at_random(digit: str) -> None:
    body = f"4900000000{digit}0"
    code = next(f"{body}{last}" for last in range(10) if _valid(f"{body}{last}"))

    card = decode_bardigun(code)

    assert (card.kind, card.ident, card.stats) == (GameKind.HIDDEN, RANDOM_EGG, ())
    assert bardigun_text(card).name == ("A random Barloid", "なにが うまれるか わからない")


def test_an_eight_digit_code_hatches_from_its_third_and_first_digits() -> None:
    card = decode_bardigun("45678905")

    assert bardigun_text(card).name == ("Randaa", "ランダー")


def test_an_eight_digit_code_with_a_zero_third_digit_hatches_at_random() -> None:
    card = decode_bardigun("49000009")

    assert card.ident == RANDOM_EGG


def _valid(code: str) -> bool:
    try:
        decode_bardigun(code)
    except CheckDigitError:
        return False
    return True


def test_a_code_with_a_wrong_check_digit_is_refused() -> None:
    with pytest.raises(CheckDigitError):
        decode_bardigun("4902370501446")


@pytest.mark.parametrize("entry", bardigun_entries(), ids=lambda entry: entry.english)
def test_every_listed_creature_builds_and_reads_back_as_itself(entry: GameEntry) -> None:
    card = build_bardigun(order(entry.ident))

    assert card is not None
    assert decode_bardigun(card.barcode).ident == entry.ident


def test_thirty_five_creatures_can_be_hatched_on_purpose() -> None:
    assert len(bardigun_entries()) == 35


def test_a_creature_no_code_can_pin_builds_nothing() -> None:
    assert build_bardigun(order(160)) is None


def test_the_strongest_hatches_with_the_most_hp() -> None:
    card = strongest_bardigun()

    assert bardigun_text(card).name == ("Omame", "オマメ")
    assert max(STARTS[entry.ident][4] for entry in bardigun_entries()) == card.value("DHP")
    assert build_bardigun(order(None)) == card


def test_a_creature_card_says_what_it_hatches_with() -> None:
    card = decode_bardigun(TAKORA)

    text = bardigun_text(card)

    assert text.detail == ("Barloid number 14", "バーロイド 14ばん")
    assert text.power[0] == "Power 7, smarts 5, toughness 5, speed 5, HP 90"


def test_a_creature_is_found_by_name_or_number() -> None:
    assert bardigun_named("Chibisshii") == CHIBISSHII
    assert bardigun_named("チビッシー") == CHIBISSHII
    assert bardigun_named("97") == CHIBISSHII
    with pytest.raises(ValueError, match="Bardigun"):
        bardigun_named("Pikachu")


def test_the_game_takes_no_numbers_to_slide() -> None:
    assert STAT_KEYS == ()


def test_a_card_belongs_to_the_bardigun() -> None:
    assert decode_bardigun(TAKORA).game is Device.BARDIGUN
