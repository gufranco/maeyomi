"""Tests for reading a barcode the way the Barcode Battler II Double reads it."""

import json
from pathlib import Path
from typing import Final

import pytest

from maeyomi.decoder.decode import decode
from maeyomi.double.card import DoubleReading
from maeyomi.double.decode import decode_double, is_seven_read
from maeyomi.models.race import Race

FIXTURES: Final = Path(__file__).parent.parent / "fixtures" / "wiki_cards.json"
MAIN_STORY_THREE: Final = "正伝3 破壊神伝 カードリスト"


def main_story_three() -> list[dict[str, str | int | None]]:
    cards = json.loads(FIXTURES.read_text("utf-8"))["cards"]
    return [card for card in cards if card["source_page"] == MAIN_STORY_THREE]


def test_the_god_of_destruction_reads_with_the_seven_read() -> None:
    card = decode_double("7821818898978")

    assert card.reading is DoubleReading.SEVEN
    assert (card.hp, card.st, card.df) == (82700, 18800, 18900)
    assert (card.job, card.special.code) == (9, 27)
    assert (card.race, card.speed) == (Race.BIRD, None)


@pytest.mark.parametrize("entry", main_story_three(), ids=lambda entry: str(entry["barcode"]))
def test_every_main_story_three_card_reads_as_the_wiki_lists_it(
    entry: dict[str, str | int | None],
) -> None:
    card = decode_double(str(entry["barcode"]))

    assert (card.hp, card.st, card.df, card.job) == (
        entry["hp"],
        entry["st"],
        entry["df"],
        entry["job"],
    )
    assert card.special.code == entry["special"]
    assert card.race == entry["race"]


def test_the_list_holds_eleven_seven_read_cards_and_four_front_reads() -> None:
    readings = [decode_double(str(entry["barcode"])).reading for entry in main_story_three()]

    assert readings.count(DoubleReading.SEVEN) == 11
    assert readings.count(DoubleReading.FRONT) == 4


def test_a_code_without_both_markers_is_read_as_the_second_device_reads_it() -> None:
    card = decode_double("0451414388503")
    second = decode("0451414388503")

    assert card.reading is DoubleReading.FRONT
    assert (card.race, card.hp, card.st, card.df, card.speed) == (
        second.race,
        second.hp,
        second.st,
        second.df,
        second.speed,
    )


def test_a_back_read_leaves_speed_unknown_as_the_source_does() -> None:
    card = decode_double("4902102072618")

    assert card.reading is DoubleReading.FORTY_NINE
    assert card.speed is None
    assert card.race is Race.ARMOUR


@pytest.mark.parametrize(
    ("code", "expected"),
    [("7821818898978", True), ("7821818895977", False), ("0451414388503", False)],
)
def test_the_seven_read_needs_a_seven_first_and_an_eight_tenth(code: str, expected: bool) -> None:
    assert is_seven_read(code) is expected


def test_an_eight_digit_code_is_never_a_seven_read() -> None:
    assert not is_seven_read("75017484")


def test_a_seven_read_whose_eighth_digit_is_below_five_has_no_known_race() -> None:
    card = decode_double("7821818398973")

    assert card.race is None
