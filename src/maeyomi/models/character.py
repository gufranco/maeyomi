"""The fully decoded contents of one Barcode Battler II barcode.

The device stores HP, ST and DF internally in units of 100 and displays them
multiplied by 100, per barcodebattler.net/page01.htm and the caps applied in
`src/CreateFightingData.as` of finalfighter/BarcodeBattler2-Simulator (MIT).
This model carries the displayed values and exposes the internal units.
"""

from dataclasses import dataclass
from typing import Final

from maeyomi.models.character_class import CharacterClass
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType
from maeyomi.models.special_ability import SpecialAbility

DISPLAY_SCALE: Final = 100
HIGHEST_WARRIOR_JOB: Final = 6


@dataclass(frozen=True, slots=True)
class BarcodeBattlerCharacter:
    """A character or item as the device reads it from a barcode."""

    barcode: str
    read_type: ReadType
    race: Race
    job: int
    hp: int
    st: int
    df: int
    special: SpecialAbility
    speed: int | None = None
    pp: int = 0
    mp: int = 0
    sign_is_volatile: bool = False

    def __post_init__(self) -> None:
        """Reject stat values the device cannot represent."""
        for name in ("hp", "st", "df"):
            value: int = getattr(self, name)
            if value % DISPLAY_SCALE:
                message = f"{name} of {value} is not a multiple of {DISPLAY_SCALE}"
                raise ValueError(message)

    @property
    def is_fighter(self) -> bool:
        """Whether this barcode yields a playable character rather than an item."""
        return self.race.is_fighter

    @property
    def character_class(self) -> CharacterClass | None:
        """Warrior or magician for a fighter, None for an item."""
        if not self.is_fighter:
            return None
        if self.job <= HIGHEST_WARRIOR_JOB:
            return CharacterClass.WARRIOR
        return CharacterClass.MAGICIAN

    @property
    def hp_units(self) -> int:
        """HP in the device's internal units of 100."""
        return self.hp // DISPLAY_SCALE

    @property
    def st_units(self) -> int:
        """ST in the device's internal units of 100."""
        return self.st // DISPLAY_SCALE

    @property
    def df_units(self) -> int:
        """DF in the device's internal units of 100."""
        return self.df // DISPLAY_SCALE
