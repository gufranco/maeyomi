"""Tests for the high-HP bonus, pinned to what devices were reported to show."""

import pytest

from maeyomi.decoder.decode import decode
from maeyomi.decoder.front_read import (
    BATTLE_BONUS_VALUES,
    PARTNER_BONUS_VALUES,
    AdjustedStats,
    adjusted_stats,
)
from maeyomi.decoder.uncertainties import UNCERTAINTIES
from maeyomi.generator.front_solver import assemble
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType

PAGE_TWENTY_ONE_CARD = "4994699095453"
HIGH_HP_UNITS = 209


def fighter(race: Race, st_digits: int, df_digits: int) -> str:
    return assemble(
        hp_units=HIGH_HP_UNITS,
        st_digits=st_digits,
        df_digits=df_digits,
        race=race,
        job=0,
        speed=5,
        special=0,
    )


def test_the_card_page_twenty_one_scanned_reads_as_the_device_showed_it() -> None:
    character = decode(PAGE_TWENTY_ONE_CARD)

    assert character.read_type is ReadType.FRONT
    assert (character.hp, character.st, character.df) == (49900, 14600, 19900)
    assert (character.battle_st, character.battle_df) == (24600, None)


def test_a_mechanical_fighter_gains_strength_alone_outside_both_sets() -> None:
    character = decode(fighter(Race.MECHANICAL, 10, 50))

    assert (character.st, character.df) == (11000, 5000)
    assert (character.battle_st, character.battle_df) == (None, None)


@pytest.mark.parametrize("st_digits", sorted(PARTNER_BONUS_VALUES))
def test_the_partner_set_raises_a_mechanical_fighters_defence_and_nothing_hidden(
    st_digits: int,
) -> None:
    character = decode(fighter(Race.MECHANICAL, st_digits, 50))

    assert (character.st, character.df) == ((st_digits + 100) * 100, 15000)
    assert character.battle_st is None


@pytest.mark.parametrize(
    ("st_digits", "battle_st"),
    [(14, 21400), (30, 23000), (46, 24600), (62, 600), (78, 2200), (94, 3800)],
)
def test_the_battle_set_matches_the_published_table(st_digits: int, battle_st: int) -> None:
    character = decode(fighter(Race.MECHANICAL, st_digits, 50))

    assert character.st == (st_digits + 100) * 100
    assert character.df == 15000
    assert character.battle_st == battle_st


@pytest.mark.parametrize(
    ("df_digits", "battle_df"),
    [(14, 21400), (30, 23000), (46, 24600), (62, 600), (78, 2200), (94, 3800)],
)
def test_an_animal_mirrors_the_battle_set_on_defence(df_digits: int, battle_df: int) -> None:
    character = decode(fighter(Race.ANIMAL, 50, df_digits))

    assert character.st == 15000
    assert character.df == (df_digits + 100) * 100
    assert character.battle_df == battle_df


def test_an_animal_ignores_the_partner_set() -> None:
    character = decode(fighter(Race.ANIMAL, 50, 45))

    assert (character.st, character.df) == (5000, 14500)
    assert (character.battle_st, character.battle_df) == (None, None)


def test_an_aquatic_fighter_gains_both_stats_and_nothing_hidden() -> None:
    assert adjusted_stats(Race.AQUATIC, hp_units=HIGH_HP_UNITS, st_digits=46, df_digits=46) == (
        AdjustedStats(146, 146, 146, 146)
    )


@pytest.mark.parametrize("race", [Race.BIRD, Race.HUMAN])
def test_a_race_without_the_bonus_is_read_plainly(race: Race) -> None:
    assert adjusted_stats(race, hp_units=HIGH_HP_UNITS, st_digits=46, df_digits=46) == (
        AdjustedStats(46, 46, 46, 46)
    )


def test_below_the_threshold_no_race_gains_anything() -> None:
    assert adjusted_stats(Race.MECHANICAL, hp_units=199, st_digits=46, df_digits=99) == (
        AdjustedStats(46, 99, 46, 99)
    )


def test_the_two_sets_do_not_overlap() -> None:
    assert not PARTNER_BONUS_VALUES & BATTLE_BONUS_VALUES


@pytest.mark.parametrize("race", [race for race in Race if race.is_fighter])
def test_no_displayed_stat_passes_the_published_ceiling(race: Race) -> None:
    for st_digits in range(100):
        for df_digits in range(100):
            stats = adjusted_stats(
                race, hp_units=HIGH_HP_UNITS, st_digits=st_digits, df_digits=df_digits
            )
            assert max(stats.st, stats.df) <= 199, f"{race.name} {st_digits} {df_digits}"
            assert min(stats.battle_st, stats.battle_df) >= 0


def test_the_unresolved_branches_are_recorded_as_blocking_generation() -> None:
    blocking = {key for key, entry in UNCERTAINTIES.items() if entry.blocks_generation}

    assert blocking == {
        "battle_stat_wrap",
        "animal_partner_set",
        "low_leading_item_read_type",
        "bb1_back_read_flag",
    }
