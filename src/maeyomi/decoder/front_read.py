"""The front reading, where fixed digit slices map directly onto attributes.

Source: `pre_reading` in `src/BarcodeRead.as` of
finalfighter/BarcodeBattler2-Simulator (MIT), with three deliberate divergences,
each recorded in `uncertainties.py`:

- speed is read from index 9 rather than index 11;
- the high hit point bonus follows the two sources that tested printed codes on
  a device, barcodebattler.net/page21.htm and the note.com analysis by
  sakigomyway, rather than the simulator's single bonus set;
- job 6 is a warrior and starts without magic points, as page01 and two of the
  simulator's three job tests have it.

Above the bonus threshold a device fights with a strength or defence it never
displays. Both values are kept: the displayed one is what the card prints, and
the battle one is what a fight uses.
"""

from dataclasses import dataclass
from typing import Final

from maeyomi.models.character import (
    DISPLAY_SCALE,
    HIGHEST_WARRIOR_JOB,
    BarcodeBattlerCharacter,
)
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType
from maeyomi.models.special_ability import SpecialAbility

HP_SLICE: Final = slice(0, 3)
ST_SLICE: Final = slice(3, 5)
DF_SLICE: Final = slice(5, 7)
RACE_INDEX: Final = 7
JOB_INDEX: Final = 8
SPEED_INDEX: Final = 9
SPECIAL_SLICE: Final = slice(10, 12)

HIGH_HP_THRESHOLD_UNITS: Final = 200
HIGH_HP_BONUS_UNITS: Final = 100
PARTNER_BONUS_VALUES: Final = frozenset({13, 29, 45, 61, 77, 93})
BATTLE_BONUS_VALUES: Final = frozenset({14, 30, 46, 62, 78, 94})
BATTLE_STAT_WRAP_UNITS: Final = 256

STARTING_POWER_POINTS: Final = 5
STARTING_MAGIC_POINTS: Final = 10

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
    stats = adjusted_stats(
        race, hp_units=hp, st_digits=int(code[ST_SLICE]), df_digits=int(code[DF_SLICE])
    )
    job = int(code[JOB_INDEX])
    return _build(
        code,
        race=race,
        job=job,
        hp=hp,
        st=stats.st,
        df=stats.df,
        battle_st=stats.battle_st,
        battle_df=stats.battle_df,
        special=special,
        speed=int(code[SPEED_INDEX]),
        pp=STARTING_POWER_POINTS,
        mp=STARTING_MAGIC_POINTS if job > HIGHEST_WARRIOR_JOB else 0,
    )


@dataclass(frozen=True, slots=True)
class AdjustedStats:
    """Strength and defence in device units, as displayed and as fought with."""

    st: int
    df: int
    battle_st: int
    battle_df: int


def adjusted_stats(race: Race, *, hp_units: int, st_digits: int, df_digits: int) -> AdjustedStats:
    """Return ST and DF in device units after the bonus a high HP triggers.

    This is the forward direction of `stat_digit_options` in the generator. The
    two are asserted to agree in the generator's tests.
    """
    if hp_units < HIGH_HP_THRESHOLD_UNITS or race not in _HIGH_HP_RACES:
        return AdjustedStats(st_digits, df_digits, st_digits, df_digits)
    if race is Race.AQUATIC:
        st = st_digits + HIGH_HP_BONUS_UNITS
        df = df_digits + HIGH_HP_BONUS_UNITS
        return AdjustedStats(st, df, st, df)
    if race is Race.MECHANICAL:
        lead, partner, battle = _lead_bonus(st_digits, df_digits, partner_set_applies=True)
        return AdjustedStats(lead, partner, battle, partner)
    lead, partner, battle = _lead_bonus(df_digits, st_digits, partner_set_applies=False)
    return AdjustedStats(partner, lead, partner, battle)


def _lead_bonus(lead: int, partner: int, *, partner_set_applies: bool) -> tuple[int, int, int]:
    """The lead stat, its partner, and the lead stat a fight uses.

    The lead stat always gains the bonus. Its digits decide whether the partner
    gains one too, and whether the fight uses a further hidden bonus that wraps
    at one byte.
    """
    shown = lead + HIGH_HP_BONUS_UNITS
    partner_gains = lead in BATTLE_BONUS_VALUES or (
        partner_set_applies and lead in PARTNER_BONUS_VALUES
    )
    shown_partner = partner + (HIGH_HP_BONUS_UNITS if partner_gains else 0)
    battle = shown + (HIGH_HP_BONUS_UNITS if lead in BATTLE_BONUS_VALUES else 0)
    return shown, shown_partner, battle % BATTLE_STAT_WRAP_UNITS


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
    battle_st: int | None = None,
    battle_df: int | None = None,
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
        battle_st=_hidden(battle_st, st),
        battle_df=_hidden(battle_df, df),
        special=special,
        speed=speed,
        pp=pp,
        mp=mp,
        sign_is_volatile=sign_is_volatile,
    )


def _hidden(battle: int | None, shown: int) -> int | None:
    """The battle value in display units, or None when it equals the shown one."""
    if battle is None or battle == shown:
        return None
    return battle * DISPLAY_SCALE
