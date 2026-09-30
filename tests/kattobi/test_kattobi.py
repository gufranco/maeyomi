"""Tests for Kattobi Road's barcode reading, against what the game read in MAME."""

import json
from pathlib import Path
from typing import Final

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_types import GameOrder
from maeyomi.decoder.errors import CheckDigitError
from maeyomi.gameboy.kattobi import (
    POWER_KEY,
    STAT_KEYS,
    WEIGHT_KEY,
    build_kattobi,
    decode_kattobi,
    kattobi_entries,
    kattobi_named,
    kattobi_text,
    read_kattobi,
    strongest_kattobi,
)
from maeyomi.gameboy.kattobi_tables import NAMES
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.official.catalogue import OfficialSet, official_cards

FIXTURE: Final = Path(__file__).parent.parent / "fixtures" / "oracle" / "kattobi.json"
CARDS: Final = json.loads(FIXTURE.read_text(encoding="utf-8"))["cards"]
TRUCK: Final = "4902105002063"
F1: Final = "4987084410924"
ANY: Final = Constraint.anything()
MODELS: Final = 256
TRUCK_MODEL: Final = 188
F1_MODEL: Final = 7
KNOWN_CARDS: Final = 6


def order(ident: int | None) -> GameOrder:
    return GameOrder(ident, (ANY, ANY, ANY))


def word(record: bytes, offset: int) -> int:
    return record[offset] | record[offset + 1] << 8


def test_the_fixture_holds_every_scan() -> None:
    assert len(CARDS) >= 500


@pytest.mark.parametrize("card", CARDS, ids=[card["barcode"] for card in CARDS])
def test_the_car_matches_what_the_game_built(card: dict[str, str]) -> None:
    record = bytes.fromhex(card["record"])

    read = read_kattobi(card["barcode"])

    assert (read.model, read.power, read.torque, read.weight) == (
        record[0x1D],
        word(record, 10),
        word(record, 12),
        word(record, 14),
    )


def test_the_truck_card_reads_as_the_game_shows_it() -> None:
    card = decode_kattobi(TRUCK)

    text = kattobi_text(card)

    assert card.ident == TRUCK_MODEL
    assert card.game is Device.KATTOBI
    assert card.kind is GameKind.UNIT
    assert (card.value(POWER_KEY), card.value(WEIGHT_KEY)) == (227, 3890)
    assert text.name == ("Fowaarudo", "フォワールド")
    assert text.detail == ("Truck", "トラック")
    assert text.heading == ("Torque", "トルク")
    assert text.power == ("67.4 kg-m", "67.4 kg-m")


def test_the_f1_card_reads_as_the_formula_car() -> None:
    assert decode_kattobi(F1).ident == F1_MODEL


def test_the_fixture_holds_eight_digit_codes() -> None:
    assert sum(1 for card in CARDS if len(card["barcode"]) == 8) >= 20


def test_a_code_the_reader_cannot_scan_is_refused() -> None:
    with pytest.raises(CheckDigitError):
        decode_kattobi("4902105002060")


def test_every_model_is_listed() -> None:
    entries = kattobi_entries()

    assert [entry.ident for entry in entries] == list(range(MODELS))
    assert entries[TRUCK_MODEL].japanese == "フォワールド"


@pytest.mark.parametrize(
    ("typed", "expected"), [("188", 188), ("fowaarudo", 188), ("ガウディ", 43)]
)
def test_a_car_can_be_named_in_either_language_or_by_number(typed: str, expected: int) -> None:
    assert kattobi_named(typed) == expected


@pytest.mark.parametrize("typed", ["256", "Bicycle"])
def test_what_is_not_a_car_is_refused(typed: str) -> None:
    with pytest.raises(ValueError, match="no Kattobi Road car"):
        kattobi_named(typed)


@pytest.mark.parametrize("ident", range(MODELS))
def test_every_car_can_be_ordered_at_its_strongest(ident: int) -> None:
    card = build_kattobi(order(ident))

    assert card is not None
    assert card.ident == ident
    assert len(card.barcode) == 13


def test_no_recorded_code_gives_the_ordered_car_more_power() -> None:
    card = build_kattobi(order(TRUCK_MODEL))

    recorded = [read_kattobi(entry["barcode"]) for entry in CARDS]

    assert card is not None
    assert all(
        read.power <= card.value(POWER_KEY) for read in recorded if read.model == TRUCK_MODEL
    )


def test_an_order_for_what_is_not_a_car_is_refused() -> None:
    assert build_kattobi(order(MODELS)) is None


def test_an_order_for_any_car_gives_the_strongest() -> None:
    assert build_kattobi(order(None)) == strongest_kattobi()


def test_the_strongest_car_has_the_most_power_any_code_gives() -> None:
    card = strongest_kattobi()

    powers = [build_kattobi(order(ident)) for ident in range(MODELS)]

    assert card.value(POWER_KEY) == max(built.value(POWER_KEY) for built in powers if built)


def test_every_known_card_reads_as_the_car_it_is_named_for() -> None:
    cards = official_cards(OfficialSet.KATTOBI)

    names = [NAMES[decode_kattobi(card.barcode).ident] for card in cards]

    assert names == [card.name for card in cards]
    assert len(cards) == KNOWN_CARDS


def test_the_numbers_follow_from_the_car_so_nothing_is_ordered_by_number() -> None:
    assert STAT_KEYS == ()
