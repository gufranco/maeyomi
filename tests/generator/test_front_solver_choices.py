"""Tests for how the inverter narrows each field before it enumerates."""

import itertools

import pytest

from barcode_battler.decoder.decode import decode
from barcode_battler.generator.front_solver import iter_front_candidates
from barcode_battler.models.card_request import CardRequest
from barcode_battler.models.character_class import CharacterClass
from barcode_battler.models.constraint import Constraint
from barcode_battler.models.race import Race


def take(request: CardRequest, count: int) -> list[str]:
    return list(itertools.islice(iter_front_candidates(request), count))


def test_an_unconstrained_race_walks_every_race() -> None:
    request = CardRequest(
        hp=Constraint.exactly(4000),
        st=Constraint.exactly(1000),
        df=Constraint.exactly(500),
        job=3,
        special=0,
        speed=0,
    )

    races = {decode(code).race for code in take(request, 40)}

    assert set(Race) - races == set()


@pytest.mark.parametrize(
    ("requested", "allowed"),
    [
        (CharacterClass.WARRIOR, set(range(7))),
        (CharacterClass.MAGICIAN, {7, 8, 9}),
    ],
)
def test_a_requested_class_narrows_the_job_digit(
    requested: CharacterClass, allowed: set[int]
) -> None:
    request = CardRequest(
        hp=Constraint.exactly(4000),
        st=Constraint.exactly(1000),
        df=Constraint.exactly(500),
        race=Race.HUMAN,
        character_class=requested,
        special=0,
        speed=0,
    )

    jobs = {decode(code).job for code in take(request, 40)}

    assert jobs <= allowed
    assert jobs


def test_a_support_item_sub_type_is_inferred_from_a_strength_request() -> None:
    request = CardRequest(st=Constraint.exactly(300), race=Race.SUPPORT_ITEM)

    decoded = decode(take(request, 1)[0])

    assert decoded.job == 7
    assert decoded.pp == 3


def test_a_support_item_sub_type_is_inferred_from_a_defence_request() -> None:
    request = CardRequest(df=Constraint.exactly(500), race=Race.SUPPORT_ITEM)

    decoded = decode(take(request, 1)[0])

    assert decoded.job == 8
    assert decoded.mp == 5


def test_a_support_item_defaults_to_the_hit_point_sub_type() -> None:
    request = CardRequest(hp=Constraint.exactly(1200), race=Race.SUPPORT_ITEM)

    decoded = decode(take(request, 1)[0])

    assert decoded.job == 0
    assert decoded.hp == 1200


def test_an_item_request_pinned_to_speed_zero_uses_only_the_plain_carrier() -> None:
    request = CardRequest(st=Constraint.exactly(600), race=Race.WEAPON, speed=0)

    codes = take(request, 10)

    assert codes
    assert all(code[9] == "0" for code in codes)


def test_an_item_request_pinned_to_speed_five_uses_only_the_marker_carrier() -> None:
    request = CardRequest(st=Constraint.exactly(600), race=Race.WEAPON, speed=5)

    codes = take(request, 10)

    assert codes
    assert all(code[9] == "5" and code[2] == "9" for code in codes)


def test_an_item_request_pinned_to_another_speed_yields_nothing() -> None:
    request = CardRequest(st=Constraint.exactly(600), race=Race.WEAPON, speed=3)

    assert take(request, 1) == []


def test_a_zero_strength_support_item_still_picks_the_power_point_sub_type() -> None:
    request = CardRequest(st=Constraint.exactly(0), race=Race.SUPPORT_ITEM)

    decoded = decode(take(request, 1)[0])

    assert decoded.job == 7
