"""Tests for the value constraint used to express a card request."""

import pytest

from maeyomi.models.constraint import Constraint


def test_an_unconstrained_value_admits_everything() -> None:
    constraint = Constraint.anything()

    assert constraint.admits(0)
    assert constraint.admits(99900)
    assert not constraint.is_exact


def test_an_exact_constraint_admits_one_value() -> None:
    constraint = Constraint.exactly(4000)

    assert constraint.admits(4000)
    assert not constraint.admits(4100)
    assert constraint.is_exact
    assert constraint.exact_value == 4000


def test_a_lower_bound_admits_everything_above_it() -> None:
    constraint = Constraint.at_least(1500)

    assert constraint.admits(1500)
    assert constraint.admits(99900)
    assert not constraint.admits(1400)


def test_an_upper_bound_admits_everything_below_it() -> None:
    constraint = Constraint.at_most(1500)

    assert constraint.admits(0)
    assert not constraint.admits(1600)


def test_a_range_admits_its_interior_and_both_ends() -> None:
    constraint = Constraint.between(5000, 6000)

    assert constraint.admits(5000)
    assert constraint.admits(6000)
    assert not constraint.admits(4900)


def test_values_walk_a_bounded_range_in_order() -> None:
    constraint = Constraint.between(5000, 5300)

    assert list(constraint.values(step=100, ceiling=99900)) == [5000, 5100, 5200, 5300]


def test_values_of_an_unbounded_constraint_stop_at_the_ceiling() -> None:
    constraint = Constraint.at_least(99700)

    assert list(constraint.values(step=100, ceiling=99900)) == [99700, 99800, 99900]


def test_an_inverted_range_is_rejected() -> None:
    with pytest.raises(ValueError, match="minimum"):
        Constraint.between(6000, 5000)


def test_the_exact_value_of_a_range_is_none() -> None:
    assert Constraint.between(5000, 6000).exact_value is None


def test_an_unbounded_constraint_renders_as_any() -> None:
    assert str(Constraint.anything()) == "any"


def test_a_lower_bound_renders_as_at_least() -> None:
    assert str(Constraint.at_least(1500)) == "at least 1500"


def test_an_upper_bound_renders_as_at_most() -> None:
    assert str(Constraint.at_most(1500)) == "at most 1500"


def test_a_range_renders_as_both_ends() -> None:
    assert str(Constraint.between(5000, 6000)) == "5000 to 6000"


def test_an_exact_constraint_renders_as_its_value() -> None:
    assert str(Constraint.exactly(4000)) == "4000"
