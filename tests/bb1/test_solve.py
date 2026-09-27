"""Tests for building a first Barcode Battler card to order."""

import pytest

from maeyomi.bb1.decode import decode_first
from maeyomi.bb1.solve import solve_first
from maeyomi.models.card_request import CardRequest
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.constraint import Constraint
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType


def test_a_fully_specified_fighter_decodes_to_exactly_the_request() -> None:
    request = CardRequest(
        race=Race.BIRD,
        job=9,
        speed=7,
        special=5,
        hp=Constraint.exactly(19900),
        st=Constraint.exactly(9900),
        df=Constraint.exactly(9900),
    )

    outcome = solve_first(request)

    assert outcome.card is not None
    assert outcome.card == decode_first(outcome.card.barcode)
    assert (outcome.card.hp, outcome.card.st, outcome.card.df) == (19900, 9900, 9900)
    assert (outcome.card.race, outcome.card.job, outcome.card.dx, outcome.card.flag.code) == (
        Race.BIRD,
        9,
        7,
        5,
    )


def test_a_range_is_met_by_its_lowest_reachable_value() -> None:
    request = CardRequest(race=Race.HUMAN, hp=Constraint.between(2000, 3000))

    outcome = solve_first(request)

    assert outcome.card is not None
    assert outcome.card.hp == 2000


@pytest.mark.parametrize(
    ("request_", "carried"),
    [
        (CardRequest(race=Race.WEAPON, st=Constraint.exactly(4500)), (0, 4500, 0)),
        (CardRequest(race=Race.SINGLE_USE_ARMOUR, df=Constraint.exactly(300)), (0, 0, 300)),
        (CardRequest(race=Race.SUPPORT_ITEM, hp=Constraint.exactly(19900)), (19900, 0, 0)),
    ],
    ids=["weapon", "armour", "potion"],
)
def test_an_item_carries_only_what_was_asked(
    request_: CardRequest, carried: tuple[int, int, int]
) -> None:
    outcome = solve_first(request_)

    assert outcome.card is not None
    assert (outcome.card.hp, outcome.card.st, outcome.card.df) == carried


@pytest.mark.parametrize(
    ("request_", "reason"),
    [
        (CardRequest(hp=Constraint.exactly(20000)), "hp of 20000 is above the ceiling of 19900"),
        (CardRequest(st=Constraint.exactly(10000)), "st of 10000 is above the ceiling of 9900"),
        (CardRequest(df=Constraint.exactly(150)), "df of 150 is not a multiple of 100"),
        (
            CardRequest(character_class=CharacterClass.MAGICIAN),
            "every fighter on the first Barcode Battler is a warrior",
        ),
        (
            CardRequest(pp=Constraint.exactly(5)),
            "the first Barcode Battler has no herbs or magic points",
        ),
    ],
    ids=["hp", "st", "multiple", "magician", "herbs"],
)
def test_an_impossible_request_names_the_field(request_: CardRequest, reason: str) -> None:
    outcome = solve_first(request_)

    assert outcome.card is None
    assert reason in outcome.blockers


def test_an_enemy_read_from_the_back_carries_the_requested_numbers() -> None:
    request = CardRequest(
        hp=Constraint.exactly(10000), st=Constraint.exactly(1900), df=Constraint.exactly(900)
    )

    outcome = solve_first(request, read_type=ReadType.BACK)

    assert outcome.card is not None
    assert outcome.card.read_type is ReadType.BACK
    assert (outcome.card.hp, outcome.card.st, outcome.card.df) == (10000, 1900, 900)


def test_an_enemy_is_tuned_so_both_sources_agree_it_has_no_flag() -> None:
    outcome = solve_first(CardRequest(hp=Constraint.exactly(4200)), read_type=ReadType.BACK)

    assert outcome.card is not None
    assert outcome.card.barcode[-1] == "0"
    assert outcome.card.flag.code == 0


@pytest.mark.parametrize(
    ("request_", "reason"),
    [
        (
            CardRequest(st=Constraint.exactly(2000)),
            "st of 2000 is outside the enemy range of 1000 to 1900",
        ),
        (
            CardRequest(df=Constraint.exactly(1000)),
            "df of 1000 is outside the enemy range of 100 to 900",
        ),
        (
            CardRequest(hp=Constraint.exactly(10100)),
            "hp of 10100 is outside the enemy range of 100 to 10000",
        ),
        (
            CardRequest(race=Race.HUMAN),
            "an enemy read from the back has no race any source records",
        ),
        (CardRequest(special=5), "an enemy's flag is disputed, see bb1_back_read_flag"),
    ],
    ids=["st", "df", "hp", "race", "flag"],
)
def test_an_impossible_enemy_names_the_field(request_: CardRequest, reason: str) -> None:
    outcome = solve_first(request_, read_type=ReadType.BACK)

    assert outcome.card is None
    assert reason in outcome.blockers


def test_a_request_no_candidate_meets_says_so() -> None:
    outcome = solve_first(CardRequest(race=Race.WEAPON, speed=3))

    assert outcome.card is None
    assert outcome.blockers == ("no barcode satisfies every constraint at once",)


@pytest.mark.parametrize("request_", [CardRequest(speed=4), CardRequest(job=5)], ids=["dx", "job"])
def test_an_enemy_takes_no_dx_and_no_job_but_two(request_: CardRequest) -> None:
    outcome = solve_first(request_, read_type=ReadType.BACK)

    assert "an enemy has no DX any source records and always has occupation 2" in (outcome.blockers)
