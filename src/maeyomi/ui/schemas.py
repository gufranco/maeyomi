"""Request and response shapes for the local web interface.

Every field arrives as text or a small integer and is parsed into the same
typed request the command line builds, so both surfaces go through one solver.

The choice lists the page renders come from these views rather than being
retyped in the page, so a race or an ability added to the enums appears in the
interface without a second edit.
"""

from pydantic import BaseModel, ConfigDict, Field

from maeyomi.models.character import BarcodeBattlerCharacter
from maeyomi.models.race import Race
from maeyomi.models.special_ability import FIRST_C1_C2_ONLY_CODE, SpecialAbility
from maeyomi.rendering.labels import (
    RACE_DESCRIPTIONS,
    RACE_DESCRIPTIONS_JA,
    race_label,
)


class CardSpec(BaseModel):
    """One card asked for over HTTP."""

    model_config = ConfigDict(populate_by_name=True)

    name: str = "Card"
    hp: str | None = None
    st: str | None = None
    df: str | None = None
    race: str | None = None
    character_class: str | None = Field(default=None, alias="class")
    job: int | None = Field(default=None, ge=0, le=9)
    speed: int | None = Field(default=None, ge=0, le=9)
    ability: int | None = Field(default=None, ge=0, le=99)
    nearest: bool = False
    back_read: bool = Field(default=False, alias="backRead")


class RandomSpec(CardSpec):
    """A batch of random cards asked for over HTTP."""

    count: int = Field(default=9, ge=1, le=200)
    seed: int | None = None
    device: str = "bb2"


class SheetSpec(BaseModel):
    """A sheet built from an explicit list of cards."""

    cards: list[CardSpec]


class PreviewSpec(BaseModel):
    """A barcode to draw a single card for, read the way the chosen device reads it."""

    barcode: str
    name: str = "Card"
    device: str = "bb2"


class BarcodeSheetSpec(BaseModel):
    """A sheet of cards that already have barcodes, so nothing is solved."""

    cards: list[PreviewSpec]


class ProductView(BaseModel):
    """One real product, and what the device makes of its barcode."""

    barcode: str
    name: str
    brand: str
    kind: str
    label: str
    label_ja: str
    stats: str
    stats_ja: str
    effect: str
    effect_ja: str
    readable: bool = True
    note: str = ""
    note_ja: str = ""


class ProductShelf(BaseModel):
    """The products that matched, and how many are on the shelf altogether."""

    products: list[ProductView]
    total: int
    source: str
    licence: str


class LookupResult(BaseModel):
    """What the open product database calls a barcode, when it knows."""

    barcode: str
    name: str | None = None


class OfficialSpec(BaseModel):
    """One official set, or every set when none is named."""

    official_set: str | None = Field(default=None, alias="set")
    device: str = "bb2"


class OfficialSetView(BaseModel):
    """One official card list as the page shows it."""

    key: str
    english: str
    japanese: str
    count: int


class RejectedView(BaseModel):
    """A transcription that was left out, and why."""

    barcode: str
    name: str
    reason: str


class OfficialCatalogue(BaseModel):
    """Every official set, the printable total, and what was left out."""

    sets: list[OfficialSetView]
    total: int
    rejected: list[RejectedView]


class AbilityView(BaseModel):
    """One row of the published ability table."""

    code: int
    description: str
    description_ja: str = ""
    usable_in_battle: bool = True

    @classmethod
    def of(cls, ability: SpecialAbility) -> AbilityView:
        """Build the view, flagging the codes an ordinary battle ignores."""
        return cls(
            code=ability.code,
            description=ability.description,
            description_ja=ability.japanese,
            usable_in_battle=ability.code < FIRST_C1_C2_ONLY_CODE,
        )


class RaceView(BaseModel):
    """One kind of card, named for someone who has not read the manual."""

    name: str
    label: str
    label_ja: str
    description: str
    description_ja: str
    is_fighter: bool

    @classmethod
    def of(cls, race: Race) -> RaceView:
        """Build the view from the race enum."""
        return cls(
            name=race.name.lower(),
            label=race_label(race).english,
            label_ja=race_label(race).japanese,
            description=RACE_DESCRIPTIONS[race],
            description_ja=RACE_DESCRIPTIONS_JA[race],
            is_fighter=race.is_fighter,
        )


class CharacterView(BaseModel):
    """A decoded character rendered for the browser."""

    barcode: str
    read_type: str
    hp: int
    st: int
    df: int
    battle_st: int | None
    battle_df: int | None
    race: str
    job: int
    character_class: str | None
    speed: int | None
    pp: int
    mp: int
    special: AbilityView
    sign_is_volatile: bool

    @classmethod
    def of(cls, character: BarcodeBattlerCharacter) -> CharacterView:
        """Build the view from a decoded character."""
        character_class = character.character_class
        return cls(
            barcode=character.barcode,
            read_type=character.read_type.value,
            hp=character.hp,
            st=character.st,
            df=character.df,
            battle_st=character.battle_st,
            battle_df=character.battle_df,
            race=character.race.name.lower(),
            job=character.job,
            character_class=character_class.value if character_class else None,
            speed=character.speed,
            pp=character.pp,
            mp=character.mp,
            special=AbilityView.of(character.special),
            sign_is_volatile=character.sign_is_volatile,
        )


class GenerateResult(BaseModel):
    """What one solved request produced."""

    barcode: str
    character: CharacterView
    mismatches: list[str]
    searched: int
    is_exact: bool = True
    distance: int = 0
    differences: list[str] = Field(default_factory=list)
    differences_ja: list[str] = Field(default_factory=list)


class SheetPreview(BaseModel):
    """Page images for a sheet, or one card's image when only one card is asked for.

    `single` says the one image is a card drawn alone rather than a page.
    """

    count: int
    pages: list[str]
    single: bool


class DeviceCardSpec(CardSpec):
    """One card asked for over HTTP for any device, with the fields only a game reads."""

    device: str = "bb2"
    character: str | None = None
    level: int | None = Field(default=None, ge=0, le=3)
    picks: dict[str, int] = Field(default_factory=dict)


class DeviceCheatSpec(BaseModel):
    """The device whose strongest card is wanted, and the name to print on it."""

    device: str = "bb2"
    name: str | None = None
    kind: str | None = None


class CheatKindView(BaseModel):
    """One kind of cheat card a device offers, named in both languages."""

    key: str
    english: str
    japanese: str
    default_name: str


class DeviceView(BaseModel):
    """One device or game, and which parts of the card maker apply to it."""

    key: str
    english: str
    japanese: str
    group: str
    platform: str
    fields: list[str]
    hp_max: int
    st_max: int
    df_max: int
    steps: list[int]
    stat_keys: list[str]
    sheet_fields: list[str]
    ranges: list[list[int]]
    back_ranges: list[list[int]] | None
    cheat_kinds: list[CheatKindView]


class FactView(BaseModel):
    """One line of what a card is, in both languages."""

    label: str
    label_ja: str
    value: str
    value_ja: str


class DeviceReading(BaseModel):
    """A barcode as one device reads it, and whether it is exactly what was asked for.

    `companion` is the second card's barcode for a game that reads cards in pairs,
    and `cards` every barcode of a cheat kind that prints more than one card.
    """

    name: str = ""
    barcode: str
    facts: list[FactView]
    is_exact: bool = True
    companion: str | None = None
    cards: list[str] = Field(default_factory=list)


class DbzChoiceView(BaseModel):
    """One fighter or item Datach Dragon Ball Z can produce."""

    id: int
    kind: str
    english: str
    japanese: str


class OptionView(BaseModel):
    """One value a card's choice can take."""

    value: int
    english: str
    japanese: str


class PickView(BaseModel):
    """A choice a game's card offers beside its numbers."""

    key: str
    english: str
    japanese: str
    options: list[OptionView]
