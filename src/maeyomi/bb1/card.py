"""What the first Barcode Battler makes of one barcode.

It differs from the Barcode Battler II's result in three ways that matter on a
printed card. Every fighter is a warrior, so there is no class to print. The
two-digit code is a flag from its own table, not a II special ability. And an
enemy read from the back has no race and no DX that any source could find, so
those fields are absent rather than guessed.
"""

from dataclasses import dataclass

from maeyomi.bb1.flags import Flag
from maeyomi.models.race import Race
from maeyomi.models.read_type import ReadType


@dataclass(frozen=True, slots=True)
class FirstBattlerCard:
    """A fighter, an enemy or an item as the first Barcode Battler reads it."""

    barcode: str
    read_type: ReadType
    race: Race | None
    job: int
    hp: int
    st: int
    df: int
    flag: Flag
    dx: int | None
