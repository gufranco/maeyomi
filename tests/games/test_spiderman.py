"""Tests for the barcodes Spider-Man: Lethal Foes reads on its password screen."""

from maeyomi.datach.game_card import GameKind
from maeyomi.games.effects import decode_effect
from maeyomi.games.spiderman import SPIDERMAN

DEFEAT = 1
SOUNDS = 5


def test_a_check_digit_of_one_with_a_three_in_the_eighth_place_gives_endless_lives() -> None:
    card = decode_effect("4954323394871", SPIDERMAN)

    assert (card.kind, card.ident) == (GameKind.EFFECT, DEFEAT)


def test_the_box_code_opens_the_sound_test() -> None:
    assert decode_effect("4905040098504", SPIDERMAN).ident == SOUNDS


def test_a_code_no_test_matches_does_nothing() -> None:
    assert decode_effect("4912345678904", SPIDERMAN).kind is GameKind.NO_EFFECT
