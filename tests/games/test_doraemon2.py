"""Tests for the barcodes Doraemon 2 reads on its password screen and in its menus."""

from maeyomi.datach.game_card import GameKind
from maeyomi.games.doraemon2 import DORAEMON2
from maeyomi.games.effects import decode_effect

LIVES = 2
AIR_CANNON = 15


def test_a_check_digit_of_two_sets_the_lives_on_the_password_screen() -> None:
    card = decode_effect("4937543597932", DORAEMON2)

    assert (card.kind, card.ident) == (GameKind.EFFECT, LIVES)


def test_a_code_the_password_screen_refuses_can_still_give_a_secret_tool() -> None:
    assert decode_effect("4906898575315", DORAEMON2).ident == AIR_CANNON


def test_a_code_neither_screen_takes_does_nothing() -> None:
    assert decode_effect("4912345678911", DORAEMON2).kind is GameKind.NO_EFFECT
