"""Analytic inversion of the front reading.

The front reading maps fixed digit slices onto attributes, so inverting it is
placement rather than search. A fully specified fighter request determines every
digit, and the check digit is computed, so exactly one candidate is produced.

Three couplings make a naive placement wrong, and each is handled here:

1. The read-type predicate must still classify the finished code as a front
   read. A leading digit of 2 or more needs the published marker, which forces
   the third digit to 9 and the tenth digit to 5. Since the first three digits
   are the hit points of a fighter, a fighter above 19900 HP can only exist on a
   hundred ending in 900, and its speed is always 5.
2. Above 20000 HP the races 0, 1 and 2 have their strength and defence rewritten
   after they are read, so the digits are pre-compensated here.
3. Items read a different slice than characters, so the digits a character uses
   for hit points are free and are filled with a carrier value.

Candidates are proposals. Nothing here is trusted until `solve` has run it back
through the decoder.
"""

import itertools
from collections.abc import Iterator, Sequence
from typing import Final

from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.decoder.front_read import (
    BATTLE_BONUS_VALUES,
    HIGH_HP_BONUS_UNITS,
    PARTNER_BONUS_VALUES,
)
from maeyomi.decoder.front_read import HIGH_HP_THRESHOLD_UNITS as HIGH_HP
from maeyomi.decoder.read_type import (
    FALLBACK_MAX_DF_UNITS,
    FALLBACK_MAX_HP_UNITS,
    FALLBACK_MAX_ST_UNITS,
)
from maeyomi.generator.quarantine import quarantines_digits
from maeyomi.models.card_request import CardRequest
from maeyomi.models.character import DISPLAY_SCALE, HIGHEST_WARRIOR_JOB
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.constraint import Constraint
from maeyomi.models.race import Race

MAX_HP_DISPLAY: Final = 99900
MAX_STAT_DISPLAY: Final = 19900
"""The displayed strength and defence ceiling, as barcodebattler.net publishes it.

A request constrains what the device displays. A fight can use more, up to
`MAX_BATTLE_STAT`, but no display shows it and no request asks for it.
"""
MAX_BATTLE_STAT: Final = 24600
"""The highest strength or defence a fight uses without wrapping one byte.

A mechanical fighter above the high hit point threshold whose strength digits
are 46 displays 14600 and fights with 24600, per barcodebattler.net/page21.htm.
An animal reaches the same figure on defence. The decoder is asserted to reach
exactly this and nothing above it outside the quarantined wrap.
"""
MAX_DIGIT_PAIR: Final = 99
MARKER_HP_UNITS_ENDING: Final = 9
MARKER_SPEED_DIGIT: Final = 5
MARKER_CARRIER_HP_UNITS: Final = 209
PLAIN_CARRIER_HP_UNITS: Final = 0
SUPPORT_HP_SUB_TYPES: Final = range(5)
SUPPORT_POWER_POINT_SUB_TYPE: Final = 7
ALL_DIGITS: Final = tuple(range(10))
ALL_SPECIALS: Final = tuple(range(100))


def iter_front_candidates(request: CardRequest) -> Iterator[str]:
    """Yield front-read barcodes that should satisfy the request, in a fixed order."""
    for race in _races(request):
        if race.is_fighter:
            yield from _fighter_candidates(request, race)
        else:
            yield from _item_candidates(request, race)


def stat_digit_options(
    race: Race, *, hp_units: int, st_units: int, df_units: int
) -> list[tuple[int, int]]:
    """Return the digit pairs that decode to the requested strength and defence.

    Empty when no pair reaches the values. The branches `uncertainties.py`
    flags as blocking generation are never proposed, so a value only those
    branches can produce is reported as unreachable.
    """
    return [
        (st_digits, df_digits)
        for st_digits, df_digits in _raw_digit_options(race, hp_units, st_units, df_units)
        if not quarantines_digits(race, hp_units=hp_units, st_digits=st_digits, df_digits=df_digits)
    ]


def _raw_digit_options(
    race: Race, hp_units: int, st_units: int, df_units: int
) -> list[tuple[int, int]]:
    """The digit pairs that decode to the values, before any quarantine."""
    if hp_units < HIGH_HP or race not in _ADJUSTED_RACES:
        return _pair(st_units, df_units)
    if race is Race.AQUATIC:
        return _pair(st_units - HIGH_HP_BONUS_UNITS, df_units - HIGH_HP_BONUS_UNITS)
    if race is Race.MECHANICAL:
        lead, partner = _lead_options(st_units, df_units, partner_set_applies=True)
        return _pair(lead, partner)
    lead, partner = _lead_options(df_units, st_units, partner_set_applies=False)
    return _pair(partner, lead)


_ADJUSTED_RACES: Final = (Race.MECHANICAL, Race.ANIMAL, Race.AQUATIC)


def _lead_options(lead: int, partner: int, *, partner_set_applies: bool) -> tuple[int, int]:
    """The lead and partner digits that display as the requested values.

    The lead digits are fixed by the lead value alone, and they in turn decide
    whether the partner value carries a bonus that has to be taken back off.
    """
    lead_digits = lead - HIGH_HP_BONUS_UNITS
    partner_gains = lead_digits in BATTLE_BONUS_VALUES or (
        partner_set_applies and lead_digits in PARTNER_BONUS_VALUES
    )
    return lead_digits, partner - (HIGH_HP_BONUS_UNITS if partner_gains else 0)


def _pair(st_digits: int, df_digits: int) -> list[tuple[int, int]]:
    """Wrap a digit pair as the single option, or none when it does not fit."""
    if _is_digit_pair(st_digits) and _is_digit_pair(df_digits):
        return [(st_digits, df_digits)]
    return []


def _is_digit_pair(value: int) -> bool:
    """Whether a value fits the two digits available to it."""
    return 0 <= value <= MAX_DIGIT_PAIR


def _races(request: CardRequest) -> Sequence[Race]:
    """The races worth trying, honouring an explicit race or class constraint."""
    if request.race is not None:
        return (request.race,)
    return tuple(Race)


def _jobs(request: CardRequest) -> Sequence[int]:
    """The job digits worth trying, honouring an explicit job or class constraint."""
    if request.job is not None:
        return (request.job,)
    if request.character_class is CharacterClass.WARRIOR:
        return tuple(range(HIGHEST_WARRIOR_JOB + 1))
    if request.character_class is CharacterClass.MAGICIAN:
        return tuple(range(HIGHEST_WARRIOR_JOB + 1, 10))
    return ALL_DIGITS


def _specials(request: CardRequest) -> Sequence[int]:
    """The special ability codes worth trying."""
    return (request.special,) if request.special is not None else ALL_SPECIALS


def _speeds(request: CardRequest, hp_units: int) -> Sequence[int]:
    """The speed digits worth trying, which the marker forces above the threshold."""
    if hp_units >= HIGH_HP:
        forced = MARKER_SPEED_DIGIT
        if request.speed is not None and request.speed != forced:
            return ()
        return (forced,)
    return (request.speed,) if request.speed is not None else ALL_DIGITS


def _units(constraint: Constraint, ceiling: int) -> Sequence[int]:
    """Walk the constrained display values as device units."""
    return [
        value // DISPLAY_SCALE for value in constraint.values(step=DISPLAY_SCALE, ceiling=ceiling)
    ]


def _fighter_candidates(request: CardRequest, race: Race) -> Iterator[str]:
    """Yield candidates for a playable character, hit points first."""
    for hp_units in _units(request.hp, MAX_HP_DISPLAY):
        if hp_units >= HIGH_HP and hp_units % 10 != MARKER_HP_UNITS_ENDING:
            continue
        speeds = _speeds(request, hp_units)
        if speeds:
            yield from _fighter_for_hit_points(request, race, hp_units, speeds)


def _fighter_for_hit_points(
    request: CardRequest, race: Race, hp_units: int, speeds: Sequence[int]
) -> Iterator[str]:
    """Yield candidates for a character whose hit points are already fixed."""
    combinations = itertools.product(
        _units(request.st, MAX_STAT_DISPLAY),
        _units(request.df, MAX_STAT_DISPLAY),
        _jobs(request),
        _specials(request),
        speeds,
    )
    for st_units, df_units, job, special, speed in combinations:
        options = stat_digit_options(race, hp_units=hp_units, st_units=st_units, df_units=df_units)
        for st_digits, df_digits in options:
            yield assemble(
                hp_units=hp_units,
                st_digits=st_digits,
                df_digits=df_digits,
                race=race,
                job=job,
                speed=speed,
                special=special,
            )


def _item_candidates(request: CardRequest, race: Race) -> Iterator[str]:
    """Yield candidates for a weapon, a piece of armour, or a support item."""
    if race.is_weapon:
        values = [(value, 0, 0) for value in _units(request.st, MAX_STAT_DISPLAY)]
    elif race.is_armour:
        values = [(0, value, 0) for value in _units(request.df, MAX_STAT_DISPLAY)]
    else:
        values = _support_values(request)
    for (st_digits, df_digits, hp_units), special in itertools.product(values, _specials(request)):
        yield from _carried(request, race, hp_units, st_digits, df_digits, special)


def _support_values(request: CardRequest) -> list[tuple[int, int, int]]:
    """Strength, defence and hit point digits for a support item's sub-type."""
    sub_type = _support_sub_type(request)
    if sub_type in SUPPORT_HP_SUB_TYPES:
        return [(0, 0, value) for value in _units(request.hp, MAX_HP_DISPLAY)]
    if sub_type == SUPPORT_POWER_POINT_SUB_TYPE:
        return [(value, 0, 0) for value in _units(request.st, MAX_STAT_DISPLAY)]
    return [(0, value, 0) for value in _units(request.df, MAX_STAT_DISPLAY)]


def _support_sub_type(request: CardRequest) -> int:
    """The sub-type digit a support item uses, inferred when the request omits it."""
    if request.job is not None:
        return request.job
    if request.st.minimum is not None:
        return SUPPORT_POWER_POINT_SUB_TYPE
    if request.df.minimum is not None:
        return SUPPORT_POWER_POINT_SUB_TYPE + 1
    return 0


def _carried(
    request: CardRequest,
    race: Race,
    hp_units: int,
    st_digits: int,
    df_digits: int,
    special: int,
) -> Iterator[str]:
    """Emit the item under each carrier that can make the code a front read."""
    job = _support_sub_type(request) if race is Race.SUPPORT_ITEM else 0
    hp_is_free = hp_units == 0 and race is not Race.SUPPORT_ITEM
    for carrier_hp, speed in _carriers(
        request, hp_units, st_digits, df_digits, hp_is_free=hp_is_free
    ):
        yield assemble(
            hp_units=carrier_hp,
            st_digits=st_digits,
            df_digits=df_digits,
            race=race,
            job=job,
            speed=speed,
            special=special,
        )


def _carriers(
    request: CardRequest,
    hp_units: int,
    st_digits: int,
    df_digits: int,
    *,
    hp_is_free: bool,
) -> Sequence[tuple[int, int]]:
    """Hit point digits and speed digit that make an item's code a front read.

    The plain carrier leaves the leading digit at 0 and relies on the stat-bound
    fallback. The marker carrier raises the leading digit and supplies the
    published marker, which is the only route for a stat above the fallback
    bound. When the hit point digits carry a value rather than being free, the
    marker carrier can only be used if that value already ends in 9 and reaches
    the threshold, because overwriting it would change what the card decodes to.
    """
    plain_fits = (
        st_digits <= FALLBACK_MAX_ST_UNITS
        and df_digits <= FALLBACK_MAX_DF_UNITS
        and hp_units <= FALLBACK_MAX_HP_UNITS
    )
    carriers: list[tuple[int, int]] = []
    if plain_fits and (request.speed is None or request.speed == 0):
        carriers.append((hp_units or PLAIN_CARRIER_HP_UNITS, 0))
    if request.speed is not None and request.speed != MARKER_SPEED_DIGIT:
        return carriers
    marker_hp = MARKER_CARRIER_HP_UNITS if hp_is_free else hp_units
    if marker_hp >= HIGH_HP and marker_hp % 10 == MARKER_HP_UNITS_ENDING:
        carriers.append((marker_hp, MARKER_SPEED_DIGIT))
    return carriers


def assemble(
    *,
    hp_units: int,
    st_digits: int,
    df_digits: int,
    race: Race,
    job: int,
    speed: int,
    special: int,
) -> str:
    """Build a 13-digit barcode from digit values and append its check digit."""
    body = f"{hp_units:03d}{st_digits:02d}{df_digits:02d}{int(race)}{job}{speed}{special:02d}"
    return body + str(expected_check_digit(body))
