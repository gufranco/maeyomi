"""Turn a request into a barcode, and prove it before returning it.

Every candidate the inverter proposes is decoded and compared against the
request. A candidate that disagrees on any field is discarded, and a candidate
that would rest on an unresolved branch is discarded as well. No path returns a
barcode that skipped this check.

The front reading is tried by default because it carries the wider ranges. A
caller that wants a card the device reads from the back asks for it explicitly,
and the back-read inverter is used instead.
"""

import itertools
from dataclasses import dataclass, field
from typing import Final

from barcode_battler.decoder.decode import decode
from barcode_battler.decoder.errors import BarcodeError
from barcode_battler.generator.back_solver import iter_back_candidates
from barcode_battler.generator.blockers import blockers
from barcode_battler.generator.front_solver import iter_front_candidates
from barcode_battler.generator.quarantine import takes_quarantined_branch
from barcode_battler.models.card_request import CardRequest
from barcode_battler.models.character import BarcodeBattlerCharacter
from barcode_battler.models.read_type import ReadType

DEFAULT_BUDGET: Final = 500_000


@dataclass(frozen=True, slots=True)
class Mismatch:
    """One field where a candidate disagreed with the request."""

    field_name: str
    requested: str
    produced: str

    def __str__(self) -> str:
        """Render the disagreement for a report."""
        return f"{self.field_name}: requested {self.requested}, produced {self.produced}"


@dataclass(frozen=True, slots=True)
class SolveOutcome:
    """The result of one solve, whether or not it found a barcode."""

    request: CardRequest
    barcode: str | None = None
    character: BarcodeBattlerCharacter | None = None
    searched: int = 0
    budget_exhausted: bool = False
    blockers: tuple[str, ...] = ()
    mismatches: tuple[Mismatch, ...] = field(default_factory=tuple)

    @property
    def solved(self) -> bool:
        """Whether a verified barcode was found."""
        return self.barcode is not None


def solve(
    request: CardRequest,
    *,
    budget: int = DEFAULT_BUDGET,
    read_type: ReadType = ReadType.FRONT,
) -> SolveOutcome:
    """Find a barcode that decodes to the request, or explain why none exists."""
    known = blockers(request) if read_type is ReadType.FRONT else ()
    if known:
        return SolveOutcome(request=request, blockers=known)
    candidates = (
        iter_front_candidates(request)
        if read_type is ReadType.FRONT
        else (candidate.barcode for candidate in iter_back_candidates(request))
    )
    searched = 0
    for candidate in itertools.islice(candidates, budget):
        searched += 1
        character = verify(request, candidate)
        if character is not None:
            return SolveOutcome(
                request=request,
                barcode=candidate,
                character=character,
                searched=searched,
            )
    exhausted = searched >= budget
    return SolveOutcome(
        request=request,
        searched=searched,
        budget_exhausted=exhausted,
        blockers=_exhaustion_reason(request, exhausted=exhausted),
    )


def mismatches(request: CardRequest, character: BarcodeBattlerCharacter) -> tuple[Mismatch, ...]:
    """Every field where the decoded character disagrees with the request."""
    found: list[Mismatch] = []
    for name, constraint in (("hp", request.hp), ("st", request.st), ("df", request.df)):
        produced: int = getattr(character, name)
        if not constraint.admits(produced):
            found.append(Mismatch(name, str(constraint), str(produced)))
    found += _categorical_mismatches(request, character)
    return tuple(found)


def _categorical_mismatches(
    request: CardRequest, character: BarcodeBattlerCharacter
) -> list[Mismatch]:
    """Disagreements on the fields that carry one exact value or nothing."""
    pairs = (
        ("race", request.race, character.race),
        ("job", request.job, character.job),
        ("character_class", request.character_class, character.character_class),
        ("special", request.special, character.special.code),
        ("speed", request.speed, character.speed),
    )
    return [
        Mismatch(name, str(wanted), str(produced))
        for name, wanted, produced in pairs
        if wanted is not None and wanted != produced
    ]


def verify(request: CardRequest, candidate: str) -> BarcodeBattlerCharacter | None:
    """Return the decoded candidate when it satisfies the request, otherwise None."""
    if takes_quarantined_branch(candidate):
        return None
    try:
        character = decode(candidate)
    except BarcodeError:
        return None
    if mismatches(request, character):
        return None
    return character


def _exhaustion_reason(request: CardRequest, *, exhausted: bool) -> tuple[str, ...]:
    """Explain a search that ended without a match."""
    if exhausted:
        target = request.name or "this card"
        return (
            (
                "no barcode found within the search budget; raise the budget or "
                f"narrow the request for {target}"
            ),
        )
    return (
        (
            "no barcode satisfies every constraint at once; each field is reachable "
            "on its own, so at least two of them cannot hold together"
        ),
    )
