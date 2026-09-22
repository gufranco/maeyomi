"""The closest card to a request that cannot be satisfied exactly.

This is opt-in. The exact solver reports which field blocks a request and stops
there, because a card that quietly differs from what was asked for is the
failure this project exists to prevent. The nearest match exists for the case
where the caller has read that report and wants the closest reachable card
anyway.

**Distance.** The sum of the absolute gaps on HP, ST and DF, in displayed
units, counting only the stats the request constrained. A request for 20900 HP
answered with 20900 HP and 10900 ST against a requested 11000 scores 100.

**What is never approximated.** Race, job, class, ability and speed are
categorical: a request for a human is not better served by a bird. Those stay
exact, and a request blocked on one of them comes back unsatisfied rather than
substituted.

**Bounded on purpose.** Only hit point values within a window of the request are
considered, so the search is predictable and the answer stays recognisably close
to what was asked for. Finding nothing in the window is reported rather than
silently widened.

**Characters only.** An item carries one modifier rather than three stats, so
there is nothing to trade off. A request for an item is reported as outside this
search rather than approximated.
"""

from dataclasses import dataclass
from typing import Final

from barcode_battler.decoder.decode import decode
from barcode_battler.decoder.front_read import HIGH_HP_THRESHOLD_UNITS, adjusted_stats
from barcode_battler.generator.blockers import blockers
from barcode_battler.generator.front_solver import (
    MARKER_HP_UNITS_ENDING,
    MARKER_SPEED_DIGIT,
    MAX_HP_DISPLAY,
    MAX_STAT_DISPLAY,
    assemble,
)
from barcode_battler.generator.quarantine import takes_quarantined_branch
from barcode_battler.generator.solve import solve
from barcode_battler.models.card_request import CardRequest
from barcode_battler.models.character import DISPLAY_SCALE, BarcodeBattlerCharacter
from barcode_battler.models.character_class import CharacterClass
from barcode_battler.models.constraint import Constraint
from barcode_battler.models.race import Race

DEFAULT_WINDOW: Final = 2000
CATEGORICAL_FIELDS: Final = ("race", "job", "character_class", "special", "speed")
MAX_DIGIT_PAIR: Final = 99
LOWEST_MAGICIAN_JOB: Final = 7
_MAX_HP_UNITS: Final = MAX_HP_DISPLAY // DISPLAY_SCALE
_MAX_STAT_UNITS: Final = MAX_STAT_DISPLAY // DISPLAY_SCALE


@dataclass(frozen=True, slots=True)
class NearestOutcome:
    """The closest reachable card, or the reason there is none."""

    request: CardRequest
    barcode: str | None = None
    character: BarcodeBattlerCharacter | None = None
    distance: int = 0
    differences: tuple[str, ...] = ()
    searched: int = 0
    blockers: tuple[str, ...] = ()

    @property
    def is_exact(self) -> bool:
        """Whether the closest card is the card that was asked for."""
        return self.barcode is not None and self.distance == 0


def solve_nearest(request: CardRequest, *, window: int = DEFAULT_WINDOW) -> NearestOutcome:
    """Return the closest card to the request, keeping categorical fields exact."""
    known = blockers(request) + _item_blockers(request)
    if known:
        return NearestOutcome(request=request, blockers=known)
    exact = solve(request)
    if exact.barcode is not None and exact.character is not None:
        return NearestOutcome(
            request=request,
            barcode=exact.barcode,
            character=exact.character,
            searched=exact.searched,
        )
    return _search(request, window)


def _item_blockers(request: CardRequest) -> tuple[str, ...]:
    """The nearest match covers characters only."""
    if request.race is None or request.race.is_fighter:
        return ()
    return (
        (
            f"race {request.race.name.lower()} is an item, which carries one modifier "
            f"rather than three stats, so there is nothing to approximate"
        ),
    )


def _search(request: CardRequest, window: int) -> NearestOutcome:
    """Walk the reachable cards inside the window and keep the closest."""
    best: tuple[int, str] | None = None
    searched = 0
    for hp_units in _hp_candidates(request, window):
        for st_digits, df_digits in _digit_pairs():
            searched += 1
            scored = _score(request, hp_units, st_digits, df_digits)
            if scored is not None and (best is None or scored[0] < best[0]):
                best = scored
    if best is None:
        return NearestOutcome(request=request, searched=searched, blockers=_empty(window))
    return _verified(request, best[1], searched)


def _digit_pairs() -> list[tuple[int, int]]:
    """Every strength and defence digit pair, in ascending order."""
    return [
        (st_digits, df_digits)
        for st_digits in range(MAX_DIGIT_PAIR + 1)
        for df_digits in range(MAX_DIGIT_PAIR + 1)
    ]


def _hp_candidates(request: CardRequest, window: int) -> list[int]:
    """Hit point values inside the window that a front read can carry."""
    target = request.hp.exact_value
    low, high = _window_bounds(request, target, window)
    return [
        units
        for units in range(max(0, low), min(_MAX_HP_UNITS, high) + 1)
        if units < HIGH_HP_THRESHOLD_UNITS or units % 10 == MARKER_HP_UNITS_ENDING
    ]


def _window_bounds(request: CardRequest, target: int | None, window: int) -> tuple[int, int]:
    """The inclusive range of hit point units the search may consider."""
    if target is not None:
        span = window // DISPLAY_SCALE
        return target // DISPLAY_SCALE - span, target // DISPLAY_SCALE + span
    minimum = request.hp.minimum if request.hp.minimum is not None else 0
    maximum = request.hp.maximum if request.hp.maximum is not None else MAX_HP_DISPLAY
    return minimum // DISPLAY_SCALE, maximum // DISPLAY_SCALE


def _score(
    request: CardRequest, hp_units: int, st_digits: int, df_digits: int
) -> tuple[int, str] | None:
    """Score one reachable card, or None when it is out of range or quarantined."""
    race = request.race if request.race is not None else Race.HUMAN
    st_units, df_units = adjusted_stats(
        race, hp_units=hp_units, st_digits=st_digits, df_digits=df_digits
    )
    if not 0 <= st_units <= _MAX_STAT_UNITS or not 0 <= df_units <= _MAX_STAT_UNITS:
        return None
    code = assemble(
        hp_units=hp_units,
        st_digits=st_digits,
        df_digits=df_digits,
        race=race,
        job=_job(request),
        speed=_speed(request, hp_units),
        special=request.special if request.special is not None else 0,
    )
    if takes_quarantined_branch(code):
        return None
    distance = _distance(request, hp_units, st_units, df_units)
    return distance, code


def _distance(request: CardRequest, hp_units: int, st_units: int, df_units: int) -> int:
    """Sum the gaps on the stats the request constrained, in displayed units."""
    produced = {
        "hp": hp_units * DISPLAY_SCALE,
        "st": st_units * DISPLAY_SCALE,
        "df": df_units * DISPLAY_SCALE,
    }
    total = 0
    for name, value in produced.items():
        constraint: Constraint = getattr(request, name)
        total += _gap(constraint, value)
    return total


def _gap(constraint: Constraint, value: int) -> int:
    """How far a value falls outside a constraint, zero when it satisfies it."""
    if constraint.minimum is not None and value < constraint.minimum:
        return constraint.minimum - value
    if constraint.maximum is not None and value > constraint.maximum:
        return value - constraint.maximum
    return 0


def _job(request: CardRequest) -> int:
    """The job digit to place, honouring an explicit job or class."""
    if request.job is not None:
        return request.job
    if request.character_class is CharacterClass.MAGICIAN:
        return LOWEST_MAGICIAN_JOB
    return 0


def _speed(request: CardRequest, hp_units: int) -> int:
    """The speed digit to place, which the marker forces above the threshold."""
    if hp_units >= HIGH_HP_THRESHOLD_UNITS:
        return MARKER_SPEED_DIGIT
    return request.speed if request.speed is not None else 0


def _verified(request: CardRequest, code: str, searched: int) -> NearestOutcome:
    """Decode the winner and report what it does not match."""
    character = decode(code)
    distance = _distance(request, character.hp_units, character.st_units, character.df_units)
    return NearestOutcome(
        request=request,
        barcode=code,
        character=character,
        distance=distance,
        differences=_differences(request, character),
        searched=searched,
    )


def _differences(request: CardRequest, character: BarcodeBattlerCharacter) -> tuple[str, ...]:
    """Name each stat that came out different, with both values."""
    return tuple(
        f"{name}: requested {getattr(request, name)}, produced {getattr(character, name)}"
        for name in ("hp", "st", "df")
        if not getattr(request, name).admits(getattr(character, name))
    )


def _empty(window: int) -> tuple[str, ...]:
    """Explain a window that contained nothing reachable."""
    return (
        (
            f"no reachable card within a window of {window} hit points; widen the "
            f"window or relax a categorical field, which is never approximated"
        ),
    )
