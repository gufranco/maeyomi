"""Tests for the item cards J.League Excite Stage '95 reads through the Barcode Battler II."""

import json
from pathlib import Path

import pytest

from maeyomi.datach.game_card import GameKind
from maeyomi.decoder.errors import BarcodeError
from maeyomi.games.excite95 import (
    HANDICAP,
    KICK_SPEED,
    NO_CARDS,
    OVERALL,
    PK_ITEM_NAMES,
    SAVING,
    build_excite95,
    decode_excite95,
    pk_reading,
    strongest_excite95,
)

TOP: int = 253
FIXTURE = Path(__file__).parent.parent / "fixtures" / "oracle" / "excite95.json"
PK_FIXTURE = Path(__file__).parent.parent / "fixtures" / "oracle" / "excite95_pk.json"


def recorded() -> list[dict[str, object]]:
    return json.loads(FIXTURE.read_text("utf-8"))["cards"]


@pytest.mark.parametrize("entry", recorded(), ids=lambda entry: str(entry["barcode"]))
def test_every_code_reads_as_the_game_itself_read_it_in_mame(entry: dict[str, object]) -> None:
    card = decode_excite95(str(entry["barcode"]))

    assert (card.ident, card.traits) == (entry["kind"], (entry["value"],))


def test_a_check_digit_below_eight_is_a_player_item_with_its_value() -> None:
    card = decode_excite95("4964262129977")

    assert (card.kind, card.ident, card.traits) == (GameKind.ITEM, OVERALL, (TOP,))


def test_an_odd_second_and_eighth_digit_make_it_a_keeper_item() -> None:
    assert decode_excite95("4938323640565").ident == SAVING


def test_a_check_digit_of_eight_or_nine_is_a_special_card() -> None:
    assert decode_excite95("4998403297928").ident == HANDICAP
    assert decode_excite95("4951454752778").ident == NO_CARDS


@pytest.mark.parametrize(
    ("kind", "value"),
    [(OVERALL, 0), (KICK_SPEED, 104), (SAVING, TOP), (HANDICAP, 4), (NO_CARDS, 1)],
)
def test_a_built_card_reads_back_as_the_kind_and_value_asked_for(kind: int, value: int) -> None:
    card = build_excite95(kind, value)

    assert card is not None
    assert (card.ident, card.traits) == (kind, (value,))


def test_a_value_the_kind_cannot_carry_builds_no_card() -> None:
    assert build_excite95(HANDICAP, 9) is None
    assert build_excite95(OVERALL, TOP + 1) is None


def test_the_strongest_card_raises_every_ability_by_the_most() -> None:
    card = strongest_excite95()

    assert (card.ident, card.traits) == (OVERALL, (TOP,))


def test_a_malformed_code_is_refused() -> None:
    with pytest.raises(BarcodeError):
        decode_excite95("4964262129970")


@pytest.mark.parametrize(
    "entry", json.loads(PK_FIXTURE.read_text(encoding="utf-8"))["cards"], ids=str
)
def test_every_code_reads_in_pk_mode_as_the_game_read_it_in_mame(entry: dict[str, object]) -> None:
    assert pk_reading(str(entry["barcode"])) == (entry["pk_item"], entry["value"])


def test_every_pk_item_is_named_in_both_languages() -> None:
    assert sorted(PK_ITEM_NAMES) == [8, 9, 11, 12]
    assert all(
        english.isascii() and not japanese.isascii() for english, japanese in PK_ITEM_NAMES.values()
    )
