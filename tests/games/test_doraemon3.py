"""Tests for the barcodes Doraemon 3 reads on its password screen and in play."""

from maeyomi.datach.game_card import GameKind
from maeyomi.games.doraemon3 import DORAEMON3
from maeyomi.games.effects import decode_effect

WORLD = 10
LIVES_NINE = 115


def test_a_check_digit_of_two_starts_a_later_world() -> None:
    card = decode_effect("4525066031042", DORAEMON3)

    assert (card.kind, card.ident) == (GameKind.EFFECT, WORLD)


def test_the_second_pair_of_matching_digits_wins_over_the_first_in_play() -> None:
    assert decode_effect("4923796551548", DORAEMON3).ident == LIVES_NINE


def test_a_code_neither_screen_takes_does_nothing() -> None:
    assert decode_effect("4912345678911", DORAEMON3).kind is GameKind.NO_EFFECT
