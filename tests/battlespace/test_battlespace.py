"""Tests for reading and building Battle Space fighters.

The fixture holds the player record the game itself filled in, running in MAME,
for 668 scanned codes, among them one card this program built for each class
and 60 EAN-8 codes;
the decoder has to agree with every one.
"""

import json
from pathlib import Path
from typing import Final

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_types import GameOrder
from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.decoder.errors import CheckDigitError
from maeyomi.gameboy.battlespace import (
    MP_KEY,
    STAT_KEYS,
    battle_space_entries,
    battle_space_named,
    battle_space_text,
    build_battle_space,
    decode_battle_space,
    strongest_battle_space,
)
from maeyomi.gameboy.battlespace_names import CLASS_ENGLISH, SPECIAL_ENGLISH, SPELL_ENGLISH
from maeyomi.gameboy.battlespace_tables import CLASS_NAMES, SPECIAL_NAMES, SPELL_NAMES
from maeyomi.models.constraint import Constraint

FIXTURE: Final = Path(__file__).parent.parent / "fixtures/oracle/bspace.json"
CARDS: Final = json.loads(FIXTURE.read_text(encoding="utf-8"))["cards"]
STATS_AT: Final = 0x25
HUNDRED: Final = 100
BERSERKER: Final = "4907981000301"
ANY: Final = Constraint.anything()


def recorded(record: str) -> tuple[int, tuple[int, ...]]:
    raw = bytes.fromhex(record)
    stats = tuple(
        int.from_bytes(raw[STATS_AT + 2 * i : STATS_AT + 2 * i + 2], "little") for i in range(4)
    )
    return raw[0], stats


def test_the_fixture_holds_every_scan() -> None:
    assert len(CARDS) == 668
    assert {card["status"] for card in CARDS} == {0}


@pytest.mark.parametrize("card", CARDS, ids=lambda card: card["barcode"])
def test_the_decoder_reads_every_code_as_the_game_did(card: dict[str, object]) -> None:
    klass, (hp, mp, ap, dp) = recorded(str(card["record"]))

    read = decode_battle_space(str(card["barcode"]))

    assert read.ident == klass
    assert (read.value("GHP"), read.value(MP_KEY), read.value("AP"), read.value("GDP")) == (
        hp * HUNDRED,
        mp * HUNDRED,
        ap * HUNDRED,
        dp * HUNDRED,
    )


def test_the_berserker_card_reads_as_the_game_shows_it() -> None:
    read = decode_battle_space(BERSERKER)

    text = battle_space_text(read)

    assert text.name == ("Berserker", "バーサーカー")
    assert text.power == ("Flurry of slashes", "めったぎり")
    assert (read.value("GHP"), read.value(MP_KEY), read.value("AP"), read.value("GDP")) == (
        900000,
        1000,
        90000,
        3000,
    )


def test_every_name_has_an_english_translation() -> None:
    assert (len(CLASS_ENGLISH), len(SPELL_ENGLISH), len(SPECIAL_ENGLISH)) == (
        len(CLASS_NAMES),
        len(SPELL_NAMES),
        len(SPECIAL_NAMES),
    )


def test_every_class_is_listed() -> None:
    entries = battle_space_entries()

    assert len(entries) == len(CLASS_NAMES)
    assert {entry.kind for entry in entries} == {GameKind.FIGHTER}


@pytest.mark.parametrize(
    ("typed", "expected"), [("Berserker", 0x18), ("バーサーカー", 0x18), ("24", 24)]
)
def test_a_class_can_be_named_in_either_language_or_by_number(typed: str, expected: int) -> None:
    assert battle_space_named(typed) == expected


def test_an_unknown_class_is_refused() -> None:
    with pytest.raises(ValueError, match="no Battle Space class"):
        battle_space_named("Astronaut")


@pytest.mark.parametrize("klass", [0x00, 0x18, 0x4A, 0x61])
def test_a_class_can_be_ordered(klass: int) -> None:
    order = GameOrder(klass, (ANY, ANY, ANY))

    card = build_battle_space(order)

    assert card is not None
    assert decode_battle_space(card.barcode).ident == klass
    assert card.barcode[12] == str(expected_check_digit(card.barcode[:12]))


def test_an_order_keeps_the_numbers_asked_for() -> None:
    order = GameOrder(
        None, (Constraint.exactly(430000), Constraint.exactly(35100), Constraint.exactly(75600))
    )

    card = build_battle_space(order)

    assert card is not None
    read = decode_battle_space(card.barcode)
    assert (read.value("GHP"), read.value("AP"), read.value("GDP")) == (430000, 35100, 75600)


def test_an_order_the_game_cannot_read_is_refused() -> None:
    order = GameOrder(None, (Constraint.at_least(1000001), ANY, ANY))

    assert build_battle_space(order) is None


def test_the_strongest_fighter_has_the_top_hp_the_game_reads() -> None:
    card = strongest_battle_space()

    read = decode_battle_space(card.barcode)
    assert read.value("GHP") == 999900
    assert read.value("AP") >= 90000


def test_no_code_reads_every_number_at_its_top() -> None:
    top = GameOrder(
        None, (Constraint.exactly(999900), Constraint.exactly(99900), Constraint.exactly(99900))
    )

    card = build_battle_space(top)

    assert card is None or card.value(MP_KEY) < 99900


def test_the_card_names_its_magic_group_and_spells() -> None:
    read = decode_battle_space("4911826551347")

    text = battle_space_text(read)

    assert text.detail == ("Fighter, magic M", "せんし・まほう M")
    assert text.heading == ("Spells", "じゅもん")
    assert text.power[0] == "Weak, Slow, Bombs, Thunder, Fire, Tornado, Meteor"
    assert text.power[1].endswith("メテオ")


def test_a_fighter_with_a_special_move_and_magic_names_both() -> None:
    read = decode_battle_space("7605510653703")

    text = battle_space_text(read)

    assert text.heading == ("Special and spells", "とくしゅ と じゅもん")
    assert (
        text.power[0] == "Healing. Spells: Strength, Shield, Cure, Resist, Fog, Refresh, Holy Force"
    )


def test_a_fighter_with_every_spell_says_every_spell() -> None:
    read = decode_battle_space("6244783919867")

    text = battle_space_text(read)

    assert text.heading == ("Spells", "じゅもん")
    assert text.power == ("All 14 spells", "14しゅ すべて")


def test_a_fighter_without_a_special_move_or_magic_says_none() -> None:
    read = decode_battle_space("4918156001351")

    text = battle_space_text(read)

    assert text.heading == ("Special", "とくしゅ")
    assert text.power == ("None", "なし")


def test_a_fighter_without_magic_says_so() -> None:
    read = decode_battle_space(BERSERKER)

    text = battle_space_text(read)

    assert text.detail == ("Fighter, no magic", "せんし・まほう なし")


def test_the_three_sliders_are_hp_ap_and_dp() -> None:
    assert STAT_KEYS == ("GHP", "AP", "GDP")


def test_a_code_the_reader_cannot_scan_is_refused() -> None:
    with pytest.raises(CheckDigitError):
        decode_battle_space("4907981000302")


def test_a_search_stops_when_its_attempts_run_out() -> None:
    top = GameOrder(
        None, (Constraint.exactly(999900), Constraint.exactly(99900), Constraint.exactly(99900))
    )

    card = build_battle_space(top, attempts=1)

    assert card is None


def test_numbers_a_class_cannot_have_give_that_class_nearest_card() -> None:
    order = GameOrder(
        0x0B, (Constraint.exactly(500000), Constraint.exactly(30000), Constraint.exactly(20000))
    )

    card = build_battle_space(order)

    assert card is not None
    assert card.ident == 0x0B
    assert card.value("GHP") >= 750000


def test_numbers_no_code_gives_are_met_as_closely_as_the_game_allows() -> None:
    order = GameOrder(
        None, (Constraint.exactly(5000), Constraint.exactly(1800), Constraint.exactly(1200))
    )

    card = build_battle_space(order)

    assert card is not None
    assert abs(card.value("GHP") - 5000) <= 300
    assert abs(card.value("AP") - 1800) <= 300
    assert abs(card.value("GDP") - 1200) <= 300
