"""Read and build barcodes the way Datach Ultraman Club reads them.

Derived from the game's program, bank 13, and confirmed against the game
running in MAME on its analyzer screen, the third entry of the title menu:

1. The ten digits scatter into the 40-bit stream through `PERMUTATION`.
2. The top 6 bits pick the type through the slot table at $B6B9; 32 and up
   are items.
3. PW, ST and SP follow in that order, each as 4 bits picking tens from $B699
   and 4 bits picking units from $B6A9, in hundreds.

The first two digits and the check digit are never read, and the last 10 bits
of the stream are unused, so every card has many barcodes. A card built here
takes the first one that every Datach reader accepts.
"""

import itertools
from collections.abc import Iterator
from dataclasses import dataclass
from itertools import accumulate
from typing import Final

from maeyomi.datach.game_card import DatachCard, GameKind, GameStat, required
from maeyomi.datach.game_reader import printable
from maeyomi.datach.stream import code_for, eight_bit, field, stream_of
from maeyomi.datach.ultraman_tables import ADDENDS, FIRST_ITEM, PERMUTATION, TENS, TYPE_SLOTS
from maeyomi.decoder.validation import validate_barcode
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device

STAT_KEYS: Final = ("PW", "UST", "USP")
HUNDRED: Final = 100
TYPE_BITS: Final = 6
PICK_BITS: Final = 4
STAT_BITS: Final = 8
TYPE_SHIFT: Final = 34
STAT_SHIFTS: Final = (26, 18, 10)
STREAM_LIMIT: Final = 2000
PREFIXES: Final = tuple(f"{number:02d}" for number in range(100))
STRONGEST_TYPE: Final = 0
STRONGEST_HUNDREDS: Final = 99


@dataclass(frozen=True, slots=True)
class UltramanOrder:
    """The type wanted, or any, and what each of PW, ST and SP must be."""

    ident: int | None
    pw: Constraint
    st: Constraint
    sp: Constraint


def decode_ultraman(code: str) -> DatachCard:
    """Read a barcode, raising a typed error when it is not a valid EAN."""
    normalised = validate_barcode(code)
    stream = stream_of(normalised, PERMUTATION)
    ident = _type_of(field(stream, 0, TYPE_BITS))
    stats = tuple(
        GameStat(key, _hundreds(stream, TYPE_BITS + STAT_BITS * index) * HUNDRED)
        for index, key in enumerate(STAT_KEYS)
    )
    kind = GameKind.ITEM if ident >= FIRST_ITEM else GameKind.FIGHTER
    return DatachCard(normalised, Device.DATACH_ULTRAMAN, kind, ident, stats)


def build_ultraman(order: UltramanOrder) -> DatachCard | None:
    """The first card every Datach reader accepts that the game reads as ordered."""
    streams = itertools.islice(_streams(order), STREAM_LIMIT)
    codes = (code for stream in streams for code in codes_of(stream))
    return next(map(decode_ultraman, codes), None)


def strongest_ultraman(ident: int = STRONGEST_TYPE) -> DatachCard:
    """A card whose PW, ST and SP are all the highest the game can read."""
    top = Constraint.exactly(STRONGEST_HUNDREDS * HUNDRED)
    card = build_ultraman(UltramanOrder(ident, top, top, top))
    return required(
        card, f"no printable Ultraman Club card is type {ident} at the top of all three"
    )


def _type_of(value: int) -> int:
    """The type whose run of slots holds a 6-bit value."""
    ends = accumulate(count for _, count in TYPE_SLOTS)
    return next(ident for (ident, _), end in zip(TYPE_SLOTS, ends, strict=True) if value < end)


def _hundreds(stream: int, start: int) -> int:
    """One number in hundreds: tens from the first four bits, units from the next four."""
    tens = TENS[field(stream, start, PICK_BITS)]
    return tens + ADDENDS[field(stream, start + PICK_BITS, PICK_BITS)]


def _streams(order: UltramanOrder) -> Iterator[int]:
    """Every stream that reads as the order, type first, then PW, ST and SP."""
    sixes = [value for value in range(1 << TYPE_BITS) if order.ident in {None, _type_of(value)}]
    picks = [list(_picks(constraint)) for constraint in (order.pw, order.st, order.sp)]
    for six, *stats in itertools.product(sixes, *picks):
        yield six << TYPE_SHIFT | sum(
            pick << shift for pick, shift in zip(stats, STAT_SHIFTS, strict=True)
        )


def _picks(constraint: Constraint) -> Iterator[int]:
    """Every 8-bit field whose number in hundreds the constraint admits."""
    for tens, units in itertools.product(range(len(TENS)), range(len(ADDENDS))):
        if constraint.admits((TENS[tens] + ADDENDS[units]) * HUNDRED):
            yield tens << PICK_BITS | units


def codes_of(stream: int) -> Iterator[str]:
    """Every code for the stream, with and without an 8, that every reader accepts."""
    for extra, prefix in itertools.product((0, eight_bit(PERMUTATION)), PREFIXES):
        code = code_for(stream | extra, PERMUTATION, prefix)
        if code is not None and printable(code):
            yield code
