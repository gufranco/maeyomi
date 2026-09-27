"""Tests for the refusal to emit a code whose behaviour is unresolved."""

import pytest

from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.generator.front_solver import assemble
from maeyomi.generator.quarantine import (
    WRAPPING_BATTLE_VALUES,
    quarantines_digits,
    takes_quarantined_branch,
)
from maeyomi.models.race import Race


def complete(body: str) -> str:
    return body + str(expected_check_digit(body))


def fighter(race: Race, st_digits: int, df_digits: int, hp_units: int = 209) -> str:
    return assemble(
        hp_units=hp_units,
        st_digits=st_digits,
        df_digits=df_digits,
        race=race,
        job=0,
        speed=5,
        special=0,
    )


def test_only_the_three_values_past_one_byte_wrap() -> None:
    assert frozenset({62, 78, 94}) == WRAPPING_BATTLE_VALUES


@pytest.mark.parametrize(
    ("race", "st_digits", "df_digits", "expected"),
    [
        (Race.MECHANICAL, 62, 0, True),
        (Race.MECHANICAL, 46, 0, False),
        (Race.MECHANICAL, 45, 0, False),
        (Race.MECHANICAL, 10, 0, False),
        (Race.ANIMAL, 0, 94, True),
        (Race.ANIMAL, 0, 45, True),
        (Race.ANIMAL, 0, 46, False),
        (Race.AQUATIC, 94, 94, False),
        (Race.HUMAN, 94, 94, False),
    ],
)
def test_the_digit_form_matches_the_code_form(
    race: Race, st_digits: int, df_digits: int, expected: bool
) -> None:
    code = fighter(race, st_digits, df_digits)

    assert quarantines_digits(race, hp_units=209, st_digits=st_digits, df_digits=df_digits) is (
        expected
    )
    assert takes_quarantined_branch(code) is expected


def test_the_digit_form_ignores_hit_points_below_the_threshold() -> None:
    assert not quarantines_digits(Race.MECHANICAL, hp_units=40, st_digits=62, df_digits=0)


def test_a_back_read_code_outside_the_disputed_band_is_never_quarantined() -> None:
    assert not takes_quarantined_branch("7310707558739")


@pytest.mark.parametrize(
    "body",
    [
        "060000090000",
        "000055050000",
        "000500570000",
    ],
    ids=["hp-item-above-bound", "weapon-with-high-defence", "armour-with-high-strength"],
)
def test_an_item_the_two_read_rules_classify_differently_is_quarantined(body: str) -> None:
    assert takes_quarantined_branch(complete(body))


@pytest.mark.parametrize(
    "body",
    ["000050550000", "000050570000", "000000090000", "000101000000"],
    ids=["weapon-in-bounds", "armour-in-bounds", "hp-item-in-bounds", "fighter"],
)
def test_an_item_both_rules_read_the_same_way_is_not_quarantined(body: str) -> None:
    assert not takes_quarantined_branch(complete(body))


def test_an_eight_digit_code_is_outside_the_disputed_band() -> None:
    assert not takes_quarantined_branch("05017447")
