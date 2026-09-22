"""Decide whether the device reads a barcode from the front or from the back.

Source: `prepost_check` in `src/BarcodeRead.as` of
finalfighter/BarcodeBattler2-Simulator (MIT), and the prose on
barcodebattler.net/page02.htm, which states the marker rule and the stat-bound
fallback.
"""

from typing import Final

from maeyomi.decoder.check_digit import EAN_8_LENGTH
from maeyomi.models.read_type import ReadType

LOW_LEADING_DIGITS: Final = (0, 1)
FIGHTER_RACE_INDEX: Final = 7
HIGHEST_FIGHTER_RACE: Final = 4

MARKER_PREFIX_INDEX: Final = 2
MARKER_PREFIX_VALUE: Final = 9
MARKER_SUFFIX_INDEX: Final = 9
MARKER_SUFFIX_VALUE: Final = 5

FALLBACK_MAX_HP_UNITS: Final = 50
FALLBACK_MAX_ST_UNITS: Final = 19
FALLBACK_MAX_DF_UNITS: Final = 19

_HP_SLICE: Final = slice(0, 3)
_ST_SLICE: Final = slice(3, 5)
_DF_SLICE: Final = slice(5, 7)


def classify_read_type(code: str) -> ReadType:
    """Return the reading mode the device selects for an already validated code."""
    if len(code) == EAN_8_LENGTH:
        return ReadType.BACK
    if int(code[0]) in LOW_LEADING_DIGITS:
        return _classify_low_leading(code)
    return _classify_high_leading(code)


def _classify_low_leading(code: str) -> ReadType:
    """Classify a code whose leading digit is 0 or 1."""
    if int(code[FIGHTER_RACE_INDEX]) <= HIGHEST_FIGHTER_RACE:
        return ReadType.FRONT
    return _classify_by_stat_bounds(code)


def _classify_high_leading(code: str) -> ReadType:
    """Classify a code whose leading digit is 2 to 9 using the published marker."""
    has_marker = (
        int(code[MARKER_PREFIX_INDEX]) == MARKER_PREFIX_VALUE
        and int(code[MARKER_SUFFIX_INDEX]) == MARKER_SUFFIX_VALUE
    )
    return ReadType.FRONT if has_marker else ReadType.BACK


def _classify_by_stat_bounds(code: str) -> ReadType:
    """Front read anyway when the front reading would stay inside the published bounds."""
    within = (
        int(code[_HP_SLICE]) <= FALLBACK_MAX_HP_UNITS
        and int(code[_ST_SLICE]) <= FALLBACK_MAX_ST_UNITS
        and int(code[_DF_SLICE]) <= FALLBACK_MAX_DF_UNITS
    )
    return ReadType.FRONT if within else ReadType.BACK
