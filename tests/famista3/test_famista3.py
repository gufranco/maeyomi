"""Tests for Famista 3's barcode reading, against what the game read in MAME."""

import json
from pathlib import Path
from typing import Final

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_types import GameOrder
from maeyomi.decoder.errors import CheckDigitError
from maeyomi.gameboy.famista3 import (
    BATTER,
    HOMERS_KEY,
    PICK_KEY,
    PITCH_SPEED_KEY,
    PITCHER,
    RUN_SPEED_KEY,
    STAMINA_KEY,
    STAT_KEYS,
    build_famista3,
    decode_famista3,
    famista3_entries,
    famista3_named,
    famista3_picks,
    famista3_text,
    pick_value,
    read_famista3,
    strongest_famista3,
)
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.official.catalogue import OfficialSet, official_cards

FIXTURE: Final = Path(__file__).parent.parent / "fixtures" / "oracle" / "famista3.json"
CARDS: Final = json.loads(FIXTURE.read_text(encoding="utf-8"))["cards"]
HOME_RUN: Final = "8357933639923"
HIGH_AVERAGE: Final = "7814374127798"
PITCHER_CARD: Final = "1414213562177"
SWITCH_HITTER: Final = "8051938899244"
LEFT_PITCHER: Final = "4113352270796"
ANY: Final = Constraint.anything()
KNOWN_CARDS: Final = 4


def order(ident: int | None, value: int | None = None) -> GameOrder:
    picks = () if value is None else ((PICK_KEY, value),)
    return GameOrder(ident, (ANY, ANY, ANY), picks)


def test_the_fixture_holds_every_scan() -> None:
    assert len(CARDS) >= 500


@pytest.mark.parametrize("card", CARDS, ids=[card["barcode"] for card in CARDS])
def test_the_player_matches_what_the_game_copied(card: dict[str, str]) -> None:
    record = bytes.fromhex(card["record"])
    pitcher = card["kind"] == "pitcher"

    read = read_famista3(card["barcode"])

    assert read.kind == (PITCHER if card["kind"] == "pitcher" else BATTER)
    assert (read.side, read.first) == (record[4], record[5] | record[6] << 8)
    assert (read.second, read.third) == (
        (record[9], record[13]) if pitcher else (record[7], record[8])
    )


def test_the_home_run_card_reads_as_the_game_shows_it() -> None:
    card = decode_famista3(HOME_RUN)

    text = famista3_text(card)

    assert card.game is Device.FAMISTA3
    assert card.kind is GameKind.PLAYER
    assert card.ident == BATTER
    assert (card.value(HOMERS_KEY), card.value(RUN_SPEED_KEY)) == (35, 14)
    assert text.name == ("Rookie", "ルーキー")
    assert text.detail == ("Batter, bats right", "バッター・打席 右")
    assert text.heading == ("Batting average", "打率")
    assert text.power == (".280", ".280")


def test_a_left_handed_batter_says_so() -> None:
    assert famista3_text(decode_famista3(HIGH_AVERAGE)).detail == (
        "Batter, bats left",
        "バッター・打席 左",
    )


def test_a_switch_hitter_says_so() -> None:
    assert famista3_text(decode_famista3(SWITCH_HITTER)).detail == (
        "Batter, switch hitter",
        "バッター・打席 両",
    )


def test_the_pitcher_card_reads_as_the_game_shows_it() -> None:
    card = decode_famista3(PITCHER_CARD)

    text = famista3_text(card)

    assert card.ident == PITCHER
    assert (card.value(PITCH_SPEED_KEY), card.value(STAMINA_KEY)) == (148, 10)
    assert text.detail == ("Pitcher, throws right", "ピッチャー・右投げ")
    assert text.heading == ("ERA", "防御率")
    assert text.power == ("2.90", "2.90")


def test_a_left_handed_pitcher_says_so() -> None:
    assert famista3_text(decode_famista3(LEFT_PITCHER)).detail == (
        "Pitcher, throws left",
        "ピッチャー・左投げ",
    )


def test_a_code_the_reader_cannot_scan_is_refused() -> None:
    with pytest.raises(CheckDigitError):
        decode_famista3("8357933639920")


def test_a_batter_and_a_pitcher_are_listed() -> None:
    entries = famista3_entries()

    assert [(entry.ident, entry.japanese) for entry in entries] == [
        (BATTER, "バッター"),
        (PITCHER, "ピッチャー"),
    ]


@pytest.mark.parametrize(("typed", "expected"), [("0", 0), ("pitcher", 1), ("バッター", 0)])
def test_a_kind_can_be_named_in_either_language_or_by_number(typed: str, expected: int) -> None:
    assert famista3_named(typed) == expected


def test_what_is_not_a_kind_is_refused() -> None:
    with pytest.raises(ValueError, match="no Famista 3 player kind"):
        famista3_named("catcher")


@pytest.mark.parametrize("ident", [BATTER, PITCHER])
def test_every_player_offered_can_be_printed(ident: int) -> None:
    options = famista3_picks(ident)[0].options

    built = [build_famista3(order(ident, option.value)) for option in options]

    assert all(card is not None for card in built)
    assert [card.ident for card in built if card is not None] == [ident] * len(options)
    assert [pick_value(card) for card in built if card is not None] == [
        option.value for option in options
    ]


def test_the_players_offered_are_strongest_first() -> None:
    options = famista3_picks(BATTER)[0].options

    first = build_famista3(order(BATTER, options[0].value))

    assert first is not None
    assert first.value(HOMERS_KEY) == strongest_famista3().value(HOMERS_KEY)


def test_an_order_with_no_player_picked_gives_the_strongest_of_its_kind() -> None:
    card = build_famista3(order(PITCHER))

    options = famista3_picks(PITCHER)[0].options

    assert card is not None
    assert pick_value(card) == options[0].value


def test_a_place_no_code_reaches_is_refused() -> None:
    assert build_famista3(order(BATTER, 4 * 256)) is None


def test_an_order_for_no_kind_gives_the_strongest() -> None:
    assert build_famista3(order(None)) == strongest_famista3()


def test_an_order_for_what_is_not_a_kind_is_refused() -> None:
    assert build_famista3(order(2)) is None


def test_the_strongest_card_hits_the_most_home_runs_any_code_gives() -> None:
    card = strongest_famista3()

    homers = [
        read_famista3(entry["barcode"]).second for entry in CARDS if entry["kind"] == "batter"
    ]

    assert card.ident == BATTER
    assert card.value(HOMERS_KEY) >= max(homers)


def test_every_known_card_reads_as_the_kind_it_is_named_for() -> None:
    cards = official_cards(OfficialSet.FAMISTA3)

    kinds = [decode_famista3(card.barcode).ident for card in cards]

    assert kinds == [BATTER, BATTER, BATTER, PITCHER]
    assert len(cards) == KNOWN_CARDS


def test_the_numbers_follow_from_the_player_so_nothing_is_ordered_by_number() -> None:
    assert STAT_KEYS == ()
