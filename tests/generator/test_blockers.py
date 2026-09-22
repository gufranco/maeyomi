"""Tests for the per-field reasons a request cannot be satisfied."""

from maeyomi.generator.blockers import blockers
from maeyomi.models.card_request import CardRequest
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.constraint import Constraint
from maeyomi.models.race import Race


def test_a_satisfiable_request_has_no_blockers() -> None:
    request = CardRequest(hp=Constraint.exactly(5000), race=Race.HUMAN)

    assert blockers(request) == ()


def test_a_value_off_the_hundred_grid_names_the_field() -> None:
    reasons = blockers(CardRequest(hp=Constraint.exactly(5050)))

    assert any(reason.startswith("hp") and "multiple of 100" in reason for reason in reasons)


def test_a_value_above_the_ceiling_names_the_ceiling() -> None:
    reasons = blockers(CardRequest(st=Constraint.exactly(30000)))

    assert any("24500" in reason for reason in reasons)


def test_a_strength_the_dual_bonus_reaches_is_not_blocked() -> None:
    reasons = blockers(CardRequest(st=Constraint.exactly(24500)))

    assert not [reason for reason in reasons if reason.startswith("st")]


def test_a_negative_value_is_blocked() -> None:
    reasons = blockers(CardRequest(df=Constraint.exactly(-100)))

    assert any("below zero" in reason for reason in reasons)


def test_a_high_hit_point_value_off_the_marker_grid_explains_the_marker() -> None:
    reasons = blockers(CardRequest(hp=Constraint.exactly(25000)))

    assert any("marker" in reason and "900" in reason for reason in reasons)


def test_a_high_hit_point_value_on_the_marker_grid_is_not_blocked() -> None:
    assert blockers(CardRequest(hp=Constraint.exactly(20900))) == ()


def test_a_speed_that_the_marker_overrides_is_blocked() -> None:
    reasons = blockers(CardRequest(hp=Constraint.exactly(20900), speed=3))

    assert any("speed" in reason for reason in reasons)


def test_a_job_that_contradicts_the_requested_class_is_blocked() -> None:
    reasons = blockers(CardRequest(job=2, character_class=CharacterClass.MAGICIAN))

    assert any("contradicts" in reason for reason in reasons)


def test_a_job_that_agrees_with_the_requested_class_is_not_blocked() -> None:
    assert blockers(CardRequest(job=8, character_class=CharacterClass.MAGICIAN)) == ()
