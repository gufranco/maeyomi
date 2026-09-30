"""Build a first Barcode Battler card to order, and prove it before returning it.

Both readings place digits directly, so a request fixes every digit but the
check digit and the solver only walks the values a range admits. Every
candidate is decoded by `decode_first` and compared with the request; nothing
is returned that skipped that step.

An enemy read from the back takes its flag from the check digit according to
one source and has no flag according to the other. A free digit is therefore
tuned until the check digit is 0, which both sources read as no ability, and a
request that names a flag for an enemy is refused.
"""

import itertools
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Final

from maeyomi.bb1.card import FirstBattlerCard
from maeyomi.bb1.decode import ENEMY_JOB, decode_first
from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.models.card_request import CardRequest
from maeyomi.models.character import DISPLAY_SCALE
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.constraint import Constraint
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType
from maeyomi.said import NO_MATCH, Said, above_ceiling, field_in_japanese, not_a_multiple

MAX_HP: Final = 19900
MAX_STAT: Final = 9900
ENEMY_HP: Final = (100, 10000)
ENEMY_ST: Final = (1000, 1900)
ENEMY_DF: Final = (100, 900)
SEARCH_LIMIT: Final = 5000
ENEMY_LEAD: Final = "2"
ENEMY_FILLER: Final = "000000"
NO_FLAG_CHECK_DIGIT: Final = 0
WARRIORS_ONLY: Final = Said(
    "every fighter on the first Barcode Battler is a warrior",
    "しょだい バーコードバトラーの キャラクターは みんな せんし",
)
NO_POINTS: Final = Said(
    "the first Barcode Battler has no herbs or magic points",
    "しょだい バーコードバトラーには やくそうも まほうも ない",
)


@dataclass(frozen=True, slots=True)
class FirstSolveOutcome:
    """A verified card, or the reasons none exists."""

    request: CardRequest
    card: FirstBattlerCard | None = None
    blockers: tuple[str, ...] = ()


def solve_first(request: CardRequest, *, read_type: ReadType = ReadType.FRONT) -> FirstSolveOutcome:
    """Find a barcode the first Barcode Battler reads as the request."""
    if read_type is ReadType.BACK:
        return _solved(request, _enemy_blockers(request), _enemy_candidates(request))
    return _solved(request, _front_blockers(request), _front_candidates(request))


def _solved(
    request: CardRequest, reasons: tuple[str, ...], candidates: Iterator[str]
) -> FirstSolveOutcome:
    """Return the first candidate that decodes to the request, or why none did."""
    if reasons:
        return FirstSolveOutcome(request, blockers=reasons)
    for code in itertools.islice(candidates, SEARCH_LIMIT):
        card = decode_first(code)
        if _matches(request, card):
            return FirstSolveOutcome(request, card=card)
    return FirstSolveOutcome(request, blockers=(NO_MATCH,))


def _matches(request: CardRequest, card: FirstBattlerCard) -> bool:
    """Whether a decoded card satisfies every field the request constrains."""
    stats = request.hp.admits(card.hp) and request.st.admits(card.st)
    exact = (
        (request.race, card.race),
        (request.job, card.job),
        (request.speed, card.dx),
        (request.special, card.flag.code),
    )
    return stats and request.df.admits(card.df) and all(w is None or w == g for w, g in exact)


def _shared_blockers(request: CardRequest) -> list[str]:
    """Reasons that hold whichever way the card is read."""
    reasons: list[str] = []
    if request.character_class is CharacterClass.MAGICIAN:
        reasons.append(WARRIORS_ONLY)
    if _constrained(request.pp) or _constrained(request.mp):
        reasons.append(NO_POINTS)
    for name in ("hp", "st", "df"):
        value = getattr(request, name).exact_value
        if value is not None and value % DISPLAY_SCALE:
            reasons.append(not_a_multiple(name, value, DISPLAY_SCALE))
    return reasons


def _front_blockers(request: CardRequest) -> tuple[str, ...]:
    """Reasons a front-read card cannot be built."""
    reasons = _shared_blockers(request)
    for name, ceiling in (("hp", MAX_HP), ("st", MAX_STAT), ("df", MAX_STAT)):
        minimum = getattr(request, name).minimum
        if minimum is not None and minimum > ceiling:
            reasons.append(above_ceiling(name, minimum, ceiling))
    return tuple(reasons)


def _enemy_blockers(request: CardRequest) -> tuple[str, ...]:
    """Reasons an enemy read from the back cannot be built."""
    reasons = _shared_blockers(request)
    for name, (low, high) in (("hp", ENEMY_HP), ("st", ENEMY_ST), ("df", ENEMY_DF)):
        constraint: Constraint = getattr(request, name)
        if not any(True for _ in constraint.values(step=DISPLAY_SCALE, floor=low, ceiling=high)):
            shown = constraint.minimum if constraint.minimum is not None else constraint.maximum
            reasons.append(
                Said(
                    f"{name} of {shown} is outside the enemy range of {low} to {high}",
                    f"{field_in_japanese(name)} {shown} は てきの はんい {low}〜{high} の そと",
                )
            )
    if request.race is not None:
        reasons.append(
            Said(
                "an enemy read from the back has no race any source records",
                "うしろから よむ てきの しゅぞくは どの しりょうにも ない",
            )
        )
    if request.special is not None:
        reasons.append(
            Said(
                "an enemy's flag is disputed, see bb1_back_read_flag",
                "てきの とくしゅのうりょくは しりょうに よって ちがうので えらべない",
            )
        )
    if request.speed is not None or request.job not in {None, ENEMY_JOB}:
        reasons.append(
            Said(
                "an enemy has no DX any source records and always has occupation 2",
                "てきの DX は どの しりょうにも なく、しょくぎょうは いつも 2",
            )
        )
    return tuple(reasons)


def _constrained(constraint: Constraint) -> bool:
    """Whether a constraint asks for anything at all."""
    return constraint.minimum is not None or constraint.maximum is not None


def _front_candidates(request: CardRequest) -> Iterator[str]:
    """Front-read codes in ascending order of the values they carry."""
    race = request.race if request.race is not None else Race.HUMAN
    tail = f"{race}{request.job or 0}{request.speed or 0}{request.special or 0:02d}"
    for hp, st, df in itertools.product(*_carried_units(request, race)):
        body = f"{hp:03d}{st:02d}{df:02d}{tail}"
        yield body + str(expected_check_digit(body))


def _carried_units(request: CardRequest, race: Race) -> tuple[list[int], list[int], list[int]]:
    """The unit values to walk for HP, ST and DF, zero for what the kind does not carry."""
    hp = _units(request.hp, MAX_HP)
    st = _units(request.st, MAX_STAT)
    df = _units(request.df, MAX_STAT)
    if race.is_fighter:
        return hp, st, df
    if race.is_weapon:
        return [0], st, [0]
    if race.is_armour:
        return [0], [0], df
    return hp, [0], [0]


def _units(constraint: Constraint, ceiling: int, floor: int = 0) -> list[int]:
    """Admitted display values as device units, ascending."""
    values = constraint.values(step=DISPLAY_SCALE, floor=floor, ceiling=ceiling)
    return [value // DISPLAY_SCALE for value in values]


def _enemy_candidates(request: CardRequest) -> Iterator[str]:
    """Back-read codes, each tuned so its check digit is 0."""
    return iter(
        [
            _tuned(_enemy_tail(hp, st, df))
            for hp, st, df in itertools.product(
                _units(request.hp, ENEMY_HP[1], ENEMY_HP[0]),
                _units(request.st, ENEMY_ST[1], ENEMY_ST[0]),
                _units(request.df, ENEMY_DF[1], ENEMY_DF[0]),
            )
        ]
    )


def _enemy_tail(hp: int, st: int, df: int) -> str:
    """The digits after the free ones: filler, health, strength and defence."""
    tens, hundreds = divmod(hp % 100, 10)
    return f"{ENEMY_FILLER}{tens}{hundreds}{st - 10}{df}"


def _tuned(tail: str) -> str:
    """Pick the free second digit that makes the check digit 0."""
    body = next(
        f"{ENEMY_LEAD}{digit}{tail}"
        for digit in range(10)
        if expected_check_digit(f"{ENEMY_LEAD}{digit}{tail}") == NO_FLAG_CHECK_DIGIT
    )
    return f"{body}{NO_FLAG_CHECK_DIGIT}"
