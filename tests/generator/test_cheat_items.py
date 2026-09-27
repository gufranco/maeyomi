"""Tests for the strongest item of every kind, handed out beside the cheat card."""

import pytest

from maeyomi.decoder.decode import decode
from maeyomi.generator.carried import SUB_TYPE_FOR, Carried
from maeyomi.generator.cheat_items import ITEM_ABILITIES, build_item, strongest_items
from maeyomi.generator.quarantine import takes_quarantined_branch
from maeyomi.generator.solve import solve
from maeyomi.models.card_request import CardRequest
from maeyomi.models.constraint import Constraint
from maeyomi.models.race import Race


def by_race_and_job() -> dict[tuple[Race, int], int]:
    return {
        (card.character.race, card.character.job): index
        for index, card in enumerate(strongest_items())
    }


def test_every_item_decodes_to_what_it_claims() -> None:
    cards = strongest_items()

    assert [decode(card.barcode) for card in cards] == [card.character for card in cards]


def test_there_is_one_item_of_each_kind_that_lasts() -> None:
    kinds = by_race_and_job()

    assert set(kinds) == {
        (Race.WEAPON, 0),
        (Race.ARMOUR, 0),
        (Race.SUPPORT_ITEM, SUB_TYPE_FOR[Carried.HP]),
        (Race.SUPPORT_ITEM, SUB_TYPE_FOR[Carried.PP]),
        (Race.SUPPORT_ITEM, SUB_TYPE_FOR[Carried.MP]),
    }


def test_each_item_carries_the_most_its_digits_can_hold() -> None:
    cards = {card.character.race: card.character for card in strongest_items()[:2]}
    helpers = [card.character for card in strongest_items()[2:]]

    assert cards[Race.WEAPON].st == 9900
    assert cards[Race.ARMOUR].df == 9900
    assert [(helper.hp, helper.pp, helper.mp) for helper in helpers] == [
        (99900, 0, 0),
        (0, 99, 0),
        (0, 0, 99),
    ]


@pytest.mark.parametrize(
    "request_above",
    [
        CardRequest(st=Constraint.exactly(10000), race=Race.WEAPON),
        CardRequest(df=Constraint.exactly(10000), race=Race.ARMOUR),
        CardRequest(pp=Constraint.exactly(100), race=Race.SUPPORT_ITEM, job=7),
        CardRequest(mp=Constraint.exactly(100), race=Race.SUPPORT_ITEM, job=8),
    ],
    ids=["weapon", "armour", "herbs", "magic"],
)
def test_nothing_above_the_ceiling_can_be_built(request_above: CardRequest) -> None:
    assert solve(request_above).barcode is None


def test_no_two_items_share_a_special_power() -> None:
    codes = [card.character.special.code for card in strongest_items()]

    assert sorted(codes) == sorted(set(codes))
    assert codes == list(ITEM_ABILITIES.values())


def test_no_item_can_flip_its_sign_or_rests_on_an_unresolved_branch() -> None:
    for card in strongest_items():
        assert not card.character.sign_is_volatile
        assert not takes_quarantined_branch(card.barcode)


def test_an_item_that_cannot_be_built_is_refused_by_name() -> None:
    impossible = CardRequest(name="Broken", hp=Constraint.exactly(5050), race=Race.SUPPORT_ITEM)

    with pytest.raises(RuntimeError, match="Broken cannot be built"):
        build_item(impossible)
