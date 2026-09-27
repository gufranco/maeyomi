"""Tests for the officially released cards, as transcribed by the community."""

import json
from pathlib import Path

import pytest

from maeyomi.bb1.card import FirstBattlerCard
from maeyomi.bb1.decode import decode_first
from maeyomi.datach.dbz import decode_dbz
from maeyomi.decoder.decode import decode
from maeyomi.double.decode import decode_double
from maeyomi.models.device import Device
from maeyomi.official.catalogue import (
    OfficialSet,
    official_cards,
    official_catalogue,
    rejected_transcriptions,
)

DBZ_CARDS = 36
SOURCES = {
    False: "https://wikiwiki.jp/barcode/",
    True: "https://github.com/punesemu/puNES/",
}
KNOWN_BAD_CHECK_DIGITS = {
    "1162864348006",
    "1273634357000",
    "1784651464171",
    "1444764195221",
    "3966666425072",
}


def test_the_catalogue_holds_every_transcribed_barcode_once() -> None:
    barcodes = [card.barcode for card in official_catalogue()]

    assert len(barcodes) == 577 + DBZ_CARDS
    assert len(set(barcodes)) == len(barcodes)


def test_every_card_names_the_page_it_came_from() -> None:
    for card in official_catalogue():
        assert card.source_url.startswith(SOURCES[card.official_set is OfficialSet.DATACH_DBZ])
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
    for official_set in OfficialSet:
        readers = {
            Device.BB1: decode_first,
            Device.DOUBLE: decode_double,
            Device.BB2: decode,
            Device.DATACH_DBZ: decode_dbz,
        }
        for card in official_cards(official_set):
            assert readers[official_set.device](card.barcode) == card.character


def test_a_first_device_card_prints_the_first_device_flag() -> None:
    cards = {card.name: card.character for card in official_cards(OfficialSet.ORIGINAL)}

    hero = cards["ラーメン大帝"]

    assert isinstance(hero, FirstBattlerCard)
    assert hero.flag.description == "Hero"


def test_main_story_three_is_read_by_the_double_it_came_with() -> None:
    assert OfficialSet.MAIN_STORY_THREE.device is Device.DOUBLE


def test_exactly_the_four_lists_with_first_device_wording_use_that_device() -> None:
    first = {official_set for official_set in OfficialSet if official_set.device is Device.BB1}

    assert first == {
        OfficialSet.ORIGINAL,
        OfficialSet.CHUHAI_KHAN,
        OfficialSet.GOD_VERSUS_MOTHER,
        OfficialSet.CANDY,
    }


def test_the_printable_cards_are_every_transcription_that_decodes() -> None:
    assert len(official_cards()) == 577 + DBZ_CARDS - len(KNOWN_BAD_CHECK_DIGITS)


@pytest.mark.parametrize("official_set", list(OfficialSet))
def test_a_set_can_be_printed_on_its_own(official_set: OfficialSet) -> None:
    in_set = {entry.barcode for entry in official_catalogue() if entry.official_set is official_set}

    cards = official_cards(official_set)

    assert cards
    assert {card.barcode for card in cards} <= in_set


def test_a_card_keeps_its_published_name() -> None:
    names = {card.name for card in official_cards(OfficialSet.BOARD_GAME)}

    assert "甲賀の巻物" in names


def test_the_dragon_ball_z_cards_are_the_36_the_game_accepted() -> None:
    cards = official_cards(OfficialSet.DATACH_DBZ)

    assert OfficialSet.DATACH_DBZ.device is Device.DATACH_DBZ
    assert len(cards) == DBZ_CARDS
    assert {card.barcode for card in cards} == oracle_official_barcodes()


def oracle_official_barcodes() -> set[str]:
    fixture = Path(__file__).parent.parent / "fixtures" / "oracle" / "datach_dbz.json"
    entries = json.loads(fixture.read_text("utf-8"))["cards"]
    return {entry["barcode"] for entry in entries if "official_name" in entry}
