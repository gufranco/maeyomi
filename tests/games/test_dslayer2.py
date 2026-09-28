"""Tests for the barcodes Dragon Slayer: Eiyuu Densetsu II reads."""

from maeyomi.datach.game_card import GameKind
from maeyomi.games.dslayer2 import DSLAYER2
from maeyomi.games.effects import decode_effect

ALL_STATUS = 9
SUN_SWORD = 31
ANY_ITEM = 30
WARP_ALL = 20


def test_a_four_last_with_a_four_ninth_and_a_zero_twelfth_maxes_every_status() -> None:
    card = decode_effect("4900000040104", DSLAYER2)

    assert (card.kind, card.ident) == (GameKind.EFFECT, ALL_STATUS)


def test_the_prefix_code_gives_the_item_its_last_three_digits_number() -> None:
    assert decode_effect("0384388160168", DSLAYER2).ident == SUN_SWORD
    assert decode_effect("0384388160014", DSLAYER2).ident == ANY_ITEM


def test_nine_nine_nine_after_the_prefix_opens_every_warp() -> None:
    assert decode_effect("0384388169994", DSLAYER2).ident == WARP_ALL


def test_a_chapter_item_code_does_nothing_until_the_warps_are_open() -> None:
    assert decode_effect("4900100000008", DSLAYER2).kind is GameKind.NO_EFFECT
