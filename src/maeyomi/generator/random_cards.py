"""Random cards drawn through the real algorithm rather than invented.

Every card is produced by sampling concrete values inside the caller's ranges,
inverting them into a barcode, and decoding that barcode back. Nothing is
randomised after the decode, so a printed card always advertises what the
device will read.

A run is reproducible: the same seed and the same template give the same
ordered batch. A run that cannot fill the batch reports the shortfall rather
than returning fewer cards silently.
"""

import random
from dataclasses import dataclass
from typing import Final

from maeyomi.generator.front_solver import MAX_HP_DISPLAY, PUBLISHED_MAX_STAT_DISPLAY
from maeyomi.generator.solve import solve
from maeyomi.models.card_request import CardRequest
from maeyomi.models.character import DISPLAY_SCALE
from maeyomi.models.constraint import Constraint
from maeyomi.models.generated_card import GeneratedCard
from maeyomi.models.race import Race

ATTEMPTS_PER_CARD: Final = 200
HIGH_HP_DISPLAY: Final = 20000
MARKER_HP_REMAINDER: Final = 900


@dataclass(frozen=True, slots=True)
class RandomBatch:
    """The outcome of one random generation run."""

    cards: tuple[GeneratedCard, ...] = ()
    requested: int = 0
    attempts: int = 0
    reason: str = ""
    seed: int | None = None

    @property
    def shortfall(self) -> int:
        """How many fewer cards were produced than were asked for."""
        return self.requested - len(self.cards)


def generate_random(
    count: int,
    *,
    template: CardRequest,
    seed: int | None = None,
    attempts_per_card: int = ATTEMPTS_PER_CARD,
) -> RandomBatch:
    """Produce up to `count` distinct cards whose attributes sit inside the template."""
    rng = random.Random(seed)
    cards: list[GeneratedCard] = []
    seen: set[str] = set()
    attempts = 0
    budget = count * attempts_per_card
    while len(cards) < count and attempts < budget:
        attempts += 1
        card = _try_one(rng, template, len(cards))
        if card is None or card.barcode in seen:
            continue
        seen.add(card.barcode)
        cards.append(card)
    return RandomBatch(
        cards=tuple(cards),
        requested=count,
        attempts=attempts,
        seed=seed,
        reason=_reason(len(cards), count, attempts, budget),
    )


def _try_one(rng: random.Random, template: CardRequest, index: int) -> GeneratedCard | None:
    """Sample one concrete request from the template and solve it."""
    request = _sample(rng, template, index)
    outcome = solve(request)
    if outcome.barcode is None or outcome.character is None:
        return None
    return GeneratedCard(name=request.name, barcode=outcome.barcode, character=outcome.character)


def _sample(rng: random.Random, template: CardRequest, index: int) -> CardRequest:
    """Draw one exact request from the template's ranges."""
    race = template.race if template.race is not None else rng.choice(_FIGHTERS)
    return CardRequest(
        name=template.name or f"{race.name.replace('_', ' ').title()} {index + 1:02d}",
        hp=Constraint.exactly(_pick_hp(rng, template.hp)),
        st=Constraint.exactly(_pick(rng, template.st, PUBLISHED_MAX_STAT_DISPLAY)),
        df=Constraint.exactly(_pick(rng, template.df, PUBLISHED_MAX_STAT_DISPLAY)),
        race=race,
        job=template.job if template.job is not None else rng.randrange(10),
        character_class=template.character_class,
        special=template.special if template.special is not None else rng.randrange(100),
        speed=template.speed,
    )


_FIGHTERS: Final = tuple(race for race in Race if race.is_fighter)


def _pick(rng: random.Random, constraint: Constraint, ceiling: int) -> int:
    """Draw one admissible display value from a constraint."""
    values = list(constraint.values(step=DISPLAY_SCALE, ceiling=ceiling))
    return rng.choice(values) if values else 0


def _pick_hp(rng: random.Random, constraint: Constraint) -> int:
    """Draw one admissible hit point value, honouring the marker grid above 20000."""
    values = [
        value
        for value in constraint.values(step=DISPLAY_SCALE, ceiling=MAX_HP_DISPLAY)
        if value < HIGH_HP_DISPLAY or value % 1000 == MARKER_HP_REMAINDER
    ]
    return rng.choice(values) if values else 0


def _reason(produced: int, requested: int, attempts: int, budget: int) -> str:
    """Explain a batch that could not be filled."""
    if produced >= requested:
        return ""
    return (
        f"produced {produced} of {requested} distinct cards after {attempts} attempts "
        f"against a budget of {budget}; the requested constraints admit too few "
        f"distinct barcodes"
    )
