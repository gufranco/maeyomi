"""Tests for Family Jockey 2's barcode reading, against what the game read in MAME."""

import json
from pathlib import Path
from typing import Final

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_types import GameOrder
from maeyomi.decoder.errors import CheckDigitError
from maeyomi.gameboy.famjock2 import (
    MARE,
    RACEHORSE,
    STALLION,
    STAT_KEYS,
    STAT_PICKS,
    TILE_KEYS,
    build_famjock2,
    decode_famjock2,
    famjock2_entries,
    famjock2_named,
    famjock2_picks,
    famjock2_text,
    read_famjock2,
    strongest_famjock2,
)
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.official.catalogue import OfficialSet, official_cards

FIXTURE: Final = Path(__file__).parent.parent / "fixtures" / "oracle" / "famjock2.json"
CARDS: Final = json.loads(FIXTURE.read_text(encoding="utf-8"))["cards"]
KINDS: Final = {"racehorse": RACEHORSE, "mare": MARE, "stallion": STALLION}
MARE_A: Final = "2378649896765"
FAMICOM_BOX: Final = "4907892000001"
ANY: Final = Constraint.anything()
KNOWN_CARDS: Final = 8


def order(ident: int | None, stats: tuple[int, ...] | None = None) -> GameOrder:
    picks = () if stats is None else tuple(zip(STAT_PICKS, stats, strict=True))
    return GameOrder(ident, (ANY, ANY, ANY), picks)


def test_the_fixture_holds_every_scan_in_every_menu() -> None:
    assert len(CARDS) >= 900
    assert {card["kind"] for card in CARDS} == set(KINDS)


@pytest.mark.parametrize("card", CARDS, ids=[f"{card['kind']}-{card['barcode']}" for card in CARDS])
def test_the_horse_matches_what_the_game_built(card: dict[str, object]) -> None:
    horse = bytes.fromhex(str(card["horse"]))

    read = read_famjock2(str(card["barcode"]), KINDS[str(card["kind"])])

    assert (read.stats, read.bonus) == (tuple(horse[:6]), card["bonus"])


def test_the_mare_card_reads_as_the_game_shows_it_in_the_mare_menu() -> None:
    read = read_famjock2(MARE_A, MARE)

    assert read.stats == (7, 7, 5, 7, 5, 5)


def test_a_card_prints_its_racehorse_reading_and_names_the_other_two() -> None:
    card = decode_famjock2(MARE_A)

    text = famjock2_text(card)

    assert card.game is Device.FAMJOCK2
    assert card.kind is GameKind.FIGHTER
    assert card.ident == RACEHORSE
    assert tuple(card.value(key) for key in TILE_KEYS) == (2, 2, 0, 2, 0, 0)
    assert text.name == ("Racehorse", "競走馬")
    assert text.heading == ("In the other menus", "ほかの メニューでは")
    assert text.power == (
        "Mare SP7 ST7 G5 J7 TB5 TP5, stallion SP2 ST2 G0 J2 TB0 TP0",
        "繁殖馬 SP7 ST7 G5 J7 TB5 TP5、種馬 SP2 ST2 G0 J2 TB0 TP0",
    )


def test_a_namco_box_code_names_its_bonus() -> None:
    text = famjock2_text(decode_famjock2(FAMICOM_BOX))

    assert text.detail == (
        "A Namco Famicom game: stamina +2",
        "ナムコの ファミコンソフト: スタミナ2アップ",
    )


def test_a_card_without_a_bonus_says_which_menu_it_was_read_in() -> None:
    assert famjock2_text(decode_famjock2(MARE_A)).detail == (
        "Read in the racehorse menu",
        "競走馬の メニューで よむ",
    )


def test_a_code_the_reader_cannot_scan_is_refused() -> None:
    with pytest.raises(CheckDigitError):
        decode_famjock2("2378649896760")


def test_the_three_menus_are_listed() -> None:
    assert [(entry.ident, entry.japanese) for entry in famjock2_entries()] == [
        (RACEHORSE, "競走馬"),
        (MARE, "繁殖馬"),
        (STALLION, "種馬"),
    ]


@pytest.mark.parametrize(("typed", "expected"), [("2", 2), ("mare", 1), ("種馬", 2)])
def test_a_menu_can_be_named_in_either_language_or_by_number(typed: str, expected: int) -> None:
    assert famjock2_named(typed) == expected


def test_what_is_not_a_menu_is_refused() -> None:
    with pytest.raises(ValueError, match="no Family Jockey 2 horse kind"):
        famjock2_named("pony")


def test_each_stat_is_offered_from_0_to_9() -> None:
    picks = famjock2_picks(MARE)

    assert [pick.key for pick in picks] == list(STAT_PICKS)
    assert [option.value for option in picks[0].options] == list(range(10))


@pytest.mark.parametrize("ident", [RACEHORSE, MARE, STALLION])
@pytest.mark.parametrize("stats", [(9, 9, 9, 9, 9, 9), (0, 0, 0, 0, 0, 0), (1, 2, 3, 4, 5, 6)])
def test_a_horse_can_be_ordered_with_any_stats(ident: int, stats: tuple[int, ...]) -> None:
    card = build_famjock2(order(ident, stats))

    assert card is not None
    assert card.ident == ident
    assert read_famjock2(card.barcode, ident).stats == stats
    assert read_famjock2(card.barcode, ident).bonus == 0


def test_an_order_with_no_stats_picked_gives_nines() -> None:
    card = build_famjock2(order(STALLION))

    assert card is not None
    assert read_famjock2(card.barcode, STALLION).stats == (9,) * 6


def test_an_order_for_no_kind_gives_the_strongest() -> None:
    assert build_famjock2(order(None)) == strongest_famjock2()


def test_an_order_for_what_is_not_a_kind_is_refused() -> None:
    assert build_famjock2(order(3)) is None


def test_the_strongest_is_a_racehorse_at_nine_in_everything() -> None:
    card = strongest_famjock2()

    assert card.ident == RACEHORSE
    assert tuple(card.value(key) for key in TILE_KEYS) == (9,) * 6


def test_every_known_card_is_listed() -> None:
    assert len(official_cards(OfficialSet.FAMJOCK2)) == KNOWN_CARDS


def test_the_numbers_are_picked_so_nothing_is_ordered_by_slider() -> None:
    assert STAT_KEYS == ()
