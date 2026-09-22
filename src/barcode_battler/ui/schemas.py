"""Request and response shapes for the local web interface.

Every field arrives as text or a small integer and is parsed into the same
typed request the command line builds, so both surfaces go through one solver.
"""

from pydantic import BaseModel, ConfigDict, Field

from barcode_battler.models.character import BarcodeBattlerCharacter


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


class RandomSpec(CardSpec):
    """A batch of random cards asked for over HTTP."""

    count: int = Field(default=9, ge=1, le=200)
    seed: int | None = None


class SheetSpec(BaseModel):
    """A sheet built from an explicit list of cards."""

    cards: list[CardSpec]


class AbilityView(BaseModel):
    """One row of the published ability table."""

    code: int
    description: str


class CharacterView(BaseModel):
    """A decoded character rendered for the browser."""

    barcode: str
    read_type: str
    hp: int
    st: int
    df: int
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
            race=character.race.name.lower(),
            job=character.job,
            character_class=character_class.value if character_class else None,
            speed=character.speed,
            pp=character.pp,
            mp=character.mp,
            special=AbilityView(
                code=character.special.code, description=character.special.description
            ),
            sign_is_volatile=character.sign_is_volatile,
        )


class GenerateResult(BaseModel):
    """What one solved request produced."""

    barcode: str
    character: CharacterView
    mismatches: list[str]
    searched: int
