"""Tests for reading and building Datach Ultraman Club cards."""

import json
from pathlib import Path

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.datach.game_reader import printable
from maeyomi.datach.ultraman import (
    STAT_KEYS,
    UltramanOrder,
    build_ultraman,
    codes_of,
    decode_ultraman,
    strongest_ultraman,
)
from maeyomi.decoder.errors import BarcodeError
from maeyomi.models.constraint import Constraint

FIXTURE = Path(__file__).parent.parent / "fixtures" / "oracle" / "datach_ultraman.json"


def recorded() -> list[dict[str, object]]:
    return json.loads(FIXTURE.read_text("utf-8"))["cards"]


def exactly(pw: int, st: int, sp: int) -> tuple[Constraint, Constraint, Constraint]:
    return Constraint.exactly(pw), Constraint.exactly(st), Constraint.exactly(sp)


@pytest.mark.parametrize("entry", recorded(), ids=lambda entry: str(entry["barcode"]))
def test_every_code_reads_as_the_game_itself_read_it_in_mame(entry: dict[str, object]) -> None:
    card = decode_ultraman(str(entry["barcode"]))

    assert (card.ident, *(card.value(key) for key in STAT_KEYS)) == (
        entry["type"],
        entry["pw"],
        entry["st"],
        entry["sp"],
    )


def test_a_type_from_32_up_is_an_item_and_one_below_is_a_fighter() -> None:
    zoffy, father = decode_ultraman("0315424322677"), decode_ultraman("0416434374356")

    assert (zoffy.kind, father.kind) == (GameKind.FIGHTER, GameKind.ITEM)


def test_a_malformed_code_is_refused_before_it_is_read() -> None:
    with pytest.raises(BarcodeError):
        decode_ultraman("0315424322670")


def test_a_card_is_built_with_exactly_the_type_and_numbers_asked_for() -> None:
    card = build_ultraman(UltramanOrder(3, *exactly(7200, 6900, 4800)))

    assert card is not None
    assert (card.ident, *(card.value(key) for key in STAT_KEYS)) == (3, 7200, 6900, 4800)
    assert printable(card.barcode)


def test_a_card_built_within_ranges_lands_inside_them() -> None:
    order = UltramanOrder(
        None, Constraint.between(100, 900), Constraint.at_least(9000), Constraint.anything()
    )

    card = build_ultraman(order)

    assert card is not None
    assert 100 <= card.value("PW") <= 900
    assert card.value("UST") >= 9000


def test_a_number_the_game_cannot_hold_builds_no_card() -> None:
    assert build_ultraman(UltramanOrder(0, *exactly(7250, 100, 100))) is None


def test_the_strongest_card_carries_the_highest_number_in_all_three() -> None:
    card = strongest_ultraman()

    assert [card.value(key) for key in STAT_KEYS] == [9900, 9900, 9900]
    assert card.kind is GameKind.FIGHTER


def test_a_type_the_game_does_not_have_has_no_strongest_card() -> None:
    with pytest.raises(RuntimeError, match="no printable Ultraman Club card is type 31"):
        strongest_ultraman(31)


def test_a_stream_no_digit_can_build_yields_no_code() -> None:
    assert list(codes_of(1)) == []
