"""Tests for the solver entry point and its verification loop."""

import pytest

from maeyomi.decoder.decode import decode
from maeyomi.generator.solve import DEFAULT_BUDGET, solve
from maeyomi.models.card_request import CardRequest
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.constraint import Constraint
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType


def fire_knight() -> CardRequest:
    return CardRequest(
        name="Fire Knight",
        hp=Constraint.exactly(5000),
        st=Constraint.exactly(1800),
        df=Constraint.exactly(1200),
        race=Race.HUMAN,
        character_class=CharacterClass.WARRIOR,
        special=17,
    )


def test_a_solvable_request_returns_a_verified_barcode() -> None:
    outcome = solve(fire_knight())

    assert outcome.barcode is not None
    assert outcome.character is not None
    assert outcome.mismatches == ()


def test_the_returned_barcode_decodes_to_the_request() -> None:
    outcome = solve(fire_knight())

    assert outcome.barcode is not None
    decoded = decode(outcome.barcode)

    assert (decoded.hp, decoded.st, decoded.df) == (5000, 1800, 1200)
    assert decoded.race is Race.HUMAN
    assert decoded.character_class is CharacterClass.WARRIOR
    assert decoded.special.code == 17


def test_a_fully_specified_request_is_solved_without_a_search() -> None:
    outcome = solve(fire_knight())

    assert outcome.searched == 1


def test_a_range_request_is_satisfied_inside_its_range() -> None:
    request = CardRequest(
        hp=Constraint.between(5000, 6000),
        st=Constraint.at_least(1500),
        df=Constraint.at_least(1000),
        race=Race.HUMAN,
    )

    outcome = solve(request)

    assert outcome.character is not None
    assert 5000 <= outcome.character.hp <= 6000
    assert outcome.character.st >= 1500
    assert outcome.character.df >= 1000


def test_a_hit_point_value_off_the_grid_is_reported_as_blocked() -> None:
    request = CardRequest(hp=Constraint.exactly(5050), race=Race.HUMAN)

    outcome = solve(request)

    assert outcome.barcode is None
    assert any("multiple of 100" in reason for reason in outcome.blockers)


def test_a_hit_point_value_above_the_ceiling_is_reported_as_blocked() -> None:
    request = CardRequest(hp=Constraint.exactly(120000), race=Race.HUMAN)

    outcome = solve(request)

    assert outcome.barcode is None
    assert any("99900" in reason for reason in outcome.blockers)


def test_a_high_hit_point_value_off_the_marker_grid_is_reported_as_blocked() -> None:
    request = CardRequest(hp=Constraint.exactly(25000), race=Race.HUMAN)

    outcome = solve(request)

    assert outcome.barcode is None
    assert any("900" in reason for reason in outcome.blockers)


def test_a_high_hit_point_request_with_a_conflicting_speed_is_reported_as_blocked() -> None:
    request = CardRequest(hp=Constraint.exactly(20900), race=Race.HUMAN, speed=3)

    outcome = solve(request)

    assert outcome.barcode is None
    assert any("speed" in reason for reason in outcome.blockers)


def test_a_class_that_contradicts_the_job_is_reported_as_blocked() -> None:
    request = CardRequest(
        hp=Constraint.exactly(5000),
        race=Race.HUMAN,
        job=2,
        character_class=CharacterClass.MAGICIAN,
    )

    outcome = solve(request)

    assert outcome.barcode is None
    assert any("class" in reason for reason in outcome.blockers)


def test_an_unsatisfiable_request_names_the_field_rather_than_failing_silently() -> None:
    request = CardRequest(st=Constraint.exactly(30000), race=Race.HUMAN)

    outcome = solve(request)

    assert outcome.barcode is None
    assert any("st" in reason for reason in outcome.blockers)


def test_the_search_budget_is_reported_rather_than_silently_truncated() -> None:
    request = CardRequest(
        hp=Constraint.exactly(5000),
        st=Constraint.exactly(1800),
        df=Constraint.exactly(1200),
        race=Race.HUMAN,
        speed=4,
        special=17,
        job=2,
    )

    outcome = solve(request, budget=0)

    assert outcome.barcode is None
    assert outcome.budget_exhausted
    assert outcome.searched == 0


def test_the_default_budget_is_stated_rather_than_implied() -> None:
    assert DEFAULT_BUDGET > 0


def test_an_item_request_is_solved() -> None:
    request = CardRequest(st=Constraint.exactly(600), race=Race.WEAPON, special=1)

    outcome = solve(request)

    assert outcome.character is not None
    assert outcome.character.st == 600


@pytest.mark.parametrize("hp", [20000, 21000, 25500])
def test_every_blocked_request_reports_at_least_one_reason(hp: int) -> None:
    outcome = solve(CardRequest(hp=Constraint.exactly(hp), race=Race.HUMAN))

    assert outcome.barcode is None
    assert outcome.blockers


def test_asking_an_item_for_a_speed_is_reported_rather_than_silently_ignored() -> None:
    request = CardRequest(st=Constraint.exactly(600), race=Race.WEAPON, speed=0)

    outcome = solve(request)

    assert outcome.barcode is None
    assert outcome.searched > 0
    assert outcome.blockers


def test_a_back_read_card_can_be_requested_explicitly() -> None:
    outcome = solve(CardRequest(race=Race.HUMAN), read_type=ReadType.BACK)

    assert outcome.character is not None
    assert outcome.character.read_type is ReadType.BACK
    assert outcome.character.race is Race.HUMAN


def test_a_back_read_request_that_cannot_be_met_is_reported() -> None:
    request = CardRequest(hp=Constraint.exactly(99900), race=Race.HUMAN)

    outcome = solve(request, read_type=ReadType.BACK)

    assert outcome.barcode is None
    assert outcome.blockers


def test_the_dual_bonus_reaches_a_strength_above_the_published_ceiling() -> None:
    request = CardRequest(
        hp=Constraint.exactly(99900),
        st=Constraint.exactly(24500),
        df=Constraint.exactly(19900),
        race=Race.MECHANICAL,
    )

    outcome = solve(request)

    assert outcome.blockers == ()
    assert outcome.character is not None
    assert outcome.character.st == 24500


def test_the_mirror_of_the_dual_bonus_reaches_the_same_defence() -> None:
    request = CardRequest(
        hp=Constraint.exactly(99900),
        st=Constraint.exactly(19900),
        df=Constraint.exactly(24500),
        race=Race.ANIMAL,
    )

    outcome = solve(request)

    assert outcome.character is not None
    assert outcome.character.df == 24500
