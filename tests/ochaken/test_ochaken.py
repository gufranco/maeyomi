"""Tests for TV Ocha-Ken's card reading, against what the machine said in MAME."""

import json
from pathlib import Path
from typing import Final

import pytest

from maeyomi.beena.ochaken import (
    PRINTED,
    STAT_KEYS,
    build_ochaken,
    decode_ochaken,
    match,
    ochaken_entries,
    ochaken_named,
    ochaken_text,
)
from maeyomi.datach.game_types import GameOrder
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.said import in_japanese

FIXTURE: Final = Path(__file__).parent.parent / "fixtures" / "oracle" / "tvochken.json"
RECORDED: Final = json.loads(FIXTURE.read_text(encoding="utf-8"))
CARDS: Final = RECORDED["cards"]
ANY: Final = Constraint.anything()
JAPANESE_TEA: Final = "0101000000001001"


def order(ident: int | None) -> GameOrder:
    return GameOrder(ident, (ANY, ANY, ANY))


@pytest.mark.parametrize("card", CARDS, ids=lambda card: card["barcode"])
def test_a_code_is_listed_exactly_when_the_machine_read_it(card: dict[str, object]) -> None:
    assert (match(str(card["barcode"])) is not None) == card["read"]


def test_every_code_the_machine_ignored_ended_where_a_blank_card_does() -> None:
    screens = {card["screen"] for card in CARDS if not card["read"]}

    assert screens == {RECORDED["ignored_screen"]}


def test_a_code_read_as_a_card_ends_where_that_card_does() -> None:
    screens = {card["barcode"]: card["screen"] for card in CARDS}
    read = [
        (card["screen"], screens[PRINTED[decode_ochaken(str(card["barcode"])).ident].code])
        for card in CARDS
        if card["read"]
    ]

    assert all(seen == expected for seen, expected in read)


def test_every_listed_card_was_recorded() -> None:
    recorded = {card["barcode"] for card in CARDS}

    assert {card.code for card in PRINTED} <= recorded


def test_the_machine_reads_fifty_cards() -> None:
    assert [card.number for card in PRINTED] == list(range(1, 51))


def test_a_card_is_named_as_it_prints_its_title() -> None:
    text = ochaken_text(decode_ochaken(JAPANESE_TEA))

    assert text.name == ("Japanese tea", "和のお茶")
    assert text.detail == ("Ocha-Ken card", "お茶犬の カード")
    assert text.power == ("01", "01")


def test_a_dog_card_names_the_dog_and_its_tea() -> None:
    names = {card.number: card.name for card in PRINTED}

    assert names[47] == ("Muha, the barley tea dog", "麦茶犬〈ムハ〉")


def test_a_code_no_card_carries_is_refused_in_both_languages() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="no TV Ocha-Ken card") as raised:
        decode_ochaken("0" * 16)

    assert in_japanese(raised.value.args[0])


def test_a_beena_code_is_no_ocha_ken_card() -> None:
    with pytest.raises(UnsupportedBarcodeError, match="no TV Ocha-Ken card"):
        decode_ochaken("100010110011")


@pytest.mark.parametrize("ident", list(range(len(PRINTED))), ids=str)
def test_every_card_builds_and_reads_back_as_itself(ident: int) -> None:
    card = build_ochaken(order(ident))

    assert card is not None
    assert decode_ochaken(card.barcode).ident == ident


def test_a_number_past_the_list_builds_nothing() -> None:
    assert build_ochaken(order(len(PRINTED))) is None


def test_a_card_is_found_by_name_or_card_number() -> None:
    assert ochaken_named("japanese tea") == 0
    assert ochaken_named("和のお茶") == 0
    assert ochaken_named("13") == 12
    with pytest.raises(ValueError, match="TV Ocha-Ken"):
        ochaken_named("Pikachu")


def test_every_entry_names_its_card_in_both_languages() -> None:
    entries = ochaken_entries()

    assert len(entries) == len(PRINTED)
    assert all(entry.english and entry.japanese for entry in entries)


def test_the_cards_carry_no_numbers() -> None:
    assert STAT_KEYS == ()
    assert decode_ochaken(JAPANESE_TEA).game is Device.OCHAKEN
