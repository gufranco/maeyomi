"""The strongest Barcode Battler II Double cards, for the cheat code.

The 7-read reaches 99900 attack and defence, which "BBIIダブルC0" on
barcodebattler.net states as the ceiling. The special power is two of the
health's digits, so the power decides how much health is left: power 29,
which halves the opponent's health, leaves 92900. It is the largest
documented effect that needs no guess, and a magician, job 9, carries it.

The items are Barcode Battler II item codes, which the Double reads with the
II's front read, each carrying a different power the Double's own table
documents without a question mark. No equipment table for the Double has been
published, so nothing here says which job can use which item.
"""

from typing import Final

from maeyomi.double.card import DoubleCard
from maeyomi.double.decode import decode_double
from maeyomi.double.solve import MAX_VALUE, highest_health_for, solve_double
from maeyomi.generator.cheat import DEFAULT_CHEAT_NAME
from maeyomi.generator.cheat_items import strongest_items
from maeyomi.generator.solve import solve
from maeyomi.models.card_request import CardRequest
from maeyomi.models.constraint import Constraint
from maeyomi.models.generated_card import GeneratedCard

OPPONENT_HEALTH_HALVED: Final = 29
MAGICIAN_JOB: Final = 9
ITEM_POWERS: Final[dict[str, int]] = {
    "Cheat Blade": 27,
    "Cheat Shield": 24,
    "Cheat Potion": 28,
    "Cheat Herbs": 35,
    "Cheat Crystal": 56,
}

type DoubleGeneratedCard = GeneratedCard[DoubleCard]


def strongest_double_card(name: str = DEFAULT_CHEAT_NAME) -> DoubleGeneratedCard:
    """Attack and defence at 99900, and the most health power 29 allows."""
    return build_double_card(
        CardRequest(
            name=name,
            hp=Constraint.exactly(highest_health_for(OPPONENT_HEALTH_HALVED)),
            st=Constraint.exactly(MAX_VALUE),
            df=Constraint.exactly(MAX_VALUE),
            job=MAGICIAN_JOB,
            special=OPPONENT_HEALTH_HALVED,
        )
    )


def strongest_double_items() -> tuple[DoubleGeneratedCard, ...]:
    """The II's strongest items, each re-powered from the Double's own table."""
    return tuple(build_double_card(_item_request(card)) for card in strongest_items())


def _item_request(card: GeneratedCard) -> CardRequest:
    """The same item as a II front read, carrying the Double's power."""
    character = card.character
    return CardRequest(
        name=card.name,
        hp=Constraint.exactly(character.hp),
        st=Constraint.exactly(character.st),
        df=Constraint.exactly(character.df),
        pp=Constraint.exactly(character.pp),
        mp=Constraint.exactly(character.mp),
        race=character.race,
        job=character.job,
        special=ITEM_POWERS[card.name],
    )


def build_double_card(request: CardRequest) -> DoubleGeneratedCard:
    """A 7-read card for a fighter or no race, otherwise a II front read, read as the Double.

    Raises when the request cannot be built, which the tests assert never
    happens for the cheat cards.
    """
    if request.race is None or request.race.is_fighter:
        outcome = solve_double(request)
        barcode = None if outcome.card is None else outcome.card.barcode
        reasons = outcome.blockers
    else:
        second = solve(request)
        barcode, reasons = second.barcode, second.blockers
    if barcode is None:
        message = f"{request.name} cannot be built: {'; '.join(reasons)}"
        raise RuntimeError(message)
    return GeneratedCard(name=request.name, barcode=barcode, character=decode_double(barcode))
