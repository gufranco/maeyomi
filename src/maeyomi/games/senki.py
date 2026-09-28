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

The Black Store of the scenario mode reads a code read from the end with
smaller offsets: 3 for strength and 5 for defence where the other screens add
5 and 7 ($C2:2CE6 for a fighter, $C2:2DD4 for anything else). Both are called
while $0D5F bit 4 is set ($C2:1FDB, $C2:2142), which a map event sets at
$C1:3B6C; that the event is the shop is read from the object it draws, not
from play. The scene rescaling at $C2:2806 is not modelled.
"""

from typing import Final

from maeyomi.datach.game_card import DatachCard, GameKind
from maeyomi.decoder.validation import validate_barcode
from maeyomi.games.barcode_world import (
    FIRST_ITEM_KIND,
    BarcodeWorldOrder,
    C0Reading,
    build_c0,
    decode_c0,
    reads_in_place,
    received_text,
    strongest_c0,
)
from maeyomi.models.device import Device

SENKI_READING: Final = C0Reading(Device.SENKI, "0", wraps_item_units=True)
SOUND_TEST: Final = 0
SOUND_TEST_CODE: Final = "490504035400"
"""Bank $C2 $1FC1: the first twelve digits of the Interface box's code."""

BLACK_STORE_ST_OFFSET: Final = 3
BLACK_STORE_DF_OFFSET: Final = 5
FIGHTER_HP_SHIFT: Final = 1
ITEM_HP_SHIFT: Final = 3
ITEM_TENS_SHIFT: Final = 2
DIGIT_MASK: Final = 0x0F
BYTE: Final = 0xFF

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


def black_store_stats(code: str) -> tuple[int, int, int] | None:
    """HP, ST and DF as the Black Store reads a code, or None when every screen reads it alike."""
    text = received_text(code, SENKI_READING)
    if reads_in_place(text):
        return None
    digits = [character & DIGIT_MASK for character in text]
    fighter = digits[12] < FIRST_ITEM_KIND
    hp_shift, tens_shift, st_base = (
        (FIGHTER_HP_SHIFT, 0, 2) if fighter else (ITEM_HP_SHIFT, ITEM_TENS_SHIFT, 1)
    )
    hp = (digits[11] >> hp_shift) * 100 + digits[10] * 10 + digits[9]
    st_tens = (_wrap(digits[10], BLACK_STORE_ST_OFFSET) >> tens_shift) + st_base
    st = (st_tens * 10 + _wrap(digits[9], BLACK_STORE_ST_OFFSET)) & BYTE
    df_tens = _wrap(digits[9], BLACK_STORE_DF_OFFSET) >> tens_shift
    return hp, st, df_tens * 10 + _wrap(digits[8], BLACK_STORE_DF_OFFSET)


def _wrap(digit: int, offset: int) -> int:
    """A digit plus the shop's offset, brought back under 10 once."""
    return (digit + offset) % 10
