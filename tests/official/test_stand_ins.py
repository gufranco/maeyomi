"""Tests for a listed card whose numbers no barcode the machine reads can carry.

A stand-in replaces a transcription that is not a barcode at all. It reads as
every number the source publishes for the card except those the machine cannot
hold, and each of those is the nearest value it can.
"""

import json
from importlib import resources
from typing import Final, NotRequired, TypedDict, cast

import pytest

from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.models.character import BarcodeBattlerCharacter
from maeyomi.official.catalogue import OfficialSet, official_cards
from maeyomi.registry import readable_as

EAN_13_BODY: Final = 12
FRONT_READ_CEILING: Final = 20000
FRONT_READ_STEP: Final = 1000
FRONT_READ_ENDING: Final = 900


class StandIn(TypedDict):
    barcode: str
    published: dict[str, int]


class CardRecord(TypedDict):
    barcode: str
    name: str
    set: str
    stand_in: NotRequired[StandIn]


CARDS: Final = cast(
    "list[CardRecord]",
    json.loads(resources.files("maeyomi.official").joinpath("cards.json").read_text("utf-8"))[
        "cards"
    ],
)
STAND_INS: Final = [(card, card["stand_in"]) for card in CARDS if "stand_in" in card]


def reading(card: CardRecord, code: str) -> dict[str, int]:
    read = readable_as(OfficialSet(card["set"]).device, code)
    assert isinstance(read, BarcodeBattlerCharacter)
    assert read.speed is not None
    return {
        "hp": read.hp,
        "st": read.st,
        "df": read.df,
        "speed": read.speed,
        "race": read.race.value,
        "job": read.job,
        "power": read.special.code,
    }


def nearest_hit_points(published: int) -> int:
    if published <= FRONT_READ_CEILING:
        return published
    below = published // FRONT_READ_STEP * FRONT_READ_STEP + FRONT_READ_ENDING
    candidates = (below - FRONT_READ_STEP, below)
    return min(candidates, key=lambda value: abs(value - published))


def test_ganglati_is_the_one_stand_in() -> None:
    assert [card["name"] for card, _ in STAND_INS] == ["ガングラティ"]


@pytest.mark.parametrize(("card", "stand_in"), STAND_INS, ids=str)
def test_the_transcription_is_not_a_barcode(card: CardRecord, stand_in: StandIn) -> None:
    code = card["barcode"]
    assert stand_in["barcode"] != code

    expected = str(expected_check_digit(code[:EAN_13_BODY]))

    assert expected != code[EAN_13_BODY]


@pytest.mark.parametrize(("card", "stand_in"), STAND_INS, ids=str)
def test_the_stand_in_reads_as_the_published_card_but_for_hit_points(
    card: CardRecord, stand_in: StandIn
) -> None:
    read = reading(card, stand_in["barcode"])

    published = stand_in["published"]
    assert {**read, "hp": published["hp"]} == published
    assert read["hp"] == nearest_hit_points(published["hp"])


@pytest.mark.parametrize(("card", "stand_in"), STAND_INS, ids=str)
def test_the_stand_in_is_offered_for_printing(card: CardRecord, stand_in: StandIn) -> None:
    printed = {listed.barcode for listed in official_cards(OfficialSet(card["set"]))}

    assert stand_in["barcode"] in printed
