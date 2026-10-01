"""Tests for the officially released cards, as transcribed by the community."""

import json
from functools import partial
from pathlib import Path

import pytest

from maeyomi.bb1.card import FirstBattlerCard
from maeyomi.bb1.decode import decode_first
from maeyomi.datach.dbz import decode_dbz
from maeyomi.datach.game_card import DatachCard
from maeyomi.datach.jleague import decode_jleague
from maeyomi.datach.sdgundam import decode_sdgundam
from maeyomi.datach.ultraman import decode_ultraman
from maeyomi.datach.yuyu import decode_yuyu
from maeyomi.decoder.decode import decode
from maeyomi.double.decode import decode_double
from maeyomi.gameboy.battlespace import decode_battle_space
from maeyomi.gameboy.famista3 import decode_famista3
from maeyomi.gameboy.famjock2 import decode_famjock2
from maeyomi.gameboy.kattobi import decode_kattobi
from maeyomi.gameboy.monstermaker import decode_monster_maker
from maeyomi.games.barcode_world import decode_barcode_world
from maeyomi.games.excite94 import decode_excite94
from maeyomi.games.excite95 import KICK_SPEED, decode_excite95
from maeyomi.models.device import Device
from maeyomi.nds.cardasobu import decode_cardasobu
from maeyomi.nds.oshare import decode_oshare
from maeyomi.official.catalogue import (
    OfficialCard,
    OfficialSet,
    decodes,
    device_cards,
    official_cards,
    official_catalogue,
    rejected_transcriptions,
    sets_for,
)
from maeyomi.registry import read_as

DBZ_CARDS = 36
ULTRAMAN_CARDS = 38
SD_GUNDAM_CARDS = 76
YUYU_CARDS = 37
JLEAGUE_CARDS = 160
BARCODE_WORLD_CARDS = 24
EXCITE_CLUB_CARDS = 12
WESTERN_PACK_CARDS = 26
MARIO_CARDS = 30
ADDED_CARDS = 346
SCANNED_CARDS = 71
SELIOS = "0401209245504"
SELIOS_FOR_DRAGON_SLAYER_TWO = 1
BATTLE_SPACE_CARDS = 10
MONSTER_MAKER_CARDS = 8
KATTOBI_CARDS = 6
FAMISTA3_CARDS = 4
FAMJOCK2_CARDS = 8
CARD_DE_ASOBU_CARDS = 46
OSHARE_MAJO_CARDS = 281
MAME_LIST = "https://github.com/mamedev/mame/"
GBE_PLUS = "https://github.com/shonumi/gbe-plus/"
TRANSCRIBED = (
    577
    + DBZ_CARDS
    + ADDED_CARDS
    + SCANNED_CARDS
    + ULTRAMAN_CARDS
    + SD_GUNDAM_CARDS
    + YUYU_CARDS
    + JLEAGUE_CARDS
    + BARCODE_WORLD_CARDS
    + EXCITE_CLUB_CARDS * 2
    + WESTERN_PACK_CARDS * 5
    + MARIO_CARDS
    + SELIOS_FOR_DRAGON_SLAYER_TWO
    + BATTLE_SPACE_CARDS
    + MONSTER_MAKER_CARDS
    + KATTOBI_CARDS
    + FAMISTA3_CARDS
    + FAMJOCK2_CARDS
    + CARD_DE_ASOBU_CARDS
    + OSHARE_MAJO_CARDS
)
EXCITE_CLUB_BARCODES = {
    "0000000034111",
    "0000000014113",
    "0000000102711",
    "0000700114113",
    "0000000291040",
    "0000000024112",
    "0000000261401",
    "0003000054110",
    "0007000004113",
    "0000000823531",
    "0000000391443",
    "0000000632171",
}
IRWIN_RECODED = {
    "0030000902349",
    "2090000955002",
    "2090000965001",
    "2090005995058",
    "2090007805140",
    "2090018705385",
    "2090400605231",
    "2090500605155",
    "2090500975081",
    "2091200505370",
}
UK_PAGES = "https://www.barcodebattler.co.uk/?p="
WIKI = "https://wikiwiki.jp/barcode/"
UK_LIST = "https://www.barcodebattler.co.uk/deeta.js"
UK_SCANS = "https://www.barcodebattler.co.uk/scans/Japan/"
RETROSTUFF = "https://retrostuff.org/"
KNOWN_BAD_CHECK_DIGITS: set[str] = set()


def test_the_catalogue_holds_every_transcribed_barcode_once_per_set() -> None:
    entries = [(card.official_set, card.barcode) for card in official_catalogue()]

    assert len(entries) == TRANSCRIBED
    assert len(set(entries)) == len(entries)


def test_only_the_red_potion_the_club_cards_and_the_western_packs_share_barcodes() -> None:
    western = {
        OfficialSet.IRWIN,
        OfficialSet.TOMY,
        OfficialSet.TOMY_GERMANY,
        OfficialSet.TOMY_SPAIN,
        OfficialSet.TOMY_FRANCE,
    }
    barcodes = [card.barcode for card in official_catalogue() if card.official_set not in western]

    shared = {code for code in barcodes if barcodes.count(code) > 1}

    assert shared == {"0000500970445", SELIOS, *EXCITE_CLUB_BARCODES}


def test_every_tomy_card_is_an_epoch_card_and_irwin_recoded_ten() -> None:
    epoch = {
        card.barcode for card in official_catalogue() if card.official_set is OfficialSet.SECOND
    }
    tomy = {card.barcode for card in official_catalogue() if card.official_set is OfficialSet.TOMY}
    irwin = {
        card.barcode for card in official_catalogue() if card.official_set is OfficialSet.IRWIN
    }

    assert (tomy - epoch, irwin - epoch) == (set(), IRWIN_RECODED)


def test_irwin_life_crystals_heal_less_than_the_epoch_card_they_replace() -> None:
    irwin = {
        card.name: card.barcode
        for card in official_catalogue()
        if card.official_set is OfficialSet.IRWIN
    }

    healed = (decode(irwin["Life Crystals"]).hp, decode("0160000902138").hp)

    assert healed == (300, 1600)


def test_every_card_names_the_page_it_came_from() -> None:
    sources: dict[OfficialSet, str | tuple[str, ...]] = {
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
        OfficialSet.BARCODE_WORLD: UK_SCANS,
        OfficialSet.EXCITE_CLUBS: UK_SCANS,
        OfficialSet.DRAGON_SLAYER_HERO: UK_SCANS,
        OfficialSet.BATTLE_SPACE: GBE_PLUS,
        OfficialSet.MONSTER_MAKER: (GBE_PLUS, MAME_LIST),
        OfficialSet.KATTOBI: MAME_LIST,
        OfficialSet.FAMISTA3: MAME_LIST,
        OfficialSet.FAMJOCK2: MAME_LIST,
        OfficialSet.CARD_DE_ASOBU: GBE_PLUS,
        OfficialSet.OSHARE_MAJO: GBE_PLUS,
        OfficialSet.EXCITE94_CLUBS: UK_SCANS,
        OfficialSet.IRWIN: UK_PAGES,
        OfficialSet.TOMY: UK_PAGES,
        OfficialSet.TOMY_GERMANY: UK_PAGES,
        OfficialSet.TOMY_SPAIN: UK_PAGES,
        OfficialSet.TOMY_FRANCE: UK_PAGES,
        OfficialSet.SUPER_MARIO_WORLD: UK_PAGES,
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


def test_a_barcode_with_a_wrong_check_digit_does_not_decode() -> None:
    entry = OfficialCard(
        barcode="3966666425072",
        name="ガングラティ",
        official_set=OfficialSet.ORIGINAL,
        source_url="",
        transcribed="3966666425072",
    )

    assert decodes(entry) is False


def test_no_transcription_is_left_out_now_every_card_prints() -> None:
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
            Device.BARCODE_WORLD: decode_barcode_world,
            Device.EXCITE95: decode_excite95,
            Device.EXCITE94: decode_excite94,
            Device.DSLAYER2: partial(read_as, Device.DSLAYER2),
            Device.BATTLE_SPACE: decode_battle_space,
            Device.MONSTER_MAKER: decode_monster_maker,
            Device.KATTOBI: decode_kattobi,
            Device.FAMISTA3: decode_famista3,
            Device.FAMJOCK2: decode_famjock2,
            Device.CARD_DE_ASOBU: decode_cardasobu,
            Device.OSHARE_MAJO: decode_oshare,
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
        (OfficialSet.IRWIN, Device.BB2, WESTERN_PACK_CARDS),
        (OfficialSet.TOMY, Device.BB2, WESTERN_PACK_CARDS),
        (OfficialSet.TOMY_GERMANY, Device.BB2, WESTERN_PACK_CARDS),
        (OfficialSet.TOMY_SPAIN, Device.BB2, WESTERN_PACK_CARDS),
        (OfficialSet.TOMY_FRANCE, Device.BB2, WESTERN_PACK_CARDS),
        (OfficialSet.SUPER_MARIO_WORLD, Device.BB2, MARIO_CARDS),
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


def test_the_barcode_world_set_is_every_card_with_a_barcode() -> None:
    cards = official_cards(OfficialSet.BARCODE_WORLD)

    assert len(cards) == BARCODE_WORLD_CARDS
    assert {card.name for card in cards} >= {"キャリー", "ニトロガン"}


def test_the_excite_stage_club_cards_are_item_cards_for_excite_stage_95() -> None:
    cards = official_cards(OfficialSet.EXCITE_CLUBS)

    assert len(cards) == EXCITE_CLUB_CARDS
    flugels = next(card for card in cards if card.name == "横浜フリューゲルス")
    assert isinstance(flugels.character, DatachCard)
    assert (flugels.character.ident, flugels.character.traits) == (KICK_SPEED, (104,))


def test_bowser_is_the_strongest_super_mario_world_card() -> None:
    mario = {
        card.name: card.barcode
        for card in official_catalogue()
        if card.official_set is OfficialSet.SUPER_MARIO_WORLD
    }

    health = (decode(mario["クッパ"]).hp, decode(mario["マリオ"]).hp)

    assert health == (20900, 3500)


@pytest.mark.parametrize(
    ("official_set", "renamed"),
    [
        (OfficialSet.TOMY_GERMANY, "Heilkristall"),
        (OfficialSet.TOMY_SPAIN, "Cristales de la Vida"),
        (OfficialSet.TOMY_FRANCE, "Revitaliseurs"),
    ],
)
def test_each_tomy_edition_keeps_epochs_codes_under_its_own_names(
    official_set: OfficialSet, renamed: str
) -> None:
    uk = {card.barcode for card in official_catalogue() if card.official_set is OfficialSet.TOMY}
    edition = {
        card.barcode: card.name
        for card in official_catalogue()
        if card.official_set is official_set
    }

    assert (set(edition), edition["0160000902138"]) == (uk, renamed)
