"""One finished card: a name, the barcode, and what the barcode decodes to.

A card is generic over the device that reads it. Left unparameterised it is a
Barcode Battler II card, which is what every surface built before the other
devices expects; the renderer takes any `CardResult`.
"""

from dataclasses import dataclass

from maeyomi.bb1.card import FirstBattlerCard
from maeyomi.double.card import DoubleCard
from maeyomi.models.character import BarcodeBattlerCharacter

type CardResult = BarcodeBattlerCharacter | FirstBattlerCard | DoubleCard


@dataclass(frozen=True, slots=True)
class GeneratedCard[
    T: (BarcodeBattlerCharacter, FirstBattlerCard, DoubleCard) = BarcodeBattlerCharacter
]:
    """A card ready to render, whose barcode has already been decoded back."""

    name: str
    barcode: str
    character: T


type AnyCard = (
    GeneratedCard[BarcodeBattlerCharacter]
    | GeneratedCard[FirstBattlerCard]
    | GeneratedCard[DoubleCard]
)
