"""Tests for the officially released cards, as transcribed by the community."""

import json
from pathlib import Path

import pytest

from maeyomi.bb1.card import FirstBattlerCard
from maeyomi.bb1.decode import decode_first
from maeyomi.datach.dbz import decode_dbz
from maeyomi.datach.jleague import decode_jleague
from maeyomi.datach.sdgundam import decode_sdgundam
from maeyomi.datach.ultraman import decode_ultraman
from maeyomi.datach.yuyu import decode_yuyu
from maeyomi.decoder.decode import decode
from maeyomi.double.decode import decode_double
from maeyomi.models.device import Device
from maeyomi.official.catalogue import (
    OfficialSet,
    device_cards,
    official_cards,
    official_catalogue,
    rejected_transcriptions,
    sets_for,
)

DBZ_CARDS = 36
ULTRAMAN_CARDS = 38
SD_GUNDAM_CARDS = 76
YUYU_CARDS = 37
JLEAGUE_CARDS = 160
ADDED_CARDS = 346
SCANNED_CARDS = 71
TRANSCRIBED = (
    577
    + DBZ_CARDS
    + ADDED_CARDS
    + SCANNED_CARDS
    + ULTRAMAN_CARDS
    + SD_GUNDAM_CARDS
    + YUYU_CARDS
    + JLEAGUE_CARDS
)
SHARED_BETWEEN_SETS = {"0000500970445"}
WIKI = "https://wikiwiki.jp/barcode/"
UK_LIST = "https://www.barcodebattler.co.uk/deeta.js"
UK_SCANS = "https://www.barcodebattler.co.uk/scans/Japan/"
RETROSTUFF = "https://retrostuff.org/"
KNOWN_BAD_CHECK_DIGITS = {
    "1162864348006",
    "1273634357000",
    "1784651464171",
    "1444764195221",
    "3966666425072",
}


def test_the_catalogue_holds_every_transcribed_barcode_once_per_set() -> None:
    entries = [(card.official_set, card.barcode) for card in official_catalogue()]

    assert len(entries) == TRANSCRIBED
    assert len(set(entries)) == len(entries)


def test_only_the_red_potion_belongs_to_two_sets() -> None:
    barcodes = [card.barcode for card in official_catalogue()]

    assert {code for code in barcodes if barcodes.count(code) > 1} == SHARED_BETWEEN_SETS


def test_every_card_names_the_page_it_came_from() -> None:
    sources = {
        OfficialSet.DATACH_DBZ: "https://github.com/punesemu/puNES/",
        OfficialSet.ZELDA: UK_LIST,
        OfficialSet.SECOND_GRADE: UK_LIST,
        OfficialSet.STREET_FIGHTER: UK_LIST,
        OfficialSet.DRAGON_SLAYER: UK_SCANS,
        OfficialSet.DORAEMON_DINOSAUR: UK_SCANS,
        OfficialSet.OBOCCHAMAKUN: UK_SCANS,
        OfficialSet.MEIJI_FREEZELAND: UK_SCANS,
        OfficialSet.DATACH_ULTRAMAN: RETROSTUFF,
        OfficialSet.DATACH_SD_GUNDAM: RETROSTUFF,
        OfficialSet.DATACH_YUYU: "https://archive.org/details/",
        OfficialSet.DATACH_JLEAGUE: "https://archive.org/details/",
    }
    for card in official_catalogue():
        assert card.source_url.startswith(sources.get(card.official_set, WIKI))
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
            Device.DATACH_ULTRAMAN: decode_ultraman,
            Device.DATACH_SD_GUNDAM: decode_sdgundam,
            Device.DATACH_YUYU: decode_yuyu,
            Device.DATACH_JLEAGUE: decode_jleague,
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


def test_exactly_the_five_first_device_lists_use_that_device() -> None:
    first = {official_set for official_set in OfficialSet if official_set.device is Device.BB1}

    assert first == {
        OfficialSet.ORIGINAL,
        OfficialSet.CHUHAI_KHAN,
        OfficialSet.GOD_VERSUS_MOTHER,
        OfficialSet.CANDY,
        OfficialSet.GOD_MARS,
        OfficialSet.OBOCCHAMAKUN,
    }


def test_the_printable_cards_are_every_transcription_that_decodes() -> None:
    assert len(official_cards()) == TRANSCRIBED - len(KNOWN_BAD_CHECK_DIGITS)


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


def test_a_device_owns_exactly_the_sets_written_for_it() -> None:
    assert sets_for(Device.DATACH_DBZ) == (OfficialSet.DATACH_DBZ,)
    assert len(device_cards(Device.BB1)) == sum(
        len(official_cards(official_set)) for official_set in sets_for(Device.BB1)
    )


@pytest.mark.parametrize(
    ("official_set", "device", "count"),
    [
        (OfficialSet.GOD_MARS, Device.BB1, 39),
        (OfficialSet.MAIN_STORY_ONE, Device.BB2, 50),
        (OfficialSet.MAIN_STORY_TWO, Device.BB2, 36),
        (OfficialSet.MAIN_STORY_FOUR, Device.DOUBLE, 31),
        (OfficialSet.MACHINE_DRAGONS, Device.BB2, 36),
        (OfficialSet.ZELDA, Device.BB2, 30),
        (OfficialSet.SECOND_GRADE, Device.BB2, 24),
        (OfficialSet.STREET_FIGHTER, Device.BB2, 100),
        (OfficialSet.DRAGON_SLAYER, Device.BB2, 30),
        (OfficialSet.DORAEMON_DINOSAUR, Device.BB2, 33),
        (OfficialSet.OBOCCHAMAKUN, Device.BB1, 6),
        (OfficialSet.MEIJI_FREEZELAND, Device.BB2, 2),
    ],
)
def test_every_added_set_is_read_by_its_device(
    official_set: OfficialSet, device: Device, count: int
) -> None:
    assert official_set.device is device
    assert len(official_cards(official_set)) == count


def test_the_ultraman_club_set_is_every_card_bandai_printed_with_a_barcode() -> None:
    cards = official_cards(OfficialSet.DATACH_ULTRAMAN)

    assert len(cards) == ULTRAMAN_CARDS
    assert sets_for(Device.DATACH_ULTRAMAN) == (OfficialSet.DATACH_ULTRAMAN,)
    assert {card.name for card in cards} >= {"ゾフィー", "ウルトラの父"}


def test_the_sd_gundam_set_is_both_barcodes_of_every_card_bandai_printed_with_them() -> None:
    cards = official_cards(OfficialSet.DATACH_SD_GUNDAM)

    assert len(cards) == SD_GUNDAM_CARDS
    assert sets_for(Device.DATACH_SD_GUNDAM) == (OfficialSet.DATACH_SD_GUNDAM,)


def test_the_yu_yu_hakusho_set_is_every_card_bandai_printed_with_a_barcode() -> None:
    cards = official_cards(OfficialSet.DATACH_YUYU)

    assert len(cards) == YUYU_CARDS
    assert sets_for(Device.DATACH_YUYU) == (OfficialSet.DATACH_YUYU,)


def test_the_j_league_set_is_all_four_barcodes_of_every_card() -> None:
    cards = official_cards(OfficialSet.DATACH_JLEAGUE)

    assert len(cards) == JLEAGUE_CARDS
    assert {card.name for card in cards} >= {"ジーコ", "鹿島アントラーズ"}
