"""Reasons a request cannot be satisfied, named per field.

These are the constraints that can be decided without searching. A request that
clears every check here can still fail, because two fields can be individually
reachable and jointly impossible; the solver reports that case separately.
"""

from collections.abc import Sequence

from maeyomi.generator.front_solver import (
    HIGH_HP,
    MARKER_SPEED_DIGIT,
    MAX_HP_DISPLAY,
    MAX_STAT_DISPLAY,
)
from maeyomi.models.card_request import MAX_POINTS, CardRequest
from maeyomi.models.character import DISPLAY_SCALE, HIGHEST_WARRIOR_JOB
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.constraint import Constraint
from maeyomi.rendering.labels import class_label
from maeyomi.said import Said, field_in_japanese

HIGH_HP_DISPLAY = HIGH_HP * DISPLAY_SCALE
MARKER_HP_REMAINDER = 900


def blockers(request: CardRequest) -> tuple[str, ...]:
    """Return every reason the request cannot be satisfied, in field order."""
    reasons: list[str] = []
    reasons += _stat_blockers("hp", request.hp, MAX_HP_DISPLAY)
    reasons += _stat_blockers("st", request.st, MAX_STAT_DISPLAY)
    reasons += _stat_blockers("df", request.df, MAX_STAT_DISPLAY)
    reasons += _count_blockers("pp", request.pp)
    reasons += _count_blockers("mp", request.mp)
    reasons += _high_hp_blockers(request)
    reasons += _class_blockers(request)
    return tuple(reasons)


def _stat_blockers(name: str, constraint: Constraint, ceiling: int) -> Sequence[str]:
    """Reasons a single stat constraint cannot be met."""
    value = constraint.exact_value
    reasons: list[str] = []
    if value is not None and value % DISPLAY_SCALE:
        reasons.append(
            Said(
                f"{name} of {value} is not a multiple of 100, which the device stores",
                f"{field_in_japanese(name)} {value} は 100 ずつに して。マシンは 100 ずつ おぼえる",
            )
        )
    if constraint.minimum is not None and constraint.minimum > ceiling:
        reasons.append(
            Said(
                f"{name} of {constraint.minimum} is above the front-read ceiling of {ceiling}",
                f"{field_in_japanese(name)} {constraint.minimum} は まえよみの さいだい"
                f" {ceiling} より おおきい",
            )
        )
    if constraint.minimum is not None and constraint.minimum < 0:
        reasons.append(
            Said(
                f"{name} of {constraint.minimum} is below zero",
                f"{field_in_japanese(name)} {constraint.minimum} は 0 より ちいさい",
            )
        )
    return reasons


def _count_blockers(name: str, constraint: Constraint) -> Sequence[str]:
    """Reasons a count of herbs or magic points cannot be met."""
    reasons: list[str] = []
    if constraint.minimum is not None and constraint.minimum > MAX_POINTS:
        reasons.append(
            Said(
                f"{name} of {constraint.minimum} is above the ceiling of {MAX_POINTS}",
                f"{field_in_japanese(name)} {constraint.minimum} は さいだい"
                f" {MAX_POINTS} より おおきい",
            )
        )
    if constraint.minimum is not None and constraint.minimum < 0:
        reasons.append(
            Said(
                f"{name} of {constraint.minimum} is below zero",
                f"{field_in_japanese(name)} {constraint.minimum} は 0 より ちいさい",
            )
        )
    return reasons


def _high_hp_blockers(request: CardRequest) -> Sequence[str]:
    """Reasons a request above the high hit point threshold cannot be met."""
    value = request.hp.exact_value
    if value is None or value < HIGH_HP_DISPLAY or value > MAX_HP_DISPLAY:
        return ()
    reasons: list[str] = []
    if value % 1000 != MARKER_HP_REMAINDER:
        reasons.append(
            Said(
                f"hp of {value} is unreachable: above {HIGH_HP_DISPLAY} a front read needs the "
                "published marker, which forces the third digit to 9, so hp must end in 900",
                f"たいりょく {value} は つくれない。{HIGH_HP_DISPLAY} を こえると 3けための"
                " すうじが 9 に きまるので、たいりょくは 900 で おわる かずに して",
            )
        )
    if request.speed is not None and request.speed != MARKER_SPEED_DIGIT:
        reasons.append(
            Said(
                f"speed of {request.speed} is unreachable above {HIGH_HP_DISPLAY} hp, where the "
                f"marker forces the tenth digit, and therefore speed, to {MARKER_SPEED_DIGIT}",
                f"たいりょくが {HIGH_HP_DISPLAY} を こえると スピードは {MARKER_SPEED_DIGIT}"
                f" に きまるので、スピード {request.speed} は つくれない",
            )
        )
    return reasons


def _class_blockers(request: CardRequest) -> Sequence[str]:
    """Reasons an explicit job and an explicit class contradict each other."""
    if request.job is None or request.character_class is None:
        return ()
    implied = (
        CharacterClass.WARRIOR if request.job <= HIGHEST_WARRIOR_JOB else CharacterClass.MAGICIAN
    )
    if implied is request.character_class:
        return ()
    return (
        Said(
            f"job {request.job} implies class {implied.value}, which contradicts the "
            f"requested class {request.character_class.value}",
            f"しょくぎょう {request.job} は {class_label(implied).japanese} なので、えらんだ"
            f" たたかいかたの {class_label(request.character_class).japanese} と あわない",
        ),
    )
