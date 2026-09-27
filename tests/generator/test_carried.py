"""Tests for the table of which numbers each kind of card carries."""

from dataclasses import replace

import pytest

from maeyomi.decoder.decode import decode
from maeyomi.generator.carried import SUB_TYPE_FOR, Carried, carried
from maeyomi.generator.solve import solve
from maeyomi.models.card_request import CardRequest
from maeyomi.models.constraint import Constraint
from maeyomi.models.race import Race


@pytest.mark.parametrize("race", [race for race in Race if race.is_fighter])
def test_a_fighter_carries_all_three_battle_numbers(race: Race) -> None:
    assert carried(race) == (Carried.HP, Carried.ST, Carried.DF)


@pytest.mark.parametrize("race", [Race.SINGLE_USE_WEAPON, Race.WEAPON])
def test_a_weapon_carries_attack_alone(race: Race) -> None:
    assert carried(race) == (Carried.ST,)


@pytest.mark.parametrize("race", [Race.SINGLE_USE_ARMOUR, Race.ARMOUR])
def test_armour_carries_defence_alone(race: Race) -> None:
    assert carried(race) == (Carried.DF,)


@pytest.mark.parametrize(
    ("job", "expected"),
    [
        (None, (Carried.HP,)),
        (0, (Carried.HP,)),
        (4, (Carried.HP,)),
        (5, ()),
        (6, ()),
        (7, (Carried.PP,)),
        (8, (Carried.MP,)),
        (9, (Carried.MP,)),
    ],
)
def test_a_helper_item_carries_what_its_sub_type_names(
    job: int | None, expected: tuple[Carried, ...]
) -> None:
    assert carried(Race.SUPPORT_ITEM, job) == expected


@pytest.mark.parametrize(
    ("field", "value"), [(Carried.PP, 99), (Carried.MP, 99), (Carried.HP, 800)]
)
def test_each_sub_type_the_table_names_solves_for_its_own_number(
    field: Carried, value: int
) -> None:
    request = replace(
        CardRequest(race=Race.SUPPORT_ITEM, job=SUB_TYPE_FOR[field]),
        **{field.value: Constraint.exactly(value)},
    )

    outcome = solve(request)

    assert outcome.barcode is not None
    assert getattr(decode(outcome.barcode), field.value) == value
