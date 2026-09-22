"""Refuse to emit a barcode whose decoded value rests on an unresolved branch.

The decoder reproduces the reference simulator's two suspect arithmetic
branches faithfully, because that is the only reading anything can be checked
against. Nothing is checked against them, so a printed card must never depend
on one. See `race_one_overflow_target` and `st_overflow_threshold` in
`uncertainties.py`.
"""

from maeyomi.decoder.front_read import (
    DF_OVERFLOW_THRESHOLD,
    DF_SLICE,
    DUAL_BONUS_VALUES,
    HIGH_HP_BONUS_UNITS,
    HIGH_HP_THRESHOLD_UNITS,
    HP_SLICE,
    RACE_INDEX,
    ST_OVERFLOW_THRESHOLD,
    ST_SLICE,
)
from maeyomi.decoder.read_type import classify_read_type
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType


def takes_quarantined_branch(code: str) -> bool:
    """Whether reading this code would pass through an unresolved overflow branch."""
    if classify_read_type(code) is not ReadType.FRONT:
        return False
    return quarantines_digits(
        Race(int(code[RACE_INDEX])),
        hp_units=int(code[HP_SLICE]),
        st_digits=int(code[ST_SLICE]),
        df_digits=int(code[DF_SLICE]),
    )


def quarantines_digits(race: Race, *, hp_units: int, st_digits: int, df_digits: int) -> bool:
    """The same test on digit values, for a caller that has not built a code yet.

    A search that scores many candidates uses this and assembles a barcode only
    for the one it keeps.
    """
    if hp_units < HIGH_HP_THRESHOLD_UNITS:
        return False
    if race is Race.MECHANICAL:
        return _bonused(st_digits) > ST_OVERFLOW_THRESHOLD
    if race is Race.ANIMAL:
        return _bonused(df_digits) > DF_OVERFLOW_THRESHOLD
    return False


def _bonused(digits: int) -> int:
    """The stat value after the bonus its own slice earns it."""
    dual = HIGH_HP_BONUS_UNITS if digits in DUAL_BONUS_VALUES else 0
    return digits + dual + HIGH_HP_BONUS_UNITS
