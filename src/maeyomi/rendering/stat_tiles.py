"""The number tiles a card prints: one per number its kind of card carries.

A fighter prints health, attack and defence. An item prints the one number it
carries, so a herb item shows its herbs rather than three zeros, and an
information item prints no tile at all.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Final

from maeyomi.generator.carried import Carried, carried
from maeyomi.models.character import BarcodeBattlerCharacter
from maeyomi.rendering.icons import draw_crystal, draw_heart, draw_leaf, draw_shield, draw_sword

IconDrawer = Callable[..., None]


@dataclass(frozen=True, slots=True)
class StatTile:
    """One number to print, the key its label and colours are filed under, and its icon."""

    key: str
    value: int
    icon: IconDrawer


_ICONS: Final[dict[Carried, IconDrawer]] = {
    Carried.HP: draw_heart,
    Carried.ST: draw_sword,
    Carried.DF: draw_shield,
    Carried.PP: draw_leaf,
    Carried.MP: draw_crystal,
}


def stat_tiles(character: BarcodeBattlerCharacter) -> tuple[StatTile, ...]:
    """The tiles for a Barcode Battler II card, in the order they print."""
    return tiles_for(carried(character.race, character.job), character)


def tiles_for(fields: Sequence[Carried], values: object) -> tuple[StatTile, ...]:
    """One tile per field, reading each value off the object by its field name."""
    return tuple(
        StatTile(key=field.name, value=getattr(values, field.value), icon=_ICONS[field])
        for field in fields
    )
