"""Tests for the barcodes Donald Duck no Mahou no Boushi reads on its password screen."""

from maeyomi.datach.game_card import GameKind
from maeyomi.games.donald import DONALD
from maeyomi.games.effects import decode_effect

SKY_STAGE = 0
STAFF_ROLL = 7


def test_a_two_in_the_ninth_place_opens_the_stage_the_check_digit_names() -> None:
    card = decode_effect("4912345620040", DONALD)

    assert (card.kind, card.ident) == (GameKind.EFFECT, SKY_STAGE)


def test_a_two_in_the_eighth_place_instead_is_refused() -> None:
    assert decode_effect("4912345230010", DONALD).kind is GameKind.NO_EFFECT


def test_the_staff_roll_needs_epochs_own_prefix() -> None:
    assert decode_effect("4905040228437", DONALD).ident == STAFF_ROLL
    assert decode_effect("4915040020207", DONALD).kind is GameKind.NO_EFFECT
