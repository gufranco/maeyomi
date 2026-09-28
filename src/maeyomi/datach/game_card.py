"""The card a Datach game reads a barcode into, whichever game it is.

Dragon Ball Z keeps its own card type because it came first and its forms and
levels shape everything built on it. Every later Datach game reads into this
one: what the card is, its number in the game's own list, the numbers it
carries, and the extra choices the game read, such as a unit's weapons or a
fighter's techniques. Each game's module knows what those mean.
"""

from dataclasses import dataclass
from enum import StrEnum

from maeyomi.models.device import Device


class GameKind(StrEnum):
    """What a barcode becomes in a Datach game."""

    FIGHTER = "fighter"
    ITEM = "item"
    UNIT = "unit"
    COMMAND = "command"
    PLAYER = "player"
    TEAM = "team"
    HIDDEN = "hidden"


@dataclass(frozen=True, slots=True)
class GameStat:
    """One number a card carries, filed under the key its label is looked up by."""

    key: str
    value: int


@dataclass(frozen=True, slots=True)
class DatachCard:
    """A barcode as one Datach game reads it."""

    barcode: str
    game: Device
    kind: GameKind
    ident: int
    stats: tuple[GameStat, ...] = ()
    traits: tuple[int, ...] = ()

    def value(self, key: str) -> int:
        """The number filed under a key, or 0 when the card does not carry it."""
        return next((stat.value for stat in self.stats if stat.key == key), 0)
