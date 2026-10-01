"""Tests for Oshare Majo's card reading, against what the game's own decoder said."""

import json
from pathlib import Path
from typing import Final

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_types import GameEntry, GameOrder
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.nds.oshare import (
    ITEMS,
    STAT_KEYS,
    build_oshare,
    code_for,
    decode_oshare,
    item_of,
    oshare_entries,
    oshare_named,
    oshare_text,
)
from maeyomi.said import in_japanese

FIXTURE: Final = Path(__file__).parent.parent / "fixtures" / "oracle" / "oshare.json"
RECORDED: Final = json.loads(FIXTURE.read_text(encoding="utf-8"))["cards"]
ANY: Final = Constraint.anything()
GBE_PLUS: Final = {
    "OUQV-9AU5JD": "DUP  CB004",
    "O3OH4749GJG": "DUP  CL010",
    "OUSGC3RO6KD": "FtW  CS001",
    "OUMQ9CDKT4D": "FtW  SS004",
    "OUSPY5Q69GD": "H&M  Hr027",
    "OUMPDRQ69VD": "H&M  Hr002",
}


def order(ident: int | None) -> GameOrder:
    return GameOrder(ident, (ANY, ANY, ANY))


@pytest.mark.parametrize("card", RECORDED, ids=lambda card: card["barcode"])
def test_every_recorded_code_names_the_item_the_game_named(card: dict[str, str]) -> None:
    assert item_of(card["barcode"]) == card["item"]


def test_the_recording_holds_valid_cards_of_both_forms_and_refusals() -> None:
    items = [card["item"] for card in RECORDED]
    short = [card for card in RECORDED if card["barcode"][1] == "N" and card["item"]]

    assert items.count("") > 100
    assert len(short) >= 4


@pytest.mark.parametrize(("code", "item"), list(GBE_PLUS.items()))
def test_the_cards_gbe_plus_lists_name_their_items(code: str, item: str) -> None:
    assert item_of(code) == item


@pytest.mark.parametrize("entry", list(range(len(ITEMS))), ids=str)
def test_every_item_builds_a_card_the_game_reads_as_that_item(entry: int) -> None:
    card = build_oshare(order(entry))

    assert card is not None
    assert item_of(card.barcode) == ITEMS[entry]
    assert decode_oshare(card.barcode).ident == entry


def test_every_built_card_was_read_by_the_game() -> None:
    recorded = {card["barcode"]: card["item"] for card in RECORDED}

    assert all(recorded[code_for(item)] == item for item in ITEMS)


def test_a_built_card_carries_only_characters_code39_prints() -> None:
    texts = "".join(code_for(item) for item in ITEMS)

    assert set(texts) <= set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-. $/+%")


def test_every_item_the_game_keeps_a_card_image_for_and_can_read_is_listed() -> None:
    assert len(ITEMS) == 281


def test_a_card_reads_the_same_framed_by_its_start_and_stop() -> None:
    assert decode_oshare("*OUQV-9AU5JD*").ident == decode_oshare("OUQV-9AU5JD").ident


def test_a_refused_card_is_refused_in_both_languages() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="refuses") as raised:
        decode_oshare("OD3ED05OH0-")

    assert in_japanese(raised.value.args[0])


def test_an_item_without_a_card_image_is_refused() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="no card"):
        decode_oshare(code_for("DUP  CB099"))


def test_text_of_the_wrong_length_is_refused() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="11 characters"):
        decode_oshare("OUQV")


def test_a_character_code39_cannot_carry_is_refused() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="Code 39"):
        decode_oshare("ouqv-9au5jd")


def test_text_not_starting_with_o_is_refused() -> None:
    assert item_of("XUQV-9AU5JD") == ""


def test_a_card_names_its_item_in_both_languages() -> None:
    card = decode_oshare("OUQV-9AU5JD")

    text = oshare_text(card)

    assert card.kind is GameKind.ITEM
    assert text.name == ("Dress CB004", "ドレス CB004")
    assert text.detail == ("Dress", "ドレス")


@pytest.mark.parametrize(
    ("code", "name"),
    [
        ("OUSPY5Q69GD", ("Hair and make-up Hr027", "ヘアメイク Hr027")),
        ("OUSGC3RO6KD", ("Shoes CS001", "くつ CS001")),
    ],
)
def test_every_category_is_named(code: str, name: tuple[str, str]) -> None:
    assert oshare_text(decode_oshare(code)).name == name


def test_a_special_card_is_named() -> None:
    card = build_oshare(order(oshare_named("SP001")))

    assert card is not None
    assert oshare_text(card).name == ("Special SP001", "スペシャル SP001")


def test_a_card_is_found_by_code_name_or_number() -> None:
    first = oshare_entries()[0]

    assert oshare_named("CB004") == ITEMS.index("DUP  CB004")
    assert oshare_named("Dress CB004") == ITEMS.index("DUP  CB004")
    assert oshare_named(str(first.ident)) == first.ident
    with pytest.raises(ValueError, match="Oshare Majo"):
        oshare_named("ZZ999")


def test_the_first_card_is_built_when_none_is_named() -> None:
    card = build_oshare(order(None))

    assert card is not None
    assert card.ident == 0


def test_a_number_past_the_list_builds_nothing() -> None:
    assert build_oshare(order(len(ITEMS))) is None


def test_every_entry_is_an_item() -> None:
    entries = oshare_entries()

    assert all(isinstance(entry, GameEntry) and entry.kind is GameKind.ITEM for entry in entries)
    assert len(entries) == len(ITEMS)


def test_the_cards_carry_no_numbers() -> None:
    assert STAT_KEYS == ()
    assert decode_oshare("OUQV-9AU5JD").game is Device.OSHARE_MAJO
