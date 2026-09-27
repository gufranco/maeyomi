"""The face of a card, in terms that no longer depend on which device reads it.

Every device family reads a barcode into its own result: the Barcode Battler II
into a character with a race and a special ability, other readers into other
shapes. The card drawing code only needs what goes on the paper: a coloured
band with a pictogram and two lines of words, the number tiles, and a special
power with its code, words and pictogram. `face_of` builds that from a result,
so adding a device adds a case here and leaves the drawing code alone.
"""

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial

from maeyomi.models.character import BarcodeBattlerCharacter
from maeyomi.rendering.ability_icons import AbilityIcon, ability_icon
from maeyomi.rendering.icons import RACE_COLOURS, Colour, draw_race_icon
from maeyomi.rendering.labels import Bilingual, class_label, panel_text, race_label
from maeyomi.rendering.stat_tiles import StatTile, stat_tiles

BandIcon = Callable[..., None]


@dataclass(frozen=True, slots=True)
class CardFace:
    """Everything a card prints apart from its name and its barcode."""

    band_colour: Colour
    band_icon: BandIcon
    kind: Bilingual
    detail: Bilingual
    tiles: tuple[StatTile, ...]
    power_code: int
    power_text: Bilingual
    power_icon: AbilityIcon


def face_of(character: BarcodeBattlerCharacter) -> CardFace:
    """The face of a Barcode Battler II card."""
    race = character.race
    return CardFace(
        band_colour=RACE_COLOURS[race],
        band_icon=partial(draw_race_icon, race=race),
        kind=race_label(race),
        detail=class_label(character.character_class),
        tiles=stat_tiles(character),
        power_code=character.special.code,
        power_text=panel_text(character),
        power_icon=ability_icon(character.special),
    )
