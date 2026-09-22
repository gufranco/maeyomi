"""The back reading, which rotates digits instead of slicing them.

Source: `post_reading` in `src/BarcodeRead.as` of
finalfighter/BarcodeBattler2-Simulator (MIT). The 8-digit layout is the 13-digit
layout with every stat index moved down by five. Only the aligned read is
implemented; the shifted variant used by the C1 and C2 game modes is recorded in
`uncertainties.py` as out of scope.
"""

from dataclasses import dataclass
from typing import Final

from barcode_battler.decoder.check_digit import EAN_8_LENGTH
from barcode_battler.models.character import DISPLAY_SCALE, BarcodeBattlerCharacter
from barcode_battler.models.race import Race
from barcode_battler.models.read_type import ReadType
from barcode_battler.models.special_ability import SpecialAbility

FIGHTER_HP_DIVISOR: Final = 2
SUPPORT_HP_DIVISOR: Final = 8
ST_TENS_OFFSET: Final = 7
ST_TENS_WRAP_ABOVE: Final = 11
ST_UNITS_OFFSET: Final = 5
DF_OFFSET: Final = 7

STARTING_POWER_POINTS: Final = 5
STARTING_MAGIC_POINTS: Final = 10
LOWEST_MAGIC_JOB: Final = 6
EIGHT_DIGIT_JOB: Final = 4

SPECIAL_LOW_SELECTOR_MAX: Final = 3
SPECIAL_HIGH_SELECTOR_MIN: Final = 8
SPECIAL_MIDDLE_OFFSET: Final = 10
SPECIAL_HIGH_OFFSET: Final = 20

_WEAPON_PREFIX_BY_MARKER: Final = {3: 3, 4: 3, 5: 1, 6: 1, 7: 1, 8: 1}
_WEAPON_DEFAULT_PREFIX: Final = 2
_ARMOUR_BARE_MARKERS: Final = frozenset({3, 4, 5, 6})
_ARMOUR_TENS_MARKERS: Final = frozenset({1, 2})
_ARMOUR_TENS_PREFIX: Final = 2
_ARMOUR_DEFAULT_PREFIX: Final = 1


@dataclass(frozen=True, slots=True)
class _Layout:
    """Digit indices for one supported barcode length."""

    race: int
    hp_high: int
    hp_mid: int
    hp_low: int
    df_low: int
    job: int | None
    speed: int
    special_selector: int
    special_digit: int


_LAYOUTS: Final[dict[int, _Layout]] = {
    13: _Layout(
        race=12,
        hp_high=11,
        hp_mid=10,
        hp_low=9,
        df_low=8,
        job=5,
        speed=10,
        special_selector=8,
        special_digit=10,
    ),
    EAN_8_LENGTH: _Layout(
        race=7,
        hp_high=6,
        hp_mid=5,
        hp_low=4,
        df_low=3,
        job=None,
        speed=5,
        special_selector=3,
        special_digit=5,
    ),
}


def read_back(code: str) -> BarcodeBattlerCharacter:
    """Decode an already validated 8 or 13 digit code as a back read."""
    layout = _LAYOUTS[len(code)]
    digits = [int(character) for character in code]
    race = Race(digits[layout.race])
    special = _read_special(digits, layout)
    if race.is_fighter:
        return _read_fighter(code, digits, layout, race, special)
    return _read_item(code, digits, layout, race, special)


def _read_special(digits: list[int], layout: _Layout) -> SpecialAbility:
    """Prefix the ability digit according to the selector digit's band."""
    selector = digits[layout.special_selector]
    value = digits[layout.special_digit]
    if selector <= SPECIAL_LOW_SELECTOR_MAX:
        return SpecialAbility.from_code(value)
    if selector >= SPECIAL_HIGH_SELECTOR_MIN:
        return SpecialAbility.from_code(SPECIAL_HIGH_OFFSET + value)
    return SpecialAbility.from_code(SPECIAL_MIDDLE_OFFSET + value)


def _read_fighter(
    code: str,
    digits: list[int],
    layout: _Layout,
    race: Race,
    special: SpecialAbility,
) -> BarcodeBattlerCharacter:
    """Decode a character from the rotated digits."""
    hp = _compose(
        digits[layout.hp_high] // FIGHTER_HP_DIVISOR, digits[layout.hp_mid], digits[layout.hp_low]
    )
    tens = digits[layout.hp_mid] + ST_TENS_OFFSET
    if tens > ST_TENS_WRAP_ABOVE:
        tens -= 10
    st = tens * 10 + (digits[layout.hp_low] + ST_UNITS_OFFSET) % 10
    df = ((digits[layout.hp_low] + DF_OFFSET) % 10) * 10 + (digits[layout.df_low] + DF_OFFSET) % 10
    job = EIGHT_DIGIT_JOB if layout.job is None else digits[layout.job]
    return _build(
        code,
        race=race,
        job=job,
        hp=hp,
        st=st,
        df=df,
        special=special,
        speed=digits[layout.speed],
        pp=STARTING_POWER_POINTS,
        mp=STARTING_MAGIC_POINTS if job >= LOWEST_MAGIC_JOB else 0,
    )


def _read_item(
    code: str,
    digits: list[int],
    layout: _Layout,
    race: Race,
    special: SpecialAbility,
) -> BarcodeBattlerCharacter:
    """Decode a weapon, a piece of armour, or a support item."""
    if race.is_weapon:
        prefix = _WEAPON_PREFIX_BY_MARKER.get(digits[layout.hp_mid], _WEAPON_DEFAULT_PREFIX)
        st = prefix * 10 + (digits[layout.hp_low] + ST_UNITS_OFFSET) % 10
        return _build(code, race=race, st=st, special=special)
    if race.is_armour:
        return _build(code, race=race, df=_armour_value(digits, layout), special=special)
    hp = _compose(
        digits[layout.hp_high] // SUPPORT_HP_DIVISOR, digits[layout.hp_mid], digits[layout.hp_low]
    )
    return _build(code, race=race, hp=hp, special=special)


def _armour_value(digits: list[int], layout: _Layout) -> int:
    """Return the defence modifier, whose tens digit depends on a marker digit."""
    marker = digits[layout.hp_low]
    units = (digits[layout.df_low] + DF_OFFSET) % 10
    if marker in _ARMOUR_BARE_MARKERS:
        return units
    prefix = _ARMOUR_TENS_PREFIX if marker in _ARMOUR_TENS_MARKERS else _ARMOUR_DEFAULT_PREFIX
    return prefix * 10 + units


def _compose(high: int, mid: int, low: int) -> int:
    """Join three digit values into one three-digit number."""
    return high * 100 + mid * 10 + low


def _build(
    code: str,
    *,
    race: Race,
    special: SpecialAbility,
    job: int = 0,
    hp: int = 0,
    st: int = 0,
    df: int = 0,
    speed: int | None = None,
    pp: int = 0,
    mp: int = 0,
) -> BarcodeBattlerCharacter:
    """Assemble the model, converting the device's internal units to display values."""
    return BarcodeBattlerCharacter(
        barcode=code,
        read_type=ReadType.BACK,
        race=race,
        job=job,
        hp=hp * DISPLAY_SCALE,
        st=st * DISPLAY_SCALE,
        df=df * DISPLAY_SCALE,
        special=special,
        speed=speed,
        pp=pp,
        mp=mp,
    )
