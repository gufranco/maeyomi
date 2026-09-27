"""Tests for reading a barcode the way Datach Dragon Ball Z reads it."""

import pytest

from maeyomi.datach.dbz import DbzKind, decode_dbz, stream_of
from maeyomi.decoder.errors import CheckDigitError


def test_gokus_card_reads_as_the_game_showed_it() -> None:
    card = decode_dbz("0022248300117")

    assert card.kind is DbzKind.FIGHTER
    assert (card.character, card.level) == (0, 1)
    assert (card.hp, card.bp, card.dp) == (49500, 28250, 22750)


def test_the_stream_is_the_value_the_game_built_in_ram() -> None:
    assert stream_of("0022248300117") == 0x4114190500


def test_an_eight_digit_code_mirrors_five_of_its_digits() -> None:
    card = decode_dbz("50184385")

    assert (card.character, card.level) == (19, None)
    assert (card.hp, card.bp, card.dp) == (37500, 39750, 13250)


@pytest.mark.parametrize(
    ("code", "form"),
    [("0022738106373", 11), ("9210340180138", 9), ("0068400144373", 7)],
    ids=["super-saiyan-vegeta", "super-saiyan-goku", "vegeta-stays"],
)
def test_a_character_strong_enough_takes_its_stronger_form(code: str, form: int) -> None:
    assert decode_dbz(code).character == form


def test_an_item_card_names_an_item_and_carries_no_numbers() -> None:
    card = decode_dbz("0162347145254")

    assert card.kind is DbzKind.ITEM
    assert card.character == 44
    assert (card.hp, card.bp, card.dp, card.level) == (0, 0, 0, None)


def test_the_hidden_stream_gives_the_fixed_card() -> None:
    card = decode_dbz("0102425373735")

    assert card.kind is DbzKind.HIDDEN
    assert (card.hp, card.bp, card.dp) == (59000, 49990, 49990)
    assert (card.character, card.level) == (9, 3)


def test_a_wrong_check_digit_is_refused() -> None:
    with pytest.raises(CheckDigitError):
        decode_dbz("0022248300116")
