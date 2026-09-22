"""One finished card: a name, the barcode, and what the barcode decodes to."""

from dataclasses import dataclass

from maeyomi.models.character import BarcodeBattlerCharacter


@dataclass(frozen=True, slots=True)
class GeneratedCard:
    """A card ready to render, whose barcode has already been decoded back."""

    name: str
    barcode: str
    character: BarcodeBattlerCharacter
