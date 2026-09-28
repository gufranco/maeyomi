"""Read and build barcodes the way Barcode Battler Senki reads them.

Epoch's Conveni Wars Barcode Battler Senki, a Super Famicom game of 1993,
takes its cards through a Barcode Battler II on the Barcode Battler II
Interface, which passes on only the low four bits of each character. The game
decodes the digits in bank $C2 of its program, and it reads them the way
Barcode World does, confirmed against the game running in MAME on 211 codes
Barcode World was checked on, plus the codes below:

1. An EAN-8 arrives as thirteen digits led by five zeros, because the
   interface turns the Barcode Battler II's five spaces into zeros ($C0:A509).
2. An item read from the end keeps its strength's units digit below ten
   ($C2:2142), where Barcode World lets it reach 14.
3. The Interface's own box code opens the sound test in the two battle modes
   rather than making a card ($C2:1E75).

The Black Store of the scenario mode reads every card with other offsets
($C2:2CE6 and $C2:2DD4); that one shop is not modelled here.
"""

from typing import Final

from maeyomi.datach.game_card import DatachCard, GameKind
from maeyomi.decoder.validation import validate_barcode
from maeyomi.games.barcode_world import (
    BarcodeWorldOrder,
    C0Reading,
    build_c0,
    decode_c0,
    strongest_c0,
)
from maeyomi.models.device import Device

SENKI_READING: Final = C0Reading(Device.SENKI, "0", wraps_item_units=True)
SOUND_TEST: Final = 0
SOUND_TEST_CODE: Final = "490504035400"
"""Bank $C2 $1FC1: the first twelve digits of the Interface box's code."""

SenkiOrder = BarcodeWorldOrder


def decode_senki(code: str) -> DatachCard:
    """Read a barcode, raising a typed error when it is not a valid EAN."""
    normalised = validate_barcode(code)
    if normalised[:12] == SOUND_TEST_CODE:
        return DatachCard(normalised, Device.SENKI, GameKind.HIDDEN, SOUND_TEST)
    return decode_c0(normalised, SENKI_READING)


def build_senki(order: SenkiOrder) -> DatachCard | None:
    """The first code the game reads in place as the fighter ordered, or None."""
    return build_c0(order, SENKI_READING)


def strongest_senki() -> DatachCard:
    """A magician with HP, ST and DF at the most the game can read."""
    return strongest_c0(SENKI_READING)
