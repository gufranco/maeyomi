"""Tests for the barcodes Doraemon: Nobita to Yousei no Kuni reads."""

from maeyomi.datach.game_card import GameKind
from maeyomi.games.effects import decode_effect
from maeyomi.games.yousei import YOUSEI

INVINCIBLE = 2
ATARUGAN = 18


def test_a_nine_last_and_a_four_in_the_sixth_place_makes_doraemon_invincible() -> None:
    card = decode_effect("2227948058889", YOUSEI)

    assert (card.kind, card.ident) == (GameKind.EFFECT, INVINCIBLE)


def test_a_matching_tenth_and_twelfth_digit_gives_a_gadget_on_the_item_screen() -> None:
    assert decode_effect("4983171008982", YOUSEI).ident == ATARUGAN


def test_the_gadget_doraemon_starts_with_changes_nothing() -> None:
    assert decode_effect("4919848151415", YOUSEI).kind is GameKind.NO_EFFECT
