"""What the Barcode Battler II Double makes of one barcode."""

from dataclasses import dataclass
from enum import StrEnum

from maeyomi.double.abilities import DoubleAbility
from maeyomi.models.race import Race


class DoubleReading(StrEnum):
    """Which of the Double's three readings produced the card, in its own words."""

    FRONT = "front"
    FORTY_NINE = "49"
    SEVEN = "7"


@dataclass(frozen=True, slots=True)
class DoubleCard:
    """A fighter or an item as the Double reads it.

    The 7-read has no race or speed any source could establish, and the 49-read
    has no speed, so those fields are absent rather than guessed.
    """

    barcode: str
    reading: DoubleReading
    race: Race | None
    job: int
    hp: int
    st: int
    df: int
    special: DoubleAbility
    speed: int | None
    pp: int = 0
    mp: int = 0
