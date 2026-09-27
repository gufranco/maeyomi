"""Read a barcode the way Datach Dragon Ball Z reads it.

Derived from the game's own program and confirmed against the game running in
MAME; the derivation is in the change that added this module, and the numbers
are in `dbz_tables.py`.

1. Ten digits are used: EAN-13 digits 3 to 12, or, for EAN-8, digits 3 to 8
   followed by digits 7 down to 4.
2. Each digit's four bits, lowest first, are scattered by `PERMUTATION` into a
   40-bit stream.
3. The stream is read from its top bit: 2 bits of kind, 8 of character, and for
   a fighter 3 of level, then HP, BP and DP, each as 4 bits of base, 4 of
   addend and 1 that adds 50 when it is clear. BP and DP are then halved.
4. The character field's remainder by 60 picks an id through the slot table.
5. A fighter whose numbers reach a form record of its own takes that form.

One stream is answered with a fixed card instead, the game's own secret.
"""

from dataclasses import dataclass
from enum import StrEnum
from itertools import accumulate
from typing import Final

from maeyomi.datach.dbz_reader import check_readable
from maeyomi.datach.dbz_tables import (
    ADDENDS,
    BASES,
    FIGHTER_SLOTS,
    FORMS,
    FORMS_BY_CHARACTER,
    ITEM_SLOTS,
    LEVELS,
    PERMUTATION,
    SECRET_CARD,
    SECRET_STREAM,
)
from maeyomi.decoder.check_digit import EAN_8_LENGTH
from maeyomi.decoder.validation import validate_barcode

STREAM_BITS: Final = 40
STREAM_BYTES: Final = 5
USED_DIGITS: Final = slice(2, 12)
ITEM_KIND: Final = 3
SLOT_COUNT: Final = 60
BONUS: Final = 50
UNIT: Final = 10
NO_LEVEL: Final = 255
STAT_FIELDS: Final = (4, 4, 1)


class DbzKind(StrEnum):
    """What a barcode becomes in the game."""

    FIGHTER = "fighter"
    ITEM = "item"
    HIDDEN = "hidden"


@dataclass(frozen=True, slots=True)
class DbzCard:
    """A fighter or an item as Datach Dragon Ball Z reads it."""

    barcode: str
    kind: DbzKind
    character: int
    level: int | None
    hp: int = 0
    bp: int = 0
    dp: int = 0


def decode_dbz(code: str) -> DbzCard:
    """Decode a barcode, raising a typed error when it is not a valid EAN."""
    normalised = validate_barcode(code)
    check_readable(normalised)
    stream = stream_of(normalised)
    if stream == SECRET_STREAM:
        return _hidden(normalised)
    bits = format(stream, f"0{STREAM_BITS}b")
    kind, character = int(bits[0:2], 2), int(bits[2:10], 2)
    if kind == ITEM_KIND:
        return DbzCard(normalised, DbzKind.ITEM, _slot(ITEM_SLOTS, character), None)
    return _fighter(normalised, bits, _slot(FIGHTER_SLOTS, character))


def stream_of(code: str) -> int:
    """The 40-bit stream the game builds from a validated code's digits."""
    stream = [0] * STREAM_BYTES
    for index, digit in enumerate(_used_digits(code)):
        for bit in range(4):
            if digit >> bit & 1:
                entry = PERMUTATION[index * 4 + bit]
                stream[entry >> 4] |= 1 << (entry & 0x0F)
    return int.from_bytes(bytes(stream), "big")


def _used_digits(code: str) -> list[int]:
    """The ten digits the game reads, with an EAN-8 code's mirrored tail."""
    digits = [int(character) for character in code]
    if len(digits) == EAN_8_LENGTH:
        digits = digits + digits[6:1:-1]
    return digits[USED_DIGITS]


def _slot(table: tuple[tuple[int, int], ...], field: int) -> int:
    """The id whose run of slots holds the field's remainder by 60."""
    position = field % SLOT_COUNT + 1
    ends = accumulate(count for _, count in table)
    return next(
        identifier for (identifier, _), end in zip(table, ends, strict=True) if position <= end
    )


def _fighter(code: str, bits: str, character: int) -> DbzCard:
    """Read level and the three numbers, then apply any form the numbers reach."""
    level = LEVELS[int(bits[10:13], 2)]
    units = [_stat(bits, 13 + 9 * index) for index in range(3)]
    hp, bp, dp = units[0], units[1] // 2, units[2] // 2
    return DbzCard(
        barcode=code,
        kind=DbzKind.FIGHTER,
        character=_form(character, (hp, bp, dp)),
        level=None if level == NO_LEVEL else level,
        hp=hp * UNIT,
        bp=bp * UNIT,
        dp=dp * UNIT,
    )


def _stat(bits: str, start: int) -> int:
    """One stat in units of 10: base, addend, and 50 more when its last bit is clear."""
    base = BASES[int(bits[start : start + 4], 2)]
    addend = ADDENDS[int(bits[start + 4 : start + 8], 2)]
    return base + addend + (BONUS if bits[start + 8] == "0" else 0)


def _form(character: int, units: tuple[int, int, int]) -> int:
    """The last form record of this character whose minimums the numbers meet."""
    for record in FORMS_BY_CHARACTER.get(character, ()):
        *minimums, form = FORMS[record]
        if all(value >= minimum for value, minimum in zip(units, minimums, strict=True)):
            character = form
    return character


def _hidden(code: str) -> DbzCard:
    """The fixed card the game gives for its secret stream, forms applied."""
    character, level, hp, bp, dp = SECRET_CARD
    return DbzCard(
        barcode=code,
        kind=DbzKind.HIDDEN,
        character=_form(character, (hp, bp, dp)),
        level=level,
        hp=hp * UNIT,
        bp=bp * UNIT,
        dp=dp * UNIT,
    )
