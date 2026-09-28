"""Tests for the barcodes Lupin III reads on its password screen."""

from maeyomi.datach.game_card import GameKind
from maeyomi.games.effects import decode_effect
from maeyomi.games.lupin import LUPIN

NO_DAMAGE = 0
ITEM_MAX = 10


def test_a_five_in_the_eleventh_place_and_a_zero_in_the_eighth_makes_the_player_invincible() -> (
    None
):
    card = decode_effect("4914177063576", LUPIN)

    assert (card.kind, card.ident) == (GameKind.EFFECT, NO_DAMAGE)


def test_an_eight_first_and_a_one_in_the_eleventh_place_fills_every_item() -> None:
    card = decode_effect("4999619839148", LUPIN)

    assert card.ident == ITEM_MAX
