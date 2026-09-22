"""Tests for the card request model."""

import pytest

from barcode_battler.models.card_request import CardRequest
from barcode_battler.models.constraint import Constraint
from barcode_battler.models.race import Race


def test_an_empty_request_constrains_nothing() -> None:
    request = CardRequest()

    assert request.hp.admits(0)
    assert request.race is None
    assert request.name == ""


def test_a_request_carries_its_constraints() -> None:
    request = CardRequest(
        name="Fire Knight",
        hp=Constraint.exactly(5000),
        st=Constraint.at_least(1500),
        race=Race.HUMAN,
    )

    assert request.name == "Fire Knight"
    assert request.hp.exact_value == 5000
    assert request.st.admits(9900)
    assert request.race is Race.HUMAN


def test_a_job_digit_above_nine_is_rejected() -> None:
    with pytest.raises(ValueError, match="job"):
        CardRequest(job=10)


def test_a_negative_speed_is_rejected() -> None:
    with pytest.raises(ValueError, match="speed"):
        CardRequest(speed=-1)


def test_a_special_ability_above_ninety_nine_is_rejected() -> None:
    with pytest.raises(ValueError, match="special"):
        CardRequest(special=100)


def test_the_name_is_metadata_and_does_not_constrain_anything() -> None:
    named = CardRequest(name="Fire Knight", hp=Constraint.exactly(5000))
    unnamed = CardRequest(hp=Constraint.exactly(5000))

    assert named.hp == unnamed.hp
