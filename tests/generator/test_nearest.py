"""Tests for the opt-in nearest match."""

import pytest

from maeyomi.decoder.decode import decode
from maeyomi.generator.nearest import (
    CATEGORICAL_FIELDS,
    DEFAULT_WINDOW,
    solve_nearest,
)
from maeyomi.generator.quarantine import takes_quarantined_branch
from maeyomi.generator.solve import solve
from maeyomi.models.card_request import CardRequest
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.constraint import Constraint
from maeyomi.models.race import Race


def unreachable() -> CardRequest:
    return CardRequest(
        hp=Constraint.exactly(20900),
        st=Constraint.exactly(11000),
        df=Constraint.exactly(10000),
        race=Race.MECHANICAL,
    )


def test_the_request_used_here_is_genuinely_unsolvable() -> None:
    assert solve(unreachable()).barcode is None


def test_the_nearest_match_returns_a_verified_barcode() -> None:
    outcome = solve_nearest(unreachable())

    assert outcome.barcode is not None
    assert outcome.character is not None
    assert decode(outcome.barcode) == outcome.character


def test_the_nearest_match_keeps_every_categorical_field_exact() -> None:
    outcome = solve_nearest(unreachable())

    assert outcome.character is not None
    assert outcome.character.race is Race.MECHANICAL


def test_the_nearest_match_reports_its_distance_and_what_differs() -> None:
    outcome = solve_nearest(unreachable())

    assert outcome.distance > 0
    assert outcome.differences


def test_a_request_that_is_already_solvable_comes_back_at_distance_zero() -> None:
    request = CardRequest(
        hp=Constraint.exactly(5000),
        st=Constraint.exactly(1800),
        df=Constraint.exactly(1200),
        race=Race.HUMAN,
    )

    outcome = solve_nearest(request)

    assert outcome.distance == 0
    assert outcome.differences == ()


def test_the_distance_is_the_sum_of_the_stat_gaps() -> None:
    outcome = solve_nearest(unreachable())

    assert outcome.character is not None
    expected = (
        abs(outcome.character.hp - 20900)
        + abs(outcome.character.st - 11000)
        + abs(outcome.character.df - 10000)
    )
    assert outcome.distance == expected


def test_an_unconstrained_stat_never_contributes_to_the_distance() -> None:
    request = CardRequest(hp=Constraint.exactly(5000), race=Race.HUMAN)

    outcome = solve_nearest(request)

    assert outcome.distance == 0


def test_a_categorical_field_is_never_approximated() -> None:
    request = CardRequest(
        hp=Constraint.exactly(20900),
        st=Constraint.exactly(11000),
        df=Constraint.exactly(10000),
        race=Race.MECHANICAL,
        job=4,
        special=7,
        speed=5,
    )

    outcome = solve_nearest(request)

    assert outcome.character is not None
    assert (outcome.character.job, outcome.character.special.code) == (4, 7)
    assert outcome.character.speed == 5


def test_a_value_off_the_hundred_grid_is_still_blocked() -> None:
    outcome = solve_nearest(CardRequest(hp=Constraint.exactly(5050), race=Race.HUMAN))

    assert outcome.barcode is None
    assert any("multiple of 100" in reason for reason in outcome.blockers)


def test_a_zero_window_still_searches_the_requested_hit_points() -> None:
    outcome = solve_nearest(unreachable(), window=0)

    assert outcome.character is not None
    assert outcome.character.hp == 20900


def test_an_item_request_is_reported_as_outside_this_search() -> None:
    request = CardRequest(st=Constraint.exactly(30000), race=Race.WEAPON)

    outcome = solve_nearest(request)

    assert outcome.barcode is None
    assert any("item" in reason for reason in outcome.blockers)


def test_the_search_size_is_reported() -> None:
    outcome = solve_nearest(unreachable())

    assert outcome.searched > 0


def test_the_default_window_and_the_protected_fields_are_stated() -> None:
    assert DEFAULT_WINDOW > 0
    assert CATEGORICAL_FIELDS == ("race", "job", "character_class", "special", "speed")


@pytest.mark.parametrize("race", [Race.MECHANICAL, Race.ANIMAL, Race.AQUATIC, Race.HUMAN])
def test_a_nearest_match_is_found_for_every_fighter_race(race: Race) -> None:
    request = CardRequest(
        hp=Constraint.exactly(20900),
        st=Constraint.exactly(11000),
        df=Constraint.exactly(10000),
        race=race,
    )

    outcome = solve_nearest(request)

    assert outcome.character is not None
    assert outcome.character.race is race


def test_the_nearest_match_never_rests_on_an_unresolved_branch() -> None:
    outcome = solve_nearest(unreachable())

    assert outcome.barcode is not None
    assert not takes_quarantined_branch(outcome.barcode)


def test_a_hit_point_range_with_nothing_on_the_marker_grid_is_reported() -> None:
    request = CardRequest(hp=Constraint.between(20000, 20800), race=Race.HUMAN)

    outcome = solve_nearest(request)

    assert outcome.barcode is None
    assert any("window" in reason for reason in outcome.blockers)


def test_a_solved_outcome_reports_itself_as_exact() -> None:
    request = CardRequest(hp=Constraint.exactly(5000), race=Race.HUMAN)

    assert solve_nearest(request).is_exact


def test_an_approximated_outcome_does_not_report_itself_as_exact() -> None:
    assert not solve_nearest(unreachable()).is_exact


def test_a_requested_magician_class_picks_a_magician_job() -> None:
    request = CardRequest(
        hp=Constraint.exactly(20900),
        st=Constraint.exactly(11000),
        df=Constraint.exactly(10000),
        race=Race.MECHANICAL,
        character_class=CharacterClass.MAGICIAN,
    )

    outcome = solve_nearest(request)

    assert outcome.character is not None
    assert outcome.character.character_class is CharacterClass.MAGICIAN


def test_a_zero_upper_bound_is_honoured_rather_than_read_as_absent() -> None:
    request = CardRequest(
        hp=Constraint.exactly(0),
        st=Constraint.exactly(0),
        df=Constraint.exactly(0),
        race=Race.HUMAN,
    )

    outcome = solve_nearest(request)

    assert outcome.character is not None
    assert (outcome.character.hp, outcome.character.st, outcome.character.df) == (0, 0, 0)


def test_a_value_above_a_zero_ceiling_counts_towards_the_distance() -> None:
    request = CardRequest(
        hp=Constraint.exactly(20900),
        st=Constraint.at_most(0),
        df=Constraint.exactly(10000),
        race=Race.MECHANICAL,
    )

    outcome = solve_nearest(request)

    assert outcome.character is not None
    assert outcome.distance >= outcome.character.st
