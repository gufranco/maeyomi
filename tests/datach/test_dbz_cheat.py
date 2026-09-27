"""Tests for the strongest Datach Dragon Ball Z card."""

import pytest

from maeyomi.datach.dbz import DbzKind, decode_dbz
from maeyomi.datach.dbz_cheat import (
    CHEAT_CHARACTER,
    item_card,
    strongest_dbz_card,
    strongest_dbz_items,
    strongest_fighter,
)
from maeyomi.datach.dbz_tables import SECRET_CARD


def test_the_cheat_is_super_saiyan_goku_at_the_top_level() -> None:
    card = strongest_dbz_card().character

    assert card.kind is DbzKind.FIGHTER
    assert (card.character, card.level) == (CHEAT_CHARACTER, 3)
    assert decode_dbz(card.barcode) == card


def test_the_cheat_carries_the_most_the_rule_allows_in_printable_digits() -> None:
    card = strongest_dbz_card().character

    assert card.hp == 99500
    assert card.hp + card.bp + card.dp >= 181000


def test_the_cheat_outdoes_the_games_own_hidden_card() -> None:
    _, _, hp, bp, dp = SECRET_CARD
    card = strongest_dbz_card().character

    assert card.hp + card.bp + card.dp > (hp + bp + dp) * 10


def test_the_cheat_carries_its_name() -> None:
    assert strongest_dbz_card("Grandma").name == "Grandma"


def test_the_cheat_items_are_the_strongest_of_each_effect() -> None:
    items = strongest_dbz_items()

    assert [decode_dbz(card.barcode).character for card in items] == [33, 35, 39, 43, 45, 71]
    assert all(card.character.kind is DbzKind.ITEM for card in items)
    assert items[0].name == "Senzu bean"


def test_a_fighter_the_game_cannot_produce_has_no_strongest_card() -> None:
    with pytest.raises(RuntimeError, match="character 14 at level 3"):
        strongest_fighter(14, 3)


def test_an_item_the_game_cannot_produce_has_no_card() -> None:
    with pytest.raises(RuntimeError, match="item 60 cannot be built"):
        item_card(60)
