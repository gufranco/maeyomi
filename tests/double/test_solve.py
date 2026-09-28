"""Tests for building a Barcode Battler II Double card with the 7-read."""

import pytest

from maeyomi.double.abilities import DoubleAbility
from maeyomi.double.card import DoubleReading
from maeyomi.double.cheat import build_double_card, strongest_double_card, strongest_double_items
from maeyomi.double.decode import decode_double
from maeyomi.double.solve import solve_double
from maeyomi.models.card_request import CardRequest
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.constraint import Constraint
from maeyomi.models.race import Race


def test_a_fully_specified_card_decodes_to_exactly_the_request() -> None:
    request = CardRequest(
        hp=Constraint.exactly(82700),
        st=Constraint.exactly(18800),
        df=Constraint.exactly(18900),
        job=9,
        special=27,
    )

    outcome = solve_double(request)

    assert outcome.card is not None
    assert outcome.card.barcode == "7821818898978"
    assert decode_double(outcome.card.barcode) == outcome.card


def test_attack_and_defence_reach_the_published_ninety_nine_thousand_nine_hundred() -> None:
    request = CardRequest(st=Constraint.exactly(99900), df=Constraint.exactly(99900))

    outcome = solve_double(request)

    assert outcome.card is not None
    assert (outcome.card.st, outcome.card.df) == (99900, 99900)
    assert outcome.card.reading is DoubleReading.SEVEN


def test_a_special_power_fixes_two_of_the_health_digits() -> None:
    outcome = solve_double(CardRequest(special=29, hp=Constraint.at_least(90000)))

    assert outcome.card is not None
    assert outcome.card.hp == 92900


def test_a_class_picks_a_job_that_belongs_to_it() -> None:
    outcome = solve_double(CardRequest(character_class=CharacterClass.MAGICIAN))

    assert outcome.card is not None
    assert outcome.card.job == 7


@pytest.mark.parametrize(
    ("request_", "reason"),
    [
        (CardRequest(race=Race.WEAPON), "a 7-read card is always a fighter"),
        (CardRequest(speed=3), "a 7-read card has no speed any source records"),
        (CardRequest(pp=Constraint.exactly(3)), "a 7-read card carries no herbs or magic points"),
        (CardRequest(hp=Constraint.exactly(150)), "hp of 150 is not a multiple of 100"),
        (CardRequest(st=Constraint.exactly(100000)), "st of 100000 is above the ceiling of 99900"),
        (
            CardRequest(special=29, hp=Constraint.exactly(91000)),
            "special power 29 needs the health's thousands digit 2 and hundreds digit 9",
        ),
    ],
    ids=["race", "speed", "points", "multiple", "ceiling", "coupling"],
)
def test_an_impossible_request_names_the_reason(request_: CardRequest, reason: str) -> None:
    outcome = solve_double(request_)

    assert outcome.card is None
    assert reason in outcome.blockers


def test_the_cheat_fighter_holds_the_published_ceilings_and_halves_the_opponent() -> None:
    card = strongest_double_card().character

    assert (card.hp, card.st, card.df) == (92900, 99900, 99900)
    assert card.special.code == 29
    assert card.special.description == "opponent HP down 50%"


def test_no_health_above_the_cheat_can_carry_its_power() -> None:
    above = CardRequest(special=29, hp=Constraint.at_least(93000))

    assert solve_double(above).card is None


def test_every_cheat_item_carries_a_power_the_double_documents() -> None:
    items = strongest_double_items()

    assert all(item.character.special.is_documented for item in items)
    assert len({item.character.special.code for item in items}) == len(items)


@pytest.mark.parametrize(
    "impossible",
    [
        CardRequest(name="Broken", hp=Constraint.exactly(150)),
        CardRequest(name="Broken", race=Race.WEAPON, st=Constraint.exactly(20000)),
    ],
    ids=["seven-read", "item"],
)
def test_a_card_that_cannot_be_built_is_refused_by_name(impossible: CardRequest) -> None:
    with pytest.raises(RuntimeError, match="Broken cannot be built"):
        build_double_card(impossible)


@pytest.mark.parametrize("code", [-1, 100])
def test_a_power_outside_two_digits_is_refused(code: int) -> None:
    with pytest.raises(ValueError, match="outside 00-99"):
        DoubleAbility.from_code(code)


@pytest.mark.parametrize(
    "race", [Race.MECHANICAL, Race.ANIMAL, Race.AQUATIC, Race.BIRD, Race.HUMAN]
)
def test_a_seven_read_card_is_built_with_the_race_asked_for(race: Race) -> None:
    outcome = solve_double(CardRequest(race=race, st=Constraint.at_least(50000)))

    assert outcome.card is not None
    assert (outcome.card.race, outcome.card.st >= 50000) == (race, True)
