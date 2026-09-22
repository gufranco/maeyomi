"""Tests for the analytic inversion of the front reading."""

import itertools

import pytest

from barcode_battler.decoder.decode import decode
from barcode_battler.decoder.front_read import DUAL_BONUS_VALUES
from barcode_battler.generator.front_solver import iter_front_candidates, stat_digit_options
from barcode_battler.models.card_request import CardRequest
from barcode_battler.models.constraint import Constraint
from barcode_battler.models.race import Race
from barcode_battler.models.read_type import ReadType


def first(request: CardRequest) -> str:
    return next(iter(itertools.islice(iter_front_candidates(request), 1)))


def test_a_fully_specified_fighter_is_inverted_without_searching() -> None:
    request = CardRequest(
        hp=Constraint.exactly(5000),
        st=Constraint.exactly(1500),
        df=Constraint.exactly(1200),
        race=Race.HUMAN,
        job=3,
        speed=7,
        special=0,
    )

    candidates = list(itertools.islice(iter_front_candidates(request), 5))

    assert len(candidates) == 1
    assert decode(candidates[0]).hp == 5000


def test_the_single_candidate_decodes_to_every_requested_attribute() -> None:
    request = CardRequest(
        hp=Constraint.exactly(5000),
        st=Constraint.exactly(1800),
        df=Constraint.exactly(1200),
        race=Race.HUMAN,
        job=2,
        speed=4,
        special=17,
    )

    decoded = decode(first(request))

    assert decoded.read_type is ReadType.FRONT
    assert (decoded.hp, decoded.st, decoded.df) == (5000, 1800, 1200)
    assert decoded.race is Race.HUMAN
    assert (decoded.job, decoded.speed, decoded.special.code) == (2, 4, 17)


def test_a_low_hit_point_fighter_needs_no_marker() -> None:
    request = CardRequest(hp=Constraint.exactly(4000), race=Race.BIRD)

    code = first(request)

    assert code[0] in "01"
    assert decode(code).read_type is ReadType.FRONT


def test_a_high_hit_point_fighter_is_only_reachable_on_a_hundred_ending_in_nine() -> None:
    request = CardRequest(hp=Constraint.between(20000, 21000), race=Race.HUMAN)

    reachable = {decode(code).hp for code in itertools.islice(iter_front_candidates(request), 50)}

    assert reachable == {20900}


def test_a_high_hit_point_fighter_is_forced_to_speed_five() -> None:
    request = CardRequest(hp=Constraint.exactly(20900), race=Race.HUMAN)

    assert decode(first(request)).speed == 5


def test_a_high_hit_point_request_with_another_speed_yields_nothing() -> None:
    request = CardRequest(hp=Constraint.exactly(20900), race=Race.HUMAN, speed=3)

    assert list(itertools.islice(iter_front_candidates(request), 1)) == []


@pytest.mark.parametrize(
    ("race", "st", "df"),
    [
        (Race.MECHANICAL, 11000, 5000),
        (Race.ANIMAL, 5000, 11000),
        (Race.AQUATIC, 11000, 10000),
    ],
)
def test_the_high_hit_point_bonus_is_compensated_for_every_affected_race(
    race: Race, st: int, df: int
) -> None:
    request = CardRequest(
        hp=Constraint.exactly(20900),
        st=Constraint.exactly(st),
        df=Constraint.exactly(df),
        race=race,
    )

    decoded = decode(first(request))

    assert (decoded.st, decoded.df) == (st, df)
    assert decoded.race is race


@pytest.mark.parametrize("race", [Race.MECHANICAL, Race.ANIMAL])
def test_only_one_stat_can_be_raised_past_ninety_nine_hundred_at_high_hit_points(
    race: Race,
) -> None:
    request = CardRequest(
        hp=Constraint.exactly(20900),
        st=Constraint.exactly(11000),
        df=Constraint.exactly(10000),
        race=race,
    )

    assert list(itertools.islice(iter_front_candidates(request), 1)) == []


def test_a_weapon_carries_its_strength() -> None:
    request = CardRequest(st=Constraint.exactly(600), race=Race.WEAPON, special=1)

    decoded = decode(first(request))

    assert decoded.race is Race.WEAPON
    assert decoded.st == 600
    assert decoded.special.code == 1


def test_a_weapon_above_the_fallback_bound_uses_the_marker_path() -> None:
    request = CardRequest(st=Constraint.exactly(3000), race=Race.WEAPON)

    code = first(request)

    assert decode(code).st == 3000
    assert code[2] == "9"
    assert code[9] == "5"


def test_armour_carries_its_defence() -> None:
    request = CardRequest(df=Constraint.exactly(1900), race=Race.SINGLE_USE_ARMOUR)

    decoded = decode(first(request))

    assert decoded.race is Race.SINGLE_USE_ARMOUR
    assert decoded.df == 1900


def test_a_support_item_carries_hit_points() -> None:
    request = CardRequest(hp=Constraint.exactly(1200), race=Race.SUPPORT_ITEM, job=0)

    decoded = decode(first(request))

    assert decoded.race is Race.SUPPORT_ITEM
    assert decoded.hp == 1200


def test_a_support_item_sub_type_seven_carries_power_points() -> None:
    request = CardRequest(st=Constraint.exactly(300), race=Race.SUPPORT_ITEM, job=7)

    decoded = decode(first(request))

    assert decoded.pp == 3


def test_a_support_item_sub_type_eight_carries_magic_points() -> None:
    request = CardRequest(df=Constraint.exactly(500), race=Race.SUPPORT_ITEM, job=8)

    decoded = decode(first(request))

    assert decoded.mp == 5


def test_stat_digit_options_below_the_threshold_are_the_values_themselves() -> None:
    assert stat_digit_options(Race.MECHANICAL, hp_units=40, st_units=12, df_units=7) == [(12, 7)]


def test_stat_digit_options_for_the_aquatic_race_subtract_the_bonus() -> None:
    assert stat_digit_options(Race.AQUATIC, hp_units=209, st_units=110, df_units=110) == [(10, 10)]


def test_stat_digit_options_offer_the_dual_bonus_route_when_it_applies() -> None:
    options = stat_digit_options(Race.MECHANICAL, hp_units=209, st_units=213, df_units=110)

    assert options == [(13, 10)]
    assert options[0][0] in DUAL_BONUS_VALUES


def test_stat_digit_options_are_empty_when_the_value_is_unreachable() -> None:
    assert stat_digit_options(Race.MECHANICAL, hp_units=209, st_units=6, df_units=0) == []
