"""Read and build barcodes the way Datach J.League Super Top Players reads them.

Derived from the game's program, bank 12 at $A213, and confirmed against the
game running in MAME on its player directory, せんしゅめいかん:

1. The ten digits scatter into the 40-bit stream through `PERMUTATION`.
2. The low four bits of the first byte are the kind: 1 is a team's own card,
   anything else a player, through the table at $9161.
3. The low four bits of the second byte are the team, where 10 to 15 fold back
   onto 1 to 6, and of the third byte the player's slot, where 0 is 15.

Nothing else is read, so a card carries no numbers: it names a real player,
whose abilities are the game's own.
"""

import itertools
from collections.abc import Iterator
from typing import Final

from maeyomi.datach.game_card import DatachCard, GameKind
from maeyomi.datach.game_reader import printable
from maeyomi.datach.jleague_names import PLAYERS, TEAM_SLOTS, TEAMS, ident_of
from maeyomi.datach.stream import (
    STREAM_BITS,
    code_for,
    eight_bit,
    field,
    printable_mask,
    stream_of,
)
from maeyomi.decoder.validation import validate_barcode
from maeyomi.models.device import Device

PERMUTATION: Final = (
    0x15, 0x22, 0x35, 0x47, 0x10, 0x04, 0x32, 0x47, 0x03, 0x31,
    0x20, 0x47, 0x27, 0x02, 0x14, 0x47, 0x05, 0x13, 0x30, 0x47,
    0x21, 0x00, 0x26, 0x47, 0x33, 0x01, 0x37, 0x47, 0x17, 0x25,
    0x16, 0x47, 0x36, 0x11, 0x23, 0x47, 0x24, 0x34, 0x12, 0x47,
)  # fmt: skip
"""Bank 12 $A282: where each digit's four bits land in the 40-bit stream."""

TEAM_KIND: Final = 1
PLAYER_KIND: Final = 13
KIND_FIELD: Final = (4, 4)
TEAM_FIELD: Final = (12, 4)
SLOT_FIELD: Final = (20, 4)
FOLD_FROM: Final = 10
FOLD_BY: Final = 9
LAST_SLOT: Final = 15
FREE_TRIES: Final = 64
FREE_STEP: Final = 0x3B9ACA07
PREFIXES: Final = tuple(f"{number:02d}" for number in range(100))
NIBBLES: Final = 16


def decode_jleague(code: str) -> DatachCard:
    """Read a barcode, raising a typed error when it is not a valid EAN."""
    normalised = validate_barcode(code)
    stream = stream_of(normalised, PERMUTATION)
    team = field(stream, *TEAM_FIELD)
    team = team - FOLD_BY if team >= FOLD_FROM else team
    if field(stream, *KIND_FIELD) == TEAM_KIND:
        return DatachCard(normalised, Device.DATACH_JLEAGUE, GameKind.TEAM, ident_of(team, 0))
    slot = field(stream, *SLOT_FIELD) or LAST_SLOT
    return DatachCard(normalised, Device.DATACH_JLEAGUE, GameKind.PLAYER, ident_of(team, slot))


def build_jleague(ident: int | None) -> DatachCard | None:
    """The first card every Datach reader accepts for the team or player named, or any player."""
    wanted = [ident_of(*key) for key in PLAYERS] if ident is None else [ident]
    codes = (code for each in wanted for stream in _streams(each) for code in codes_of(stream))
    return next(map(decode_jleague, codes), None)


def codes_of(stream: int) -> Iterator[str]:
    """Every code for the stream, with and without an 8, that every reader accepts."""
    for extra, prefix in itertools.product((0, eight_bit(PERMUTATION)), PREFIXES):
        code = code_for(stream | extra, PERMUTATION, prefix)
        if code is not None and printable(code):
            yield code


def _streams(ident: int) -> Iterator[int]:
    """Every stream that reads as the card, its unread bits spread out."""
    team, slot = divmod(ident, TEAM_SLOTS)
    if team not in TEAMS:
        return iter(())
    kinds = [TEAM_KIND] if slot == 0 else [kind for kind in range(NIBBLES) if kind != TEAM_KIND]
    teams = [nibble for nibble in range(NIBBLES) if _team_of(nibble) == team]
    slots = (
        range(NIBBLES)
        if slot == 0
        else [nibble for nibble in (slot, 0) if (nibble or LAST_SLOT) == slot]
    )
    free = printable_mask(PERMUTATION) & ~_fields_mask()
    return (
        _put(kind, KIND_FIELD)
        | _put(nibble, TEAM_FIELD)
        | _put(place, SLOT_FIELD)
        | (tries * FREE_STEP & free)
        for kind, nibble, place, tries in itertools.product(kinds, teams, slots, range(FREE_TRIES))
    )


def _team_of(nibble: int) -> int:
    """The team a nibble names, 10 to 15 folding back onto 1 to 6."""
    return nibble - FOLD_BY if nibble >= FOLD_FROM else nibble


def _put(value: int, place: tuple[int, int]) -> int:
    """A field's value moved to its place in the stream."""
    start, width = place
    return value << (STREAM_BITS - start - width)


def _fields_mask() -> int:
    """Every bit the three read fields occupy."""
    return sum(
        _put((1 << width) - 1, (start, width))
        for start, width in (KIND_FIELD, TEAM_FIELD, SLOT_FIELD)
    )
