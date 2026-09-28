"""Tests for the barcodes Alice no Paint Adventure reads on its password screen."""

from maeyomi.datach.game_card import GameKind
from maeyomi.games.alice import ALICE
from maeyomi.games.effects import decode_effect

CASTLE = 22
STAFF_ROLL = 31


def test_the_box_code_starts_the_castle_story() -> None:
    card = decode_effect("4905040098702", ALICE)

    assert (card.kind, card.ident) == (GameKind.EFFECT, CASTLE)


def test_epochs_other_prefix_goes_straight_to_the_staff_roll() -> None:
    assert decode_effect("4905040129062", ALICE).ident == STAFF_ROLL


def test_an_earlier_pattern_shadows_a_later_one_with_the_same_digits() -> None:
    assert decode_effect("4993287148021", ALICE).ident == 10
