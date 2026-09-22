"""Tests for the refusal to emit a code whose behaviour is unresolved."""

import pytest

from barcode_battler.generator.front_solver import assemble
from barcode_battler.generator.quarantine import quarantines_digits, takes_quarantined_branch
from barcode_battler.models.race import Race


@pytest.mark.parametrize("code", ["2099300045000", "2091093145004"])
def test_a_code_reaching_an_overflow_branch_is_quarantined(code: str) -> None:
    assert takes_quarantined_branch(code)


@pytest.mark.parametrize("code", ["2091000045007", "2091013145008", "0401207237501"])
def test_an_ordinary_code_is_not_quarantined(code: str) -> None:
    assert not takes_quarantined_branch(code)


def test_a_back_read_code_is_never_quarantined() -> None:
    assert not takes_quarantined_branch("7310707558739")


def test_a_race_that_takes_no_bonus_is_never_quarantined() -> None:
    assert not takes_quarantined_branch("2099399945004")


@pytest.mark.parametrize(
    ("race", "st_digits", "df_digits", "expected"),
    [
        (Race.MECHANICAL, 93, 0, True),
        (Race.MECHANICAL, 10, 0, False),
        (Race.ANIMAL, 0, 93, True),
        (Race.ANIMAL, 0, 13, False),
        (Race.AQUATIC, 93, 93, False),
        (Race.HUMAN, 93, 93, False),
    ],
)
def test_the_digit_form_matches_the_code_form(
    race: Race, st_digits: int, df_digits: int, expected: bool
) -> None:
    hp_units = 209
    code = assemble(
        hp_units=hp_units,
        st_digits=st_digits,
        df_digits=df_digits,
        race=race,
        job=0,
        speed=5,
        special=0,
    )

    assert (
        quarantines_digits(race, hp_units=hp_units, st_digits=st_digits, df_digits=df_digits)
        is expected
    )
    assert takes_quarantined_branch(code) is expected


def test_the_digit_form_ignores_hit_points_below_the_threshold() -> None:
    assert not quarantines_digits(Race.MECHANICAL, hp_units=40, st_digits=93, df_digits=0)
