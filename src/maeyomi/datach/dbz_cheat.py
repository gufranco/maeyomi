"""The strongest Datach Dragon Ball Z card, for the cheat code.

Every stat is a sum picked by nine bits, but not every choice can be printed:
the stream they form must come back out of the digit scattering as ten decimal
digits. The search walks HP, BP and DP choices from the strongest down and
stops each branch as soon as it cannot beat the best total found, so it finds
the strongest printable card without trying every one.

The character is Super Saiyan Goku at the top level, which the game reaches
from Goku's slots once the numbers pass its own thresholds. The result beats
the fixed card the game hides in its program.
"""

from functools import cache
from typing import Final

from maeyomi.datach.dbz import DbzCard, DbzKind
from maeyomi.datach.dbz_names import ITEMS
from maeyomi.datach.dbz_solve import DbzRequest, solve_dbz, strongest_dbz
from maeyomi.generator.cheat import DEFAULT_CHEAT_NAME
from maeyomi.models.generated_card import GeneratedCard

CHEAT_CHARACTER: Final = 9
TOP_LEVEL: Final = 3
CHEAT_ITEMS: Final = (33, 35, 39, 43, 45, 71)
"""Full recovery, +6000 to all three, +12000 HP, +12000 BP, +50% BP and DP, level 4 moves."""


def strongest_dbz_card(name: str = DEFAULT_CHEAT_NAME) -> GeneratedCard[DbzCard]:
    """The strongest printable Super Saiyan Goku at the top level."""
    card = strongest_fighter(CHEAT_CHARACTER, TOP_LEVEL)
    return GeneratedCard(name=name, barcode=card.barcode, character=card)


@cache
def strongest_fighter(character: int, level: int) -> DbzCard:
    """The strongest printable fighter, searched once per process because the walk is long."""
    card = strongest_dbz(DbzRequest(character=character, level=level))
    if card is None:
        message = f"no printable Dragon Ball Z card is character {character} at level {level}"
        raise RuntimeError(message)
    return card


def strongest_dbz_items() -> tuple[GeneratedCard[DbzCard], ...]:
    """One item for each strongest effect, named as the game names it."""
    return tuple(item_card(identifier) for identifier in CHEAT_ITEMS)


def item_card(identifier: int) -> GeneratedCard[DbzCard]:
    """A verified barcode for one item."""
    card = solve_dbz(DbzRequest(character=identifier, kind=DbzKind.ITEM)).card
    if card is None:
        message = f"Dragon Ball Z item {identifier} cannot be built"
        raise RuntimeError(message)
    return GeneratedCard(name=ITEMS[identifier].english, barcode=card.barcode, character=card)
