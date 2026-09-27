"""Refuse to emit a barcode whose decoded value rests on an unresolved branch.

The decoder picks one reading wherever the sources disagree, because a reading
is needed to decode anything at all. A printed card must never depend on that
choice. Three disagreements are fenced off here, each recorded in
`uncertainties.py`:

- `battle_stat_wrap`: a hidden battle bonus that passes one byte, where the
  sources subtract 256 or 255;
- `animal_partner_set`: an animal whose defence digits are in the set that only
  raises a mechanical fighter's partner stat;
- `low_leading_item_read_type`: a code starting with 0 or 1 whose item digit is
  5 to 9, where the tested flowchart and the simulator choose different reads.
"""

from typing import Final

from maeyomi.decoder.check_digit import EAN_13_LENGTH
from maeyomi.decoder.front_read import (
    BATTLE_BONUS_VALUES,
    BATTLE_STAT_WRAP_UNITS,
    DF_SLICE,
    HIGH_HP_BONUS_UNITS,
    HIGH_HP_THRESHOLD_UNITS,
    HP_SLICE,
    PARTNER_BONUS_VALUES,
    RACE_INDEX,
    ST_SLICE,
)
from maeyomi.decoder.read_type import LOW_LEADING_DIGITS, classify_read_type
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType

WRAPPING_BATTLE_VALUES: Final = frozenset(
    value
    for value in BATTLE_BONUS_VALUES
    if value + 2 * HIGH_HP_BONUS_UNITS >= BATTLE_STAT_WRAP_UNITS
)
TESTED_FLOWCHART_ALWAYS_FRONT: Final = 9
TESTED_FLOWCHART_WEAPON_DIGITS: Final = (5, 6)
TESTED_FLOWCHART_MAX_UNITS: Final = 19
HIGHEST_FIGHTER_DIGIT: Final = 4


def takes_quarantined_branch(code: str) -> bool:
    """Whether reading this code would pass through an unresolved branch."""
    if _read_type_sources_disagree(code):
        return True
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
        return st_digits in WRAPPING_BATTLE_VALUES
    if race is Race.ANIMAL:
        return df_digits in WRAPPING_BATTLE_VALUES or df_digits in PARTNER_BONUS_VALUES
    return False


def _read_type_sources_disagree(code: str) -> bool:
    """Whether the tested flowchart and the simulator choose different reads."""
    if len(code) != EAN_13_LENGTH or int(code[0]) not in LOW_LEADING_DIGITS:
        return False
    item_digit = int(code[RACE_INDEX])
    if item_digit <= HIGHEST_FIGHTER_DIGIT:
        return False
    return _tested_flowchart_reads_front(code, item_digit) != (
        classify_read_type(code) is ReadType.FRONT
    )


def _tested_flowchart_reads_front(code: str, item_digit: int) -> bool:
    """The read the note.com flowchart, checked on a device, chooses."""
    if item_digit == TESTED_FLOWCHART_ALWAYS_FRONT:
        return True
    if item_digit in TESTED_FLOWCHART_WEAPON_DIGITS:
        return int(code[ST_SLICE]) <= TESTED_FLOWCHART_MAX_UNITS
    return int(code[DF_SLICE]) <= TESTED_FLOWCHART_MAX_UNITS
