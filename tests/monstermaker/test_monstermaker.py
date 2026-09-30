"""Tests for Monster Maker: Barcode Saga's barcode reading, against what the game read in MAME."""

import json
from pathlib import Path
from typing import Final

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_types import GameOrder
from maeyomi.decoder.errors import CheckDigitError
from maeyomi.gameboy.monstermaker import (
    AP_KEY,
    DP_KEY,
    HP_KEY,
    LATER_KEY,
    MP_KEY,
    STAT_KEYS,
    build_monster_maker,
    decode_monster_maker,
    later_value,
    monster_maker_entries,
    monster_maker_named,
    monster_maker_picks,
    monster_maker_text,
    read_monster_maker,
    strongest_monster_maker,
)
from maeyomi.gameboy.monstermaker_tables import NAMES
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.official.catalogue import OfficialSet, official_cards

FIXTURE: Final = Path(__file__).parent.parent / "fixtures" / "oracle" / "monstmkb.json"
CARDS: Final = json.loads(FIXTURE.read_text(encoding="utf-8"))["cards"]
LORIAN: Final = "9998017308336"
HARPY_LATER: Final = "4901121110004"
ANY: Final = Constraint.anything()
HEROES: Final = 17
LEVELS: Final = 9
LORIAN_ID: Final = 17
DRAGON_ID: Final = 20
KNOWN_CARDS: Final = 6
LINK_ID: Final = 3


def order(ident: int, later: int | None = None) -> GameOrder:
    picks = () if later is None else ((LATER_KEY, later),)
    return GameOrder(ident, (ANY, ANY, ANY), picks)


def test_the_fixture_holds_every_scan() -> None:
    assert len(CARDS) >= 500


@pytest.mark.parametrize("card", CARDS, ids=[card["barcode"] for card in CARDS])
def test_both_readings_match_what_the_game_read(card: dict[str, str]) -> None:
    party = bytes.fromhex(card["party"])
    later = bytes.fromhex(card["adventure"])

    read = read_monster_maker(card["barcode"])

    assert (read.party, read.party_class) == (party[0], party[7] >> 4)
    assert (read.later, read.later_level, read.later_class) == (
        later[0],
        later[7] & 0x0F,
        later[7] >> 4,
    )


def test_the_lorian_card_reads_as_the_game_shows_it() -> None:
    card = decode_monster_maker(LORIAN)

    text = monster_maker_text(card)

    assert card.ident == LORIAN_ID
    assert card.game is Device.MONSTER_MAKER
    assert card.kind is GameKind.FIGHTER
    assert (card.value(HP_KEY), card.value(AP_KEY), card.value(MP_KEY), card.value(DP_KEY)) == (
        150,
        53,
        0,
        60,
    )
    assert text.name == ("Lorian", "ロリエーン")
    assert text.detail == ("Archer, move 2", "ゆみつかい・ムーブ 2")
    assert text.power == (
        "Lorian, level 7: HP 370, AP 97, MP 0, DP 90, move 3",
        "ロリエーン レベル7: HP 370 AP 97 MP 0 DP 90 ムーブ 3",
    )


def test_a_card_read_later_as_a_monster_names_the_monster() -> None:
    text = monster_maker_text(decode_monster_maker(HARPY_LATER))

    assert text.heading == ("Later in the game", "ゲーム の とちゅう で")
    assert text.power == (
        "Harpy: HP 280, AP 0, MP 40, DP 70, move 5",
        "ハーピー: HP 280 AP 0 MP 40 DP 70 ムーブ 5",
    )


def test_an_ean_8_reads_its_digits_then_zeros() -> None:
    read = read_monster_maker("28792178")

    assert (read.party, read.later, read.later_level) == (1, 18, 2)


def test_a_code_with_no_digit_to_read_falls_through_to_the_roster() -> None:
    read = read_monster_maker("9700000000000")

    assert (read.party, read.later) == (LINK_ID, LINK_ID)


def test_a_code_the_reader_cannot_scan_is_refused() -> None:
    with pytest.raises(CheckDigitError):
        decode_monster_maker("9998017308330")


def test_every_hero_is_listed() -> None:
    entries = monster_maker_entries()

    assert [entry.ident for entry in entries] == list(range(1, HEROES + 1))
    assert entries[LORIAN_ID - 1].japanese == "ロリエーン"


@pytest.mark.parametrize(("typed", "expected"), [("17", 17), ("lorian", 17), ("ハーゲン", 5)])
def test_a_hero_can_be_named_in_either_language_or_by_number(typed: str, expected: int) -> None:
    assert monster_maker_named(typed) == expected


@pytest.mark.parametrize("typed", ["0", "18", "Dragon"])
def test_what_is_not_a_hero_is_refused(typed: str) -> None:
    with pytest.raises(ValueError, match="no Monster Maker hero"):
        monster_maker_named(typed)


@pytest.mark.parametrize("ident", range(1, HEROES + 1))
def test_every_later_reading_offered_can_be_printed(ident: int) -> None:
    options = monster_maker_picks(ident)[0].options

    built = [build_monster_maker(order(ident, option.value)) for option in options]

    assert all(card is not None for card in built)
    assert [card.ident for card in built if card is not None] == [ident] * len(options)
    assert [later_value(card) for card in built if card is not None] == [
        option.value for option in options
    ]


def test_each_hero_can_come_back_at_every_level() -> None:
    options = monster_maker_picks(LORIAN_ID)[0].options

    levels = [option.value for option in options if option.value // 100 == LORIAN_ID]

    assert levels == [LORIAN_ID * 100 + level for level in range(1, LEVELS + 1)]


def test_the_dragon_comes_later_on_a_link_card() -> None:
    card = build_monster_maker(order(LINK_ID, DRAGON_ID * 100))

    assert card is not None
    assert read_monster_maker(card.barcode).later == DRAGON_ID


def test_an_order_with_no_later_choice_brings_the_hero_back_at_the_top_level() -> None:
    card = build_monster_maker(order(LORIAN_ID))

    assert card is not None
    assert later_value(card) == LORIAN_ID * 100 + LEVELS


def test_a_later_reading_the_hero_cannot_have_is_refused() -> None:
    assert build_monster_maker(order(LORIAN_ID, DRAGON_ID * 100)) is None


def test_an_order_for_any_hero_gives_the_strongest() -> None:
    card = build_monster_maker(GameOrder(None, (ANY, ANY, ANY)))

    assert card == strongest_monster_maker()


def test_an_order_for_what_is_not_a_hero_is_refused() -> None:
    assert build_monster_maker(order(HEROES + 1)) is None


def test_the_strongest_card_is_lorian_back_at_level_nine() -> None:
    card = strongest_monster_maker()

    assert card.ident == LORIAN_ID
    assert later_value(card) == LORIAN_ID * 100 + LEVELS


def test_the_numbers_follow_from_the_hero_so_nothing_is_ordered_by_number() -> None:
    assert STAT_KEYS == ()


def test_every_known_card_reads_as_the_hero_it_is_named_for() -> None:
    cards = official_cards(OfficialSet.MONSTER_MAKER)

    names = [NAMES[decode_monster_maker(card.barcode).ident - 1] for card in cards]

    assert names == [card.name for card in cards]
    assert len(cards) == KNOWN_CARDS
