"""Inversion of the back reading.

The back reading is not a bijection the way the front reading is. Four digits,
at indices 8 through 11, feed hit points, strength, defence and the special
ability jointly, so choosing one attribute constrains the rest. That makes the
reachable set small enough to enumerate outright: 10000 digit combinations,
producing 5000 distinct stat triples, because the hit point hundreds digit is
halved and so collapses ten digit values onto five.

Two things make this harder than the front reading and are handled here:

1. The race sits at index 12, which is also the check digit position. A
   back-read race therefore cannot be placed; it has to be arrived at. One free
   digit is tuned until the computed check digit equals the requested race.
2. Several digit combinations produce the same attributes. The inverter emits
   the lowest-valued representative and reports how many others it passed over,
   so a caller can tell a unique answer from an arbitrary pick.

Candidates are proposals. Nothing here is trusted until the solver has run it
back through the decoder.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Final

from maeyomi.decoder.back_read import read_back
from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.models.card_request import CardRequest
from maeyomi.models.race import Race
from maeyomi.models.special_ability import MAX_BACK_READ_CODE

CODE_LENGTH: Final = 13
CHECK_DIGIT_INDEX: Final = 12
JOB_INDEX: Final = 5
TUNING_INDEX: Final = 1
LEADING_DIGIT: Final = 2
MARKER_PREFIX_INDEX: Final = 2
NON_MARKER_PREFIX: Final = 0
STAT_INDICES: Final = (8, 9, 10, 11)


@dataclass(frozen=True, slots=True)
class BackReadCandidate:
    """One proposed back-read barcode and how many equals it stood in for."""

    barcode: str
    alternatives: int


def reachable_back_stats(race: Race) -> set[tuple[int, int, int]]:
    """Every hit point, strength and defence triple a back read can carry."""
    return {_attributes_of(digits, race)[:3] for digits in _stat_digit_combinations()}


def iter_back_candidates(request: CardRequest) -> Iterator[BackReadCandidate]:
    """Yield back-read barcodes that should satisfy the request, in a fixed order."""
    race = request.race
    if race is None or not race.is_fighter:
        return
    if request.special is not None and request.special > MAX_BACK_READ_CODE:
        return
    grouped = _group_by_attributes(request, race)
    for digits_list in grouped.values():
        yield BackReadCandidate(
            barcode=_assemble(digits_list[0], request, race),
            alternatives=len(digits_list) - 1,
        )


def _stat_digit_combinations() -> Iterator[tuple[int, int, int, int]]:
    """Every value of the four digits that jointly carry the attributes."""
    for d8 in range(10):
        for d9 in range(10):
            for d10 in range(10):
                for d11 in range(10):
                    yield (d8, d9, d10, d11)


def _group_by_attributes(
    request: CardRequest, race: Race
) -> dict[tuple[int, int, int, int], list[tuple[int, int, int, int]]]:
    """Collect digit combinations that produce identical attributes."""
    grouped: dict[tuple[int, int, int, int], list[tuple[int, int, int, int]]] = {}
    for digits in _stat_digit_combinations():
        attributes = _attributes_of(digits, race)
        if not _wanted(request, attributes):
            continue
        grouped.setdefault(attributes, []).append(digits)
    return grouped


def _wanted(request: CardRequest, attributes: tuple[int, int, int, int]) -> bool:
    """Whether these attributes satisfy the request."""
    hp, st, df, special = attributes
    if not (request.hp.admits(hp) and request.st.admits(st) and request.df.admits(df)):
        return False
    return request.special is None or request.special == special


def _attributes_of(digits: tuple[int, int, int, int], race: Race) -> tuple[int, int, int, int]:
    """Decode the stats and ability a digit combination carries, in one read."""
    character = read_back(_probe(digits, race))
    return character.hp, character.st, character.df, character.special.code


def _probe(digits: tuple[int, int, int, int], race: Race) -> str:
    """Build a throwaway code carrying these digits, for reading attributes off."""
    body = ["0"] * CODE_LENGTH
    for index, value in zip(STAT_INDICES, digits, strict=True):
        body[index] = str(value)
    body[CHECK_DIGIT_INDEX] = str(int(race))
    return "".join(body)


def _assemble(digits: tuple[int, int, int, int], request: CardRequest, race: Race) -> str:
    """Build a real code whose check digit is the requested race.

    The tuning digit sits at an odd index, where its weight is 3, so stepping it
    through 0 to 9 moves the check digit through every residue. Some value
    therefore always lands on the requested race. `test_back_solver.py` asserts
    that rather than leaving it as an assumption.
    """
    body = ["0"] * CODE_LENGTH
    body[0] = str(LEADING_DIGIT)
    body[MARKER_PREFIX_INDEX] = str(NON_MARKER_PREFIX)
    body[JOB_INDEX] = str(request.job if request.job is not None else 0)
    for index, value in zip(STAT_INDICES, digits, strict=True):
        body[index] = str(value)
    tuning = next(value for value in range(10) if _check_digit_with(body, value) == int(race))
    body[TUNING_INDEX] = str(tuning)
    return "".join(body[:CHECK_DIGIT_INDEX]) + str(int(race))


def _check_digit_with(body: list[str], tuning: int) -> int:
    """The check digit this body would carry with the given tuning digit."""
    probe = list(body)
    probe[TUNING_INDEX] = str(tuning)
    return expected_check_digit("".join(probe[:CHECK_DIGIT_INDEX]))
