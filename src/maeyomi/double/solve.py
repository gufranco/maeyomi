"""Build a Barcode Battler II Double card with its 7-read, and prove it.

The 7-read places every number directly, with one coupling: the special power
is the 3rd and 12th digits, which are also the thousands and hundreds of the
health. Asking for a power therefore fixes two digits of the health, and the
solver walks only the health values that keep them. Every candidate is decoded
by `decode_double` and compared with the request before it is returned.

The race is the attack's hundreds digit less 5, so asking for a race fixes
that digit.

The Double names its jobs its own way: 0 to 3 and 5 are warriors, 4 a priest,
6 a holy warrior and 7 to 9 magicians. A class in the request picks from those.
"""

import itertools
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Final

from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.double.card import DoubleCard
from maeyomi.double.decode import RACE_OFFSET, decode_double
from maeyomi.models.card_request import CardRequest
from maeyomi.models.character import DISPLAY_SCALE
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.constraint import Constraint
from maeyomi.said import NO_MATCH, Said, above_ceiling, not_a_multiple

MAX_VALUE: Final = 99900
SEARCH_LIMIT: Final = 5000
DOUBLE_JOBS: Final[dict[CharacterClass, tuple[int, ...]]] = {
    CharacterClass.WARRIOR: (0, 1, 2, 3, 5),
    CharacterClass.MAGICIAN: (7, 8, 9),
}


@dataclass(frozen=True, slots=True)
class DoubleSolveOutcome:
    """A verified card, or the reasons none exists."""

    request: CardRequest
    card: DoubleCard | None = None
    blockers: tuple[str, ...] = ()


def solve_double(request: CardRequest) -> DoubleSolveOutcome:
    """Find a 7-read barcode the Double reads as the request."""
    reasons = _blockers(request)
    if reasons:
        return DoubleSolveOutcome(request, blockers=reasons)
    decoded = map(decode_double, itertools.islice(_candidates(request), SEARCH_LIMIT))
    card = next((card for card in decoded if _matches(request, card)), None)
    if card is None:
        return DoubleSolveOutcome(request, blockers=(NO_MATCH,))
    return DoubleSolveOutcome(request, card=card)


def _matches(request: CardRequest, card: DoubleCard) -> bool:
    """Whether a decoded card satisfies every field the request constrains."""
    stats = all(getattr(request, name).admits(getattr(card, name)) for name in ("hp", "st", "df"))
    job = request.job is None or request.job == card.job
    race = request.race is None or request.race is card.race
    return (
        stats and job and race and (request.special is None or request.special == card.special.code)
    )


def _blockers(request: CardRequest) -> tuple[str, ...]:
    """Every reason the request cannot be met, decided without searching."""
    reasons: list[str] = []
    if request.race is not None and not request.race.is_fighter:
        reasons.append(
            Said("a 7-read card is always a fighter", "7よみの カードは いつも キャラクター")
        )
    if request.speed is not None:
        reasons.append(
            Said(
                "a 7-read card has no speed any source records",
                "7よみの カードの スピードは どの しりょうにも ない",
            )
        )
    if _constrained(request.pp) or _constrained(request.mp):
        reasons.append(
            Said(
                "a 7-read card carries no herbs or magic points",
                "7よみの カードには やくそうも まほうも ない",
            )
        )
    for name in ("hp", "st", "df"):
        reasons += _value_blockers(name, getattr(request, name))
    return (*reasons, *_coupling_blockers(request))


def _value_blockers(name: str, constraint: Constraint) -> list[str]:
    """Reasons one number cannot be met."""
    reasons: list[str] = []
    if constraint.exact_value is not None and constraint.exact_value % DISPLAY_SCALE:
        reasons.append(not_a_multiple(name, constraint.exact_value, DISPLAY_SCALE))
    if constraint.minimum is not None and constraint.minimum > MAX_VALUE:
        reasons.append(above_ceiling(name, constraint.minimum, MAX_VALUE))
    return reasons


def _coupling_blockers(request: CardRequest) -> list[str]:
    """The reason an exact health cannot carry the requested power, if it cannot."""
    hp = request.hp.exact_value
    if request.special is None or hp is None or _power_of(hp // DISPLAY_SCALE) == request.special:
        return []
    tens, units = divmod(request.special, 10)
    return [
        Said(
            f"special power {request.special} needs the health's thousands digit {tens} "
            f"and hundreds digit {units}",
            f"とくしゅのうりょく {request.special} には たいりょくの 1000の くらいが {tens}、"
            f"100の くらいが {units} で ないと いけない",
        )
    ]


def _constrained(constraint: Constraint) -> bool:
    """Whether a constraint asks for anything at all."""
    return constraint.minimum is not None or constraint.maximum is not None


def highest_health_for(power: int) -> int:
    """The most health a 7-read card can carry alongside this special power."""
    ceiling = MAX_VALUE // DISPLAY_SCALE
    fitting = [units for units in range(ceiling + 1) if _power_of(units) == power]
    return max(fitting) * DISPLAY_SCALE


def _power_of(hp_units: int) -> int:
    """The special power a health value forces: its thousands and hundreds digits."""
    return (hp_units // 10 % 10) * 10 + hp_units % 10


def _candidates(request: CardRequest) -> Iterator[str]:
    """7-read codes in ascending order of health, attack and defence."""
    healths = [
        units
        for units in _units(request.hp)
        if request.special is None or _power_of(units) == request.special
    ]
    strengths = [
        units
        for units in _units(request.st)
        if request.race is None or units % 10 == request.race + RACE_OFFSET
    ]
    for job in _jobs(request):
        for hp, st, df in itertools.product(healths, strengths, _units(request.df)):
            yield _assemble(hp, st, df, job)


def _jobs(request: CardRequest) -> tuple[int, ...]:
    """The job digits worth trying, honouring an explicit job or class."""
    if request.job is not None:
        return (request.job,)
    if request.character_class is not None:
        return DOUBLE_JOBS[request.character_class]
    return (0,)


def _units(constraint: Constraint) -> list[int]:
    """Admitted display values as device units, ascending."""
    return [
        value // DISPLAY_SCALE for value in constraint.values(step=DISPLAY_SCALE, ceiling=MAX_VALUE)
    ]


def _assemble(hp: int, st: int, df: int, job: int) -> str:
    """Place every digit, then append the check digit."""
    h, s, d = f"{hp:03d}", f"{st:03d}", f"{df:03d}"
    body = f"7{h[0]}{h[1]}{s[0]}{s[1]}{d[0]}{d[1]}{s[2]}{job}8{d[2]}{h[2]}"
    return body + str(expected_check_digit(body))
