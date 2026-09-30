"""Tests that every repaired transcription is the only repair its published stats allow.

A transcription whose check digit does not match has one mistyped digit. Each
of the twelve other digits, and the check digit itself, has exactly one value
that makes the code valid again, so a code has thirteen candidate repairs. The
source also publishes each card's numbers, and a repair is kept only when it is
the one candidate the card's own device reads as those numbers.
"""

import json
from importlib import resources
from typing import Final, NamedTuple, NotRequired, TypedDict, cast

import pytest

from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.official.catalogue import OfficialSet, official_cards, official_catalogue
from maeyomi.registry import readable_as

EAN_13_BODY: Final = 12
DIGITS: Final = "0123456789"


class Repair(NamedTuple):
    name: str
    official_set: OfficialSet
    transcribed: str
    repaired: str
    published: dict[str, int]


class CorrectionRecord(TypedDict):
    barcode: str
    published: dict[str, int]


class CardRecord(TypedDict):
    barcode: str
    name: str
    set: str
    correction: NotRequired[CorrectionRecord]


def _repair_of(entry: CardRecord, correction: CorrectionRecord) -> Repair:
    return Repair(
        name=entry["name"],
        official_set=OfficialSet(entry["set"]),
        transcribed=entry["barcode"],
        repaired=correction["barcode"],
        published=correction["published"],
    )


_CARDS: Final = cast(
    "list[CardRecord]",
    json.loads(resources.files("maeyomi.official").joinpath("cards.json").read_text("utf-8"))[
        "cards"
    ],
)
STAND_INS: Final = {entry["barcode"] for entry in _CARDS if "stand_in" in entry}
REPAIRS: Final = [
    _repair_of(entry, entry["correction"]) for entry in _CARDS if "correction" in entry
]


def is_valid(code: str) -> bool:
    return str(expected_check_digit(code[:EAN_13_BODY])) == code[EAN_13_BODY]


def repairs(code: str) -> list[str]:
    candidates = (
        code[:index] + digit + code[index + 1 :]
        for index in range(len(code))
        for digit in DIGITS
        if digit != code[index]
    )
    return [candidate for candidate in candidates if is_valid(candidate)]


def reading(official_set: OfficialSet, code: str) -> dict[str, object] | None:
    card = readable_as(official_set.device, code)
    if card is None:
        return None
    power = getattr(card, "special" if hasattr(card, "special") else "flag", None)
    return {
        "hp": getattr(card, "hp", None),
        "st": getattr(card, "st", None),
        "df": getattr(card, "df", None),
        "speed": getattr(card, "speed" if hasattr(card, "speed") else "dx", None),
        "race": getattr(getattr(card, "race", None), "value", None),
        "job": getattr(card, "job", None),
        "power": getattr(power, "code", None),
    }


def test_the_four_known_typos_are_repaired() -> None:
    assert len(REPAIRS) == 4


@pytest.mark.parametrize("repair", REPAIRS, ids=lambda repair: repair.name)
def test_the_published_barcode_fails_its_check_digit(repair: Repair) -> None:
    assert not is_valid(repair.transcribed)


@pytest.mark.parametrize("repair", REPAIRS, ids=lambda repair: repair.name)
def test_the_repair_changes_one_digit(repair: Repair) -> None:
    pairs = zip(repair.transcribed, repair.repaired, strict=True)

    changed = [pair for pair in pairs if pair[0] != pair[1]]

    assert len(changed) == 1


@pytest.mark.parametrize("repair", REPAIRS, ids=lambda repair: repair.name)
def test_the_repair_is_the_only_one_that_reads_as_the_published_card(repair: Repair) -> None:
    candidates = repairs(repair.transcribed)

    matching = [
        code for code in candidates if reading(repair.official_set, code) == repair.published
    ]

    assert matching == [repair.repaired]


@pytest.mark.parametrize("repair", REPAIRS, ids=lambda repair: repair.name)
def test_the_repaired_card_is_offered_for_printing(repair: Repair) -> None:
    printed = {card.barcode for card in official_cards(repair.official_set)}

    assert repair.repaired in printed


def test_every_repair_keeps_the_digits_the_source_published() -> None:
    kept = {card.transcribed for card in official_catalogue() if card.transcribed != card.barcode}

    assert kept == {repair.transcribed for repair in REPAIRS} | STAND_INS
