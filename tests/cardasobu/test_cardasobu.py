"""Tests for Card de Asobu's card reading, against what the game accepted in GBE+."""

import json
from pathlib import Path
from typing import Final

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_types import GameEntry, GameOrder
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.nds.cardasobu import (
    NO_CARD,
    STAT_KEYS,
    build_cardasobu,
    cardasobu_entries,
    cardasobu_named,
    cardasobu_text,
    decode_cardasobu,
)
from maeyomi.said import in_japanese

FIXTURE: Final = Path(__file__).parent.parent / "fixtures" / "oracle" / "cardasobu.json"
RECORDED: Final = json.loads(FIXTURE.read_text(encoding="utf-8"))["cards"]
ACCEPTED: Final = next(card["screen"] for card in RECORDED if card["barcode"] == "*AA01C0RD00V01*")
ANY: Final = Constraint.anything()
DUCK: Final = "*AA01C0RD00V01*"
FROG: Final = "*AA47CKRC00V01*"


def order(ident: int | None) -> GameOrder:
    return GameOrder(ident, (ANY, ANY, ANY))


def framed(text: str) -> bool:
    return text.startswith("*") and text.endswith("*")


@pytest.mark.parametrize("card", RECORDED, ids=lambda card: card["barcode"])
def test_every_recorded_code_is_read_as_the_game_read_it(card: dict[str, str]) -> None:
    read = takes(card["barcode"])

    assert (framed(card["barcode"]) and read) == (card["screen"] == ACCEPTED)


def takes(text: str) -> bool:
    try:
        decode_cardasobu(text)
    except UnsupportedBarcodeError:
        return False
    return True


def test_every_listed_card_was_accepted_by_the_game() -> None:
    accepted = {card["barcode"] for card in RECORDED if card["screen"] == ACCEPTED}

    assert accepted == {f"*{build_text(entry)}*" for entry in cardasobu_entries()}


def build_text(entry: GameEntry) -> str:
    card = build_cardasobu(order(entry.ident))
    assert card is not None
    return card.barcode


def test_the_duck_is_the_first_card() -> None:
    card = decode_cardasobu(DUCK)

    assert (card.kind, card.ident) == (GameKind.ITEM, 0)
    assert cardasobu_text(card).name == ("Duck", "あひる")


def test_the_frog_takes_the_last_place_and_ka_holds_no_card() -> None:
    card = decode_cardasobu(FROG)

    assert cardasobu_text(card).name == ("Frog", "かえる")
    assert NO_CARD not in {entry.ident for entry in cardasobu_entries()}


def test_a_card_reads_the_same_without_its_start_and_stop() -> None:
    assert decode_cardasobu(DUCK.strip("*")).ident == 0


def test_the_wrong_version_is_refused_in_both_languages() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="no Card de Asobu card") as raised:
        decode_cardasobu("*AA01C0RD00V02*")

    assert in_japanese(raised.value.args[0])


def test_a_character_code39_cannot_carry_is_refused() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="Code 39"):
        decode_cardasobu("aa01c0rd00v01")


def test_the_search_card_is_an_effect() -> None:
    card = decode_cardasobu("*AA45SWW000V01*")

    assert card.kind is GameKind.EFFECT
    assert cardasobu_text(card).name == ("Find the card", "カードをさがす")


def test_forty_six_cards_can_be_printed() -> None:
    assert len(cardasobu_entries()) == 46


def test_a_card_is_built_with_its_full_text() -> None:
    card = build_cardasobu(order(7))

    assert card is not None
    assert card.barcode == "AA082KRC00V01"


def test_any_card_is_the_first_when_none_is_named() -> None:
    card = build_cardasobu(order(None))

    assert card is not None
    assert card.ident == 0


def test_the_empty_slot_builds_nothing() -> None:
    assert build_cardasobu(order(NO_CARD)) is None


def test_a_card_is_found_by_name_or_number() -> None:
    assert cardasobu_named("Whale") == 7
    assert cardasobu_named("くじら") == 7
    assert cardasobu_named("7") == 7
    with pytest.raises(ValueError, match="Card de Asobu"):
        cardasobu_named("Dragon")


def test_the_empty_slot_is_not_a_name() -> None:
    with pytest.raises(ValueError, match="Card de Asobu"):
        cardasobu_named(str(NO_CARD))


def test_a_card_says_what_it_shows_and_where_it_sits() -> None:
    text = cardasobu_text(decode_cardasobu(DUCK))

    assert text.detail == ("The card for A", "「あ」の カード")


def test_the_frog_is_the_card_for_ka() -> None:
    assert cardasobu_text(decode_cardasobu(FROG)).detail == ("The card for Ka", "「か」の カード")


def test_the_search_card_says_what_it_does() -> None:
    text = cardasobu_text(decode_cardasobu("*AA45SWW000V01*"))

    assert text.detail == ("Starts the card search", "カードさがしを はじめる")


def test_the_cards_carry_no_numbers() -> None:
    assert STAT_KEYS == ()
    assert decode_cardasobu(DUCK).game is Device.CARD_DE_ASOBU
