"""The front reading, where fixed digit slices map directly onto attributes.

Source: `pre_reading` in `src/BarcodeRead.as` of
finalfighter/BarcodeBattler2-Simulator (MIT), with two deliberate divergences:
speed is read from index 9 rather than index 11, and the race 1 overflow
correction subtracts from defence rather than from strength, because the
simulator's line produces a negative defence no device can hold. See the
`front_read_speed_digit` and `race_one_overflow_target` entries in
`uncertainties.py`.
"""

from typing import Final

from barcode_battler.models.character import DISPLAY_SCALE, BarcodeBattlerCharacter
from barcode_battler.models.race import Race
from barcode_battler.models.read_type import ReadType
from barcode_battler.models.special_ability import SpecialAbility

HP_SLICE: Final = slice(0, 3)
ST_SLICE: Final = slice(3, 5)
DF_SLICE: Final = slice(5, 7)
RACE_INDEX: Final = 7
JOB_INDEX: Final = 8
SPEED_INDEX: Final = 9
SPECIAL_SLICE: Final = slice(10, 12)

HIGH_HP_THRESHOLD_UNITS: Final = 200
HIGH_HP_BONUS_UNITS: Final = 100
DUAL_BONUS_VALUES: Final = frozenset({13, 29, 45, 61, 77, 93})
ST_OVERFLOW_THRESHOLD: Final = 256
DF_OVERFLOW_THRESHOLD: Final = 256
OVERFLOW_SUBTRAHEND: Final = 255

STARTING_POWER_POINTS: Final = 5
STARTING_MAGIC_POINTS: Final = 10
LOWEST_MAGIC_JOB: Final = 6

SUPPORT_HIGHEST_HP_SUB_TYPE: Final = 4
SUPPORT_INFORMATION_SUB_TYPES: Final = (5, 6)
SUPPORT_POWER_POINT_SUB_TYPE: Final = 7

VOLATILE_HP_ABILITY: Final = 30
VOLATILE_ST_ABILITY: Final = 31
VOLATILE_DF_ABILITY: Final = 32


def read_front(code: str) -> BarcodeBattlerCharacter:
    """Decode an already validated 13-digit code as a front read."""
    race = Race(int(code[RACE_INDEX]))
    special = SpecialAbility.from_code(int(code[SPECIAL_SLICE]))
    if race.is_fighter:
        return _read_fighter(code, race, special)
    return _read_item(code, race, special)


def _read_fighter(code: str, race: Race, special: SpecialAbility) -> BarcodeBattlerCharacter:
    """Decode a character, applying the high-HP adjustment its race calls for."""
    hp = int(code[HP_SLICE])
    st, df = adjusted_stats(
        race, hp_units=hp, st_digits=int(code[ST_SLICE]), df_digits=int(code[DF_SLICE])
    )
    job = int(code[JOB_INDEX])
    return _build(
        code,
        race=race,
        job=job,
        hp=hp,
        st=st,
        df=df,
        special=special,
        speed=int(code[SPEED_INDEX]),
        pp=STARTING_POWER_POINTS,
        mp=STARTING_MAGIC_POINTS if job >= LOWEST_MAGIC_JOB else 0,
    )


def adjusted_stats(race: Race, *, hp_units: int, st_digits: int, df_digits: int) -> tuple[int, int]:
    """Return ST and DF in device units after the bonus a high HP triggers.

    This is the forward direction of `stat_digit_options` in the generator. The
    two are asserted to agree in the generator's tests.
    """
    st = st_digits
    df = df_digits
    if hp_units < HIGH_HP_THRESHOLD_UNITS or race not in _HIGH_HP_RACES:
        return st, df
    if race is Race.AQUATIC:
        return st + HIGH_HP_BONUS_UNITS, df + HIGH_HP_BONUS_UNITS
    partner = st_digits if race is Race.MECHANICAL else df_digits
    if partner in DUAL_BONUS_VALUES:
        st += HIGH_HP_BONUS_UNITS
        df += HIGH_HP_BONUS_UNITS
    if race is Race.MECHANICAL:
        st += HIGH_HP_BONUS_UNITS
        if st > ST_OVERFLOW_THRESHOLD:
            st -= OVERFLOW_SUBTRAHEND
        return st, df
    df += HIGH_HP_BONUS_UNITS
    if df > DF_OVERFLOW_THRESHOLD:
        df -= OVERFLOW_SUBTRAHEND
    return st, df


_HIGH_HP_RACES: Final = (Race.MECHANICAL, Race.ANIMAL, Race.AQUATIC)


def _read_item(code: str, race: Race, special: SpecialAbility) -> BarcodeBattlerCharacter:
    """Decode a weapon, a piece of armour, or a support item."""
    if race.is_weapon:
        return _build(
            code,
            race=race,
            st=int(code[ST_SLICE]),
            special=special,
            sign_is_volatile=special.code == VOLATILE_ST_ABILITY,
        )
    if race.is_armour:
        return _build(
            code,
            race=race,
            df=int(code[DF_SLICE]),
            special=special,
            sign_is_volatile=special.code == VOLATILE_DF_ABILITY,
        )
    return _read_support_item(code, race, special)


def _read_support_item(code: str, race: Race, special: SpecialAbility) -> BarcodeBattlerCharacter:
    """Decode a support item, whose sub-type lives in the job digit."""
    sub_type = int(code[JOB_INDEX])
    fields: dict[str, int] = {}
    volatile = False
    if sub_type <= SUPPORT_HIGHEST_HP_SUB_TYPE:
        fields["hp"] = int(code[HP_SLICE])
        volatile = special.code == VOLATILE_HP_ABILITY
    elif sub_type in SUPPORT_INFORMATION_SUB_TYPES:
        fields = {}
    elif sub_type == SUPPORT_POWER_POINT_SUB_TYPE:
        fields["pp"] = int(code[ST_SLICE])
    else:
        fields["mp"] = int(code[DF_SLICE])
    return _build(
        code, race=race, job=sub_type, special=special, sign_is_volatile=volatile, **fields
    )


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
    sign_is_volatile: bool = False,
) -> BarcodeBattlerCharacter:
    """Assemble the model, converting the device's internal units to display values."""
    return BarcodeBattlerCharacter(
        barcode=code,
        read_type=ReadType.FRONT,
        race=race,
        job=job,
        hp=hp * DISPLAY_SCALE,
        st=st * DISPLAY_SCALE,
        df=df * DISPLAY_SCALE,
        special=special,
        speed=speed,
        pp=pp,
        mp=mp,
        sign_is_volatile=sign_is_volatile,
    )
