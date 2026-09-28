"""Tests for the battlers Hatayama Hatch no Pro Yakyuu News! reads."""

import json
from pathlib import Path

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.decoder.errors import BarcodeError
from maeyomi.games.hatayama import (
    BLIZZARD,
    WARRIOR,
    WIZARD,
    HatayamaOrder,
    build_hatayama,
    decode_hatayama,
    strongest_hatayama,
)
from maeyomi.models.constraint import Constraint

ANY = Constraint.anything()
FIXTURE = Path(__file__).parent.parent / "fixtures" / "oracle" / "hatayama.json"


def recorded() -> list[dict[str, object]]:
    return json.loads(FIXTURE.read_text("utf-8"))["cards"]


def numbers(barcode: str) -> tuple[int, int, int, int]:
    card = decode_hatayama(barcode)
    return (card.value("WHP"), card.value("WST"), card.value("WDF"), card.value("WMP"))


def test_epochs_own_layout_reads_the_numbers_in_place() -> None:
    card = decode_hatayama("9999999295997")

    assert (card.kind, card.ident) == (GameKind.FIGHTER, WIZARD)
    assert numbers("9999999295997") == (99900, 19900, 19900, 99)


def test_any_other_code_is_read_from_the_end() -> None:
    assert numbers("4594701255266") == (45900, 14700, 10100, 0)
    assert decode_hatayama("4594701255266").ident == WARRIOR


def test_a_type_of_five_or_more_is_refused() -> None:
    assert decode_hatayama("0000000500005").kind is GameKind.NO_EFFECT


def test_the_last_digit_also_picks_the_strategy_card() -> None:
    assert decode_hatayama("4912345678010").traits[1] == BLIZZARD


def test_a_built_wizard_reads_back_as_the_numbers_and_magic_asked_for() -> None:
    order = HatayamaOrder(
        WIZARD,
        (Constraint.exactly(35900), Constraint.exactly(15000), Constraint.exactly(9900)),
        (("mp", 42),),
    )

    card = build_hatayama(order)

    assert card is not None
    assert numbers(card.barcode) == (35900, 15000, 9900, 42)


def test_numbers_the_game_cannot_read_build_no_card() -> None:
    order = HatayamaOrder(WARRIOR, (Constraint.exactly(35000), ANY, ANY))

    assert build_hatayama(order) is None


def test_the_strongest_card_is_a_wizard_at_every_ceiling() -> None:
    assert numbers(strongest_hatayama().barcode) == (99900, 19900, 19900, 99)


def test_a_malformed_code_is_refused() -> None:
    with pytest.raises(BarcodeError):
        decode_hatayama("9999999295990")


@pytest.mark.parametrize("entry", recorded(), ids=lambda entry: str(entry["barcode"]))
def test_every_code_reads_as_the_game_itself_read_it_in_mame(entry: dict[str, object]) -> None:
    card = decode_hatayama(str(entry["barcode"]))

    if entry.get("refused"):
        assert card.kind is GameKind.NO_EFFECT
    else:
        wanted = (entry["stamina"], entry["attack"], entry["defense"], entry["mp"], entry["wizard"])
        read = numbers(str(entry["barcode"]))
        assert (read[0] // 100, read[1] // 100, read[2] // 100, read[3], card.ident) == wanted
