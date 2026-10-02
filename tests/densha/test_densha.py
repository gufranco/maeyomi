"""Tests for Densha Daishuugou's card reading, against what the game said in MAME."""

import json
from pathlib import Path
from typing import Final

import pytest

from maeyomi.beena.densha import (
    PRINTED,
    STAT_KEYS,
    build_densha,
    decode_densha,
    densha_entries,
    densha_named,
    densha_text,
    match,
)
from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_types import GameOrder
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.said import in_japanese

FIXTURE: Final = Path(__file__).parent.parent / "fixtures" / "oracle" / "densha.json"
RECORDED: Final = json.loads(FIXTURE.read_text(encoding="utf-8"))["cards"]
ANY: Final = Constraint.anything()
E1: Final = "100010110011"
TEST_CARD: Final = "101110111011"


def order(ident: int | None) -> GameOrder:
    return GameOrder(ident, (ANY, ANY, ANY))


@pytest.mark.parametrize("card", RECORDED, ids=lambda card: card["barcode"])
def test_a_code_is_listed_exactly_when_the_game_read_it(card: dict[str, object]) -> None:
    assert (match(str(card["barcode"])) is not None) == card["read"]


def test_every_code_the_game_ignored_left_its_page_untouched() -> None:
    ignored = {card["changed"] for card in RECORDED if not card["read"]}

    assert ignored == {0.0}


def test_every_listed_card_was_recorded() -> None:
    recorded = {card["barcode"] for card in RECORDED}

    assert {card.code for card in PRINTED} <= recorded


def test_the_game_has_fifty_cards_and_a_test_card() -> None:
    assert len(PRINTED) == 51


def test_a_card_is_named_as_it_prints_its_train() -> None:
    card = decode_densha(E1)

    text = densha_text(card)

    assert card.kind is GameKind.ITEM
    assert text.name == ("E1 Series Max Tanigawa", "E1系 Maxたにがわ")
    assert text.detail == ("Train card", "でんしゃの カード")
    assert text.power == ("04", "04")


def test_a_card_whose_name_is_unknown_keeps_its_number() -> None:
    sixteen = next(card for card in PRINTED if card.number == 16)

    assert sixteen.name == ("Train card 16", "でんしゃカード 16")


def test_a_card_is_named_as_its_scan_prints_its_train() -> None:
    names = {card.number: card.name for card in PRINTED}

    assert (names[22], names[24]) == (
        ("485 Series Yamanami", "485系 やまなみ"),
        ("485 Series NO.DO.KA", "485系 NO.DO.KA"),
    )


def test_the_test_card_says_what_it_is() -> None:
    assert densha_text(decode_densha(TEST_CARD)).name == ("Test card", "テストカード")


def test_a_code_no_card_carries_is_refused_in_both_languages() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="no Densha Daishuugou card") as raised:
        decode_densha("100000000011")

    assert in_japanese(raised.value.args[0])


def test_a_code_that_is_not_twelve_places_is_refused() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="12"):
        decode_densha("1000101100")


@pytest.mark.parametrize("ident", list(range(len(PRINTED))), ids=str)
def test_every_card_builds_and_reads_back_as_itself(ident: int) -> None:
    card = build_densha(order(ident))

    assert card is not None
    assert decode_densha(card.barcode).ident == ident


def test_the_first_card_is_built_when_none_is_named() -> None:
    card = build_densha(order(None))

    assert card is not None
    assert card.ident == 0


def test_a_number_past_the_list_builds_nothing() -> None:
    assert build_densha(order(len(PRINTED))) is None


def test_a_card_is_found_by_place_code_or_card_number() -> None:
    assert densha_named(E1) == 3
    assert densha_named("3") == 3
    assert densha_named("04") == 3
    with pytest.raises(ValueError, match="Densha Daishuugou"):
        densha_named("Pikachu")


def test_every_entry_names_its_card_in_both_languages() -> None:
    entries = densha_entries()

    assert len(entries) == len(PRINTED)
    assert all(entry.english and entry.japanese for entry in entries)


def test_the_cards_carry_no_numbers() -> None:
    assert STAT_KEYS == ()
    assert decode_densha(E1).game is Device.DENSHA
