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
from maeyomi.datach.dbz import DbzCard, DbzKind
from maeyomi.datach.dbz_names import fighter_name, item_entry
from maeyomi.double.card import DoubleCard
from maeyomi.generator.carried import Carried, carried
from maeyomi.models.character import BarcodeBattlerCharacter
from maeyomi.models.character_class import CharacterClass
from maeyomi.models.generated_card import CardResult
from maeyomi.models.race import Race
from maeyomi.rendering.ability_icons import (
    AbilityIcon,
    Glyph,
    ability_icon,
    dbz_item_icon,
    double_icon,
    flag_icon,
)
from maeyomi.rendering.icons import (
    RACE_COLOURS,
    UNKNOWN_KIND_COLOUR,
    Colour,
    draw_race_icon,
    draw_unknown_kind,
)
from maeyomi.rendering.labels import (
    DBZ_EFFECT,
    DBZ_FIGHTER,
    DBZ_MOVES,
    ITEM_CARD,
    UNKNOWN_FIGHTER,
    UNKNOWN_KIND,
    UNKNOWN_POWER,
    Bilingual,
    class_label,
    dbz_level_text,
    double_class_label,
    panel_text,
    race_label,
)
from maeyomi.rendering.stat_tiles import StatTile, stat_tiles, tiles_for, tiles_from

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
    power_heading: Bilingual | None = None


def face_of(result: CardResult) -> CardFace:
    """The face of a card, whichever device reads it."""
    if isinstance(result, FirstBattlerCard):
        return _first_battler_face(result)
    if isinstance(result, DoubleCard):
        return _double_face(result)
    if isinstance(result, DbzCard):
        return _dbz_item_face(result) if result.kind is DbzKind.ITEM else _dbz_fighter_face(result)
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


def _dbz_fighter_face(card: DbzCard) -> CardFace:
    """The face of a Datach Dragon Ball Z fighter: its name, three numbers and its level."""
    name = fighter_name(card.character)
    return CardFace(
        band_colour=RACE_COLOURS[Race.HUMAN],
        band_icon=partial(draw_race_icon, race=Race.HUMAN),
        kind=UNKNOWN_FIGHTER if name is None else Bilingual(*name),
        detail=DBZ_FIGHTER,
        tiles=tiles_from(
            (
                ("HP", Carried.HP, card.hp),
                ("BP", Carried.ST, card.bp),
                ("DP", Carried.DF, card.dp),
            )
        ),
        power_code=card.level or 0,
        power_text=dbz_level_text(card.level),
        power_icon=AbilityIcon(Glyph.NONE if card.level is None else Glyph.CROWN),
        power_heading=DBZ_MOVES,
    )


def _dbz_item_face(card: DbzCard) -> CardFace:
    """The face of a Datach Dragon Ball Z item: its name and what it does, with no numbers."""
    entry = item_entry(card.character)
    return CardFace(
        band_colour=RACE_COLOURS[Race.SUPPORT_ITEM],
        band_icon=partial(draw_race_icon, race=Race.SUPPORT_ITEM),
        kind=UNKNOWN_KIND if entry is None else Bilingual(entry.english, entry.japanese),
        detail=ITEM_CARD,
        tiles=(),
        power_code=0,
        power_text=UNKNOWN_POWER
        if entry is None
        else Bilingual(entry.effect, entry.effect_japanese),
        power_icon=dbz_item_icon(card.character),
        power_heading=DBZ_EFFECT,
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
