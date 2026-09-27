"""Tests for the strongest first Barcode Battler cards."""

import pytest

from maeyomi.bb1.cheat import build_first_card, strongest_first_card, strongest_first_items
from maeyomi.bb1.decode import decode_first
from maeyomi.bb1.solve import solve_first
from maeyomi.models.card_request import CardRequest
from maeyomi.models.constraint import Constraint
from maeyomi.models.race import Race


def test_the_cheat_fighter_holds_every_ceiling_at_once() -> None:
    card = strongest_first_card().character

    assert (card.hp, card.st, card.df) == (19900, 9900, 9900)
    assert (card.job, card.dx, card.flag.code) == (9, 9, 5)
    assert decode_first(card.barcode) == card


@pytest.mark.parametrize(
    "above",
    [
        CardRequest(hp=Constraint.exactly(20000)),
        CardRequest(st=Constraint.exactly(10000)),
        CardRequest(df=Constraint.exactly(10000)),
    ],
    ids=["hp", "st", "df"],
)
def test_nothing_above_the_cheat_fighter_can_be_built(above: CardRequest) -> None:
    assert solve_first(above).card is None


def test_each_item_carries_its_ceiling_and_its_own_flag() -> None:
    items = {card.character.race: card.character for card in strongest_first_items()}

    assert items[Race.WEAPON].st == 9900
    assert items[Race.ARMOUR].df == 9900
    assert items[Race.SUPPORT_ITEM].hp == 19900
    assert sorted(item.flag.code for item in items.values()) == [3, 6, 13]


def test_every_item_is_a_type_the_cheat_fighter_can_equip() -> None:
    for card in strongest_first_items():
        assert card.character.job == 0


def test_the_cards_carry_the_names_they_are_given() -> None:
    assert strongest_first_card("Grandma").name == "Grandma"


def test_a_card_that_cannot_be_built_is_refused_by_name() -> None:
    with pytest.raises(RuntimeError, match="Broken cannot be built"):
        build_first_card(CardRequest(name="Broken", hp=Constraint.exactly(20000)))
