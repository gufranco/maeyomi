"""The decoder judged against recorded real cards.

Two fixture sets. `wiki_cards.json` carries published attributes for every card
list on wikiwiki.jp. `simulator_corpus.json` carries barcodes only, taken from
the MIT simulator's own card XML, and exercises decoding without asserting
values.

One page is excluded by name. The `正伝3 破壊神伝` list documents cards whose
printed values do not reproduce under any reading this decoder implements, and
whose HP exceeds the published front-read arrangement for their leading digit.
Excluding it is recorded here rather than silently filtered, and the test below
asserts that the exclusion is still needed rather than assuming it.
"""

import json
import pathlib
from typing import Any

import pytest

from maeyomi.decoder.decode import decode
from maeyomi.decoder.errors import BarcodeError
from maeyomi.models.character import DISPLAY_SCALE, BarcodeBattlerCharacter
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType

FIXTURES = pathlib.Path(__file__).parent.parent / "fixtures"
UNSUPPORTED_PAGE = "正伝3 破壊神伝 カードリスト"

KNOWN_BAD_CHECK_DIGITS = frozenset(
    {
        "3966666425072",
        "1162864348006",
        "1273634357000",
        "1444764195221",
        "1784651464171",
    }
)


def load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def wiki_cards() -> list[dict[str, Any]]:
    return load("wiki_cards.json")["cards"]


def supported_cards() -> list[dict[str, Any]]:
    return [
        card
        for card in wiki_cards()
        if card["source_page"] != UNSUPPORTED_PAGE and card["barcode"] not in KNOWN_BAD_CHECK_DIGITS
    ]


def ids(cards: list[dict[str, Any]]) -> list[str]:
    return [f"{card['barcode']}-{card['type_no'] or card['name']}" for card in cards]


CARDS = supported_cards()


def test_the_fixture_set_is_large_enough_to_be_evidence() -> None:
    assert len(CARDS) >= 180


@pytest.mark.parametrize("card", CARDS, ids=ids(CARDS))
def test_every_published_card_decodes_to_its_published_attributes(
    card: dict[str, Any],
) -> None:
    decoded = decode(card["barcode"])

    assert abs(decoded.hp) == card["hp"]
    assert abs(_strength_of(decoded)) == card["st"]
    assert abs(_defence_of(decoded)) == card["df"]
    assert decoded.race == card["race"]
    assert decoded.special.code == card["special"]


@pytest.mark.parametrize("card", CARDS, ids=ids(CARDS))
def test_the_job_digit_matches_where_the_card_list_publishes_one(
    card: dict[str, Any],
) -> None:
    decoded = decode(card["barcode"])

    assert card["job"] is None or decoded.job == card["job"]


def test_speed_matches_the_published_dx_column_for_every_fighter() -> None:
    fighters = [card for card in CARDS if card["dx"] is not None and Race(card["race"]).is_fighter]

    mismatched = [
        card["barcode"] for card in fighters if decode(card["barcode"]).speed != card["dx"]
    ]

    assert len(fighters) >= 100
    assert mismatched == []


def test_the_excluded_page_still_fails_so_the_exclusion_is_still_earned() -> None:
    excluded = [card for card in wiki_cards() if card["source_page"] == UNSUPPORTED_PAGE]

    agreeing = [card for card in excluded if _matches(card)]

    assert excluded
    assert len(agreeing) < len(excluded)


def test_the_recorded_bad_check_digits_are_genuinely_bad() -> None:
    for barcode in KNOWN_BAD_CHECK_DIGITS:
        with pytest.raises(BarcodeError):
            decode(barcode)


def test_every_barcode_in_the_simulator_corpus_decodes() -> None:
    corpus = load("simulator_corpus.json")["cards"]

    failures = [
        card["barcode"]
        for card in corpus
        if len(card["barcode"]) in (8, 13) and not _decodes(card["barcode"])
    ]

    assert len(corpus) >= 150
    assert failures == []


def test_the_simulator_corpus_exercises_both_readings_and_every_race() -> None:
    corpus = [card for card in load("simulator_corpus.json")["cards"] if _decodes(card["barcode"])]

    decoded = [decode(card["barcode"]) for card in corpus]

    assert {character.read_type for character in decoded} == set(ReadType)
    assert {character.race for character in decoded} == set(Race)


def _strength_of(character: BarcodeBattlerCharacter) -> int:
    if character.race is Race.SUPPORT_ITEM and character.pp:
        return character.pp * DISPLAY_SCALE
    return character.st


def _defence_of(character: BarcodeBattlerCharacter) -> int:
    if character.race is Race.SUPPORT_ITEM and character.mp:
        return character.mp * DISPLAY_SCALE
    return character.df


def _matches(card: dict[str, Any]) -> bool:
    try:
        decoded = decode(card["barcode"])
    except BarcodeError:
        return False
    return (
        abs(decoded.hp) == card["hp"]
        and abs(decoded.st) == card["st"]
        and abs(decoded.df) == card["df"]
        and decoded.race == card["race"]
    )


def _decodes(barcode: str) -> bool:
    try:
        decode(barcode)
    except BarcodeError:
        return False
    return True
