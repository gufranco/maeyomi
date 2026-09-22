"""Tests for the officially released cards, as transcribed by the community."""

import pytest

from maeyomi.decoder.decode import decode
from maeyomi.official.catalogue import (
    OfficialSet,
    official_cards,
    official_catalogue,
    rejected_transcriptions,
)

KNOWN_BAD_CHECK_DIGITS = {
    "1162864348006",
    "1273634357000",
    "1784651464171",
    "1444764195221",
    "3966666425072",
}


def test_the_catalogue_holds_every_transcribed_barcode_once() -> None:
    barcodes = [card.barcode for card in official_catalogue()]

    assert len(barcodes) == 577
    assert len(set(barcodes)) == len(barcodes)


def test_every_card_names_the_page_it_came_from() -> None:
    for card in official_catalogue():
        assert card.source_url.startswith("https://wikiwiki.jp/barcode/")
        assert card.name


def test_every_set_has_an_english_title() -> None:
    for official_set in OfficialSet:
        assert official_set.english
        assert official_set.english.isascii()


def test_every_card_belongs_to_a_known_set() -> None:
    sets = {card.official_set for card in official_catalogue()}

    assert sets == set(OfficialSet)


def test_a_transcription_with_a_wrong_check_digit_is_rejected_rather_than_repaired() -> None:
    rejected = {card.barcode for card in rejected_transcriptions()}

    assert rejected == KNOWN_BAD_CHECK_DIGITS


def test_every_printable_card_decodes_to_the_character_it_carries() -> None:
    for card in official_cards():
        assert decode(card.barcode) == card.character


def test_the_printable_cards_are_every_transcription_that_decodes() -> None:
    assert len(official_cards()) == 577 - len(KNOWN_BAD_CHECK_DIGITS)


@pytest.mark.parametrize("official_set", list(OfficialSet))
def test_a_set_can_be_printed_on_its_own(official_set: OfficialSet) -> None:
    in_set = {entry.barcode for entry in official_catalogue() if entry.official_set is official_set}

    cards = official_cards(official_set)

    assert cards
    assert {card.barcode for card in cards} <= in_set


def test_a_card_keeps_its_published_name() -> None:
    names = {card.name for card in official_cards(OfficialSet.BOARD_GAME)}

    assert "甲賀の巻物" in names
