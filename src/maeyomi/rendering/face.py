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

from maeyomi.bb1.card import FirstBattlerCard
from maeyomi.double.card import DoubleCard
from maeyomi.generator.carried import Carried, carried
from maeyomi.models.character import BarcodeBattlerCharacter
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.generated_card import CardResult
from maeyomi.models.race import Race
from maeyomi.rendering.ability_icons import AbilityIcon, ability_icon, double_icon, flag_icon
from maeyomi.rendering.icons import (
    RACE_COLOURS,
    UNKNOWN_KIND_COLOUR,
    Colour,
    draw_race_icon,
    draw_unknown_kind,
)
from maeyomi.rendering.labels import (
    ITEM_CARD,
    UNKNOWN_FIGHTER,
    UNKNOWN_KIND,
    Bilingual,
    class_label,
    double_class_label,
    panel_text,
    race_label,
)
from maeyomi.rendering.stat_tiles import StatTile, stat_tiles, tiles_for

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


def face_of(result: CardResult) -> CardFace:
    """The face of a card, whichever device reads it."""
    if isinstance(result, FirstBattlerCard):
        return _first_battler_face(result)
    if isinstance(result, DoubleCard):
        return _double_face(result)
    return _second_battler_face(result)


def _second_battler_face(character: BarcodeBattlerCharacter) -> CardFace:
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


def _first_battler_face(card: FirstBattlerCard) -> CardFace:
    """The face of a first Barcode Battler card, whose fighters are all warriors."""
    flag = card.flag
    return CardFace(
        band_colour=UNKNOWN_KIND_COLOUR if card.race is None else RACE_COLOURS[card.race],
        band_icon=draw_unknown_kind
        if card.race is None
        else partial(draw_race_icon, race=card.race),
        kind=UNKNOWN_KIND if card.race is None else race_label(card.race),
        detail=_first_battler_detail(card.race),
        tiles=tiles_for(_first_battler_fields(card.race), card),
        power_code=flag.code,
        power_text=Bilingual(flag.description, flag.japanese),
        power_icon=flag_icon(flag),
    )


def _double_face(card: DoubleCard) -> CardFace:
    """The face of a Double card, with the Double's classes and power table."""
    special = card.special
    fields = (
        (Carried.HP, Carried.ST, Carried.DF) if card.race is None else carried(card.race, card.job)
    )
    return CardFace(
        band_colour=UNKNOWN_KIND_COLOUR if card.race is None else RACE_COLOURS[card.race],
        band_icon=draw_unknown_kind
        if card.race is None
        else partial(draw_race_icon, race=card.race),
        kind=UNKNOWN_FIGHTER if card.race is None else race_label(card.race),
        detail=ITEM_CARD
        if card.race is not None and not card.race.is_fighter
        else double_class_label(card.job),
        tiles=tiles_for(fields, card),
        power_code=special.code,
        power_text=Bilingual(special.description, special.japanese),
        power_icon=double_icon(special),
    )


def _first_battler_detail(race: Race | None) -> Bilingual:
    """Warrior for a fighter or an enemy, item card for an item."""
    if race is None or race.is_fighter:
        return class_label(CharacterClass.WARRIOR)
    return ITEM_CARD


def _first_battler_fields(race: Race | None) -> tuple[Carried, ...]:
    """What a first Barcode Battler card carries: its helper item only ever gives health."""
    if race is None or race.is_fighter:
        return (Carried.HP, Carried.ST, Carried.DF)
    if race.is_weapon:
        return (Carried.ST,)
    if race.is_armour:
        return (Carried.DF,)
    return (Carried.HP,)
