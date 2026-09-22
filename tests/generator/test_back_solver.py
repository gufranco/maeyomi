"""Tests for the back-read inverter."""

import itertools

import pytest

from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.decoder.decode import decode
from maeyomi.generator.back_solver import (
    TUNING_INDEX,
    BackReadCandidate,
    iter_back_candidates,
    reachable_back_stats,
)
from maeyomi.models.card_request import CardRequest
from maeyomi.models.constraint import Constraint
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType


def first(request: CardRequest) -> BackReadCandidate:
    return next(iter(itertools.islice(iter_back_candidates(request), 1)))


def test_a_back_read_candidate_classifies_as_a_back_read() -> None:
    request = CardRequest(race=Race.HUMAN)

    candidate = first(request)

    assert decode(candidate.barcode).read_type is ReadType.BACK


def test_the_race_is_honoured_even_though_it_sits_on_the_check_digit() -> None:
    for race in (race for race in Race if race.is_fighter):
        candidate = first(CardRequest(race=race))

        assert decode(candidate.barcode).race is race


def test_a_requested_stat_is_reached_when_it_is_reachable() -> None:
    reachable = reachable_back_stats(Race.HUMAN)
    hp, st, df = next(iter(sorted(reachable)))

    request = CardRequest(
        hp=Constraint.exactly(hp),
        st=Constraint.exactly(st),
        df=Constraint.exactly(df),
        race=Race.HUMAN,
    )
    candidate = first(request)
    decoded = decode(candidate.barcode)

    assert (decoded.hp, decoded.st, decoded.df) == (hp, st, df)


def test_an_unreachable_stat_combination_yields_nothing() -> None:
    request = CardRequest(
        hp=Constraint.exactly(49900),
        st=Constraint.exactly(11900),
        df=Constraint.exactly(9900),
        race=Race.HUMAN,
    )

    assert list(itertools.islice(iter_back_candidates(request), 1)) == []


def test_the_job_digit_is_honoured() -> None:
    candidate = first(CardRequest(race=Race.HUMAN, job=8))

    assert decode(candidate.barcode).job == 8


def test_a_candidate_reports_the_alternatives_it_did_not_pick() -> None:
    request = CardRequest(race=Race.HUMAN)

    candidate = first(request)

    assert candidate.alternatives >= 0


def test_the_reachable_set_respects_the_published_back_read_ceilings() -> None:
    reachable = reachable_back_stats(Race.HUMAN)

    assert max(hp for hp, _, _ in reachable) <= 49900
    assert max(st for _, st, _ in reachable) <= 11900
    assert max(df for _, _, df in reachable) <= 9900


def test_the_reachable_set_is_half_the_digit_combinations_because_hp_is_halved() -> None:
    reachable = reachable_back_stats(Race.HUMAN)

    assert len(reachable) == 5_000


def test_two_digit_values_collapse_onto_one_hit_point_hundreds_digit() -> None:
    reachable = reachable_back_stats(Race.HUMAN)

    hundreds = {hp // 10_000 for hp, _, _ in reachable}

    assert hundreds == {0, 1, 2, 3, 4}


@pytest.mark.parametrize("special", [0, 15, 29])
def test_a_back_read_special_ability_within_range_is_honoured(special: int) -> None:
    candidate = first(CardRequest(race=Race.HUMAN, special=special))

    assert decode(candidate.barcode).special.code == special


def test_a_special_ability_above_the_back_read_ceiling_yields_nothing() -> None:
    request = CardRequest(race=Race.HUMAN, special=50)

    assert list(itertools.islice(iter_back_candidates(request), 1)) == []


def test_an_item_race_is_not_supported_by_this_inverter() -> None:
    request = CardRequest(race=Race.WEAPON)

    assert list(itertools.islice(iter_back_candidates(request), 1)) == []


def test_every_candidate_decodes_to_the_request() -> None:
    request = CardRequest(race=Race.BIRD, job=3, special=7)

    for candidate in itertools.islice(iter_back_candidates(request), 25):
        decoded = decode(candidate.barcode)
        assert decoded.read_type is ReadType.BACK
        assert decoded.race is Race.BIRD
        assert decoded.job == 3
        assert decoded.special.code == 7


def test_the_tuning_digit_reaches_every_check_digit() -> None:
    body = list("209000000000")
    reachable: set[int] = set()
    for value in range(10):
        body[TUNING_INDEX] = str(value)
        reachable.add(expected_check_digit("".join(body)))

    assert reachable == set(range(10))
