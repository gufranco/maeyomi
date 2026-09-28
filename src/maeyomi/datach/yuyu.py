"""Read and build barcodes the way Datach Yu Yu Hakusho reads them.

Derived from the game's program, bank 12 at $8BBA and bank 9 at $A8BC, and
confirmed against the game running in MAME on its analyzer, コエンマの判決:

1. The ten digits scatter into the 40-bit stream through `PERMUTATION`.
2. One whole stream is the game's secret and reads as the hidden SP Toguro
   with every technique.
3. Otherwise the top 6 bits pick a character or, from 32 up, an item, and the
   next 4 are a mask: a character can use the technique of each bit that is
   set, and an item's level is the mask's two low bits.

A character's HP and SP come from its own record, so no barcode changes them,
and the rest of the stream is never read. A card built here takes the first
barcode every Datach reader accepts.
"""

import itertools
from collections.abc import Iterator
from dataclasses import dataclass
from itertools import accumulate
from typing import Final

from maeyomi.datach.game_card import (
    DatachCard,
    GameKind,
    GameOption,
    GamePick,
    GameStat,
    required,
)
from maeyomi.datach.game_reader import printable
from maeyomi.datach.stream import code_for, eight_bit, field, printable_mask, stream_of
from maeyomi.datach.yuyu_names import CHARACTERS, ITEMS, TECHNIQUE_NAMES, bonus_text
from maeyomi.datach.yuyu_tables import (
    FIRST_ITEM,
    ITEM_BONUSES,
    NO_BONUS,
    NUMBERS,
    PERMUTATION,
    SECRET_CHARACTER,
    SECRET_MASK,
    SECRET_STREAM,
    TECHNIQUES,
    TYPE_SLOTS,
)
from maeyomi.decoder.validation import validate_barcode
from maeyomi.models.device import Device

MOVES_KEY: Final = "moves"
LEVEL_KEY: Final = "level"
TYPE_BITS: Final = 6
MASK_BITS: Final = 4
TYPE_SHIFT: Final = 34
MASK_SHIFT: Final = 30
LEVELS: Final = 4
LEVEL_MASK: Final = 0b11
FREE_BITS: Final = 30
FREE_TRIES: Final = 64
FREE_STEP: Final = 0x2F1A3B7
PREFIXES: Final = tuple(f"{number:02d}" for number in range(100))
NO_TECHNIQUE: Final = ("No technique", "わざ なし")


@dataclass(frozen=True, slots=True)
class YuYuOrder:
    """The card wanted, or any character, and its techniques or its level."""

    ident: int | None
    picks: tuple[tuple[str, int], ...] = ()


def decode_yuyu(code: str) -> DatachCard:
    """Read a barcode, raising a typed error when it is not a valid EAN."""
    normalised = validate_barcode(code)
    stream = stream_of(normalised, PERMUTATION)
    if stream == SECRET_STREAM:
        return _fighter(normalised, SECRET_CHARACTER, SECRET_MASK, GameKind.HIDDEN)
    ident = _type_of(field(stream, 0, TYPE_BITS))
    mask = field(stream, TYPE_BITS, MASK_BITS)
    if ident >= FIRST_ITEM:
        return _item(normalised, ident, mask)
    return _fighter(normalised, ident, mask, GameKind.FIGHTER)


def mask_of(card: DatachCard) -> int:
    """The four-bit mask a card was read with."""
    return card.traits[0]


def build_yuyu(order: YuYuOrder) -> DatachCard | None:
    """The first card every Datach reader accepts that the game reads as ordered."""
    codes = (code for stream in _streams(order) for code in codes_of(stream))
    return next(map(decode_yuyu, codes), None)


def strongest_yuyu() -> DatachCard:
    """The hidden SP Toguro, whose 9999 HP and SP no other card reaches."""
    card = build_yuyu(YuYuOrder(SECRET_CHARACTER))
    return required(card, "the hidden Yu Yu Hakusho card cannot be printed")


def picks_for(ident: int) -> tuple[GamePick, ...]:
    """A character's sets of techniques, or an item's levels; the rest offer nothing."""
    if ident in CHARACTERS and ident != SECRET_CHARACTER:
        options = tuple(
            GameOption(mask, *_technique_text(_techniques(ident, mask)))
            for mask in _distinct_masks(ident)
        )
        return (GamePick(MOVES_KEY, "Techniques", "わざ", options),)
    if ident in ITEMS and ITEM_BONUSES[ident - FIRST_ITEM][0][0] != NO_BONUS:
        levels = tuple(_level_option(ident, level) for level in range(LEVELS))
        return (GamePick(LEVEL_KEY, "Level", "レベル", levels),)
    return ()


def codes_of(stream: int) -> Iterator[str]:
    """Every code for the stream, with and without an 8, that every reader accepts."""
    for extra, prefix in itertools.product((0, eight_bit(PERMUTATION)), PREFIXES):
        code = code_for(stream | extra, PERMUTATION, prefix)
        if code is not None and printable(code):
            yield code


def _type_of(value: int) -> int:
    """The character or item whose run of slots holds a 6-bit value."""
    ends = accumulate(count for _, count in TYPE_SLOTS)
    return next(ident for (ident, _), end in zip(TYPE_SLOTS, ends, strict=True) if value < end)


def _techniques(ident: int, mask: int) -> tuple[int, ...]:
    """The techniques a character can use with a mask, in bit order."""
    return tuple(
        technique
        for bit, technique in enumerate(TECHNIQUES[ident])
        if mask >> bit & 1 and technique
    )


def _fighter(code: str, ident: int, mask: int, kind: GameKind) -> DatachCard:
    """A character, with its fixed HP and SP and the techniques its mask allows."""
    hp, sp = NUMBERS[ident]
    stats = (GameStat("YHP", hp), GameStat("YSP", sp))
    return DatachCard(
        code, Device.DATACH_YUYU, kind, ident, stats, (mask, *_techniques(ident, mask))
    )


def _item(code: str, ident: int, mask: int) -> DatachCard:
    """An item, with what its level adds, or nothing when it changes the rules instead."""
    hp, sp = ITEM_BONUSES[ident - FIRST_ITEM][mask & LEVEL_MASK]
    stats = () if hp == NO_BONUS else _nonzero((GameStat("YHP", hp), GameStat("YSP", sp)))
    return DatachCard(code, Device.DATACH_YUYU, GameKind.ITEM, ident, stats, (mask,))


def _nonzero(stats: tuple[GameStat, ...]) -> tuple[GameStat, ...]:
    """The numbers an item really adds."""
    return tuple(stat for stat in stats if stat.value)


def _distinct_masks(ident: int) -> list[int]:
    """One mask per distinct set of techniques, the fullest first."""
    by_set: dict[tuple[int, ...], int] = {}
    for mask in range(1 << MASK_BITS):
        by_set.setdefault(_techniques(ident, mask), mask)
    return sorted(by_set.values(), key=lambda mask: (-len(_techniques(ident, mask)), mask))


def _technique_text(techniques: tuple[int, ...]) -> tuple[str, str]:
    """A set of techniques named in both languages."""
    if not techniques:
        return NO_TECHNIQUE
    names = [TECHNIQUE_NAMES[technique] for technique in techniques]
    return ", ".join(name for name, _ in names), "・".join(name for _, name in names)


def _level_option(ident: int, level: int) -> GameOption:
    """One level of an item, named by what it adds."""
    english, japanese = bonus_text(*ITEM_BONUSES[ident - FIRST_ITEM][level])
    return GameOption(
        level,
        f"Level {level + 1}: {english[0].lower()}{english[1:-1]}",
        f"レベル {level + 1}: {japanese}",
    )


def _streams(order: YuYuOrder) -> Iterator[int]:
    """Every stream the order allows: the secret alone for the hidden character."""
    if order.ident == SECRET_CHARACTER:
        return iter((SECRET_STREAM,))
    return _ordinary_streams(order)


def _ordinary_streams(order: YuYuOrder) -> Iterator[int]:
    """Every stream for a character or item named by its slots."""
    idents = [ident for ident in CHARACTERS if ident != SECRET_CHARACTER]
    wanted = dict(order.picks)
    for ident in idents if order.ident is None else [order.ident]:
        sixes = [value for value in range(1 << TYPE_BITS) if _type_of(value) == ident]
        for six, mask, tries in itertools.product(sixes, _masks(ident, wanted), range(FREE_TRIES)):
            free = tries * FREE_STEP % (1 << FREE_BITS) & printable_mask(PERMUTATION)
            yield six << TYPE_SHIFT | mask << MASK_SHIFT | free


def _masks(ident: int, wanted: dict[str, int]) -> list[int]:
    """The masks that give the techniques or the level asked for."""
    if ident >= FIRST_ITEM:
        level = wanted.get(LEVEL_KEY)
        return [mask for mask in range(1 << MASK_BITS) if level in {None, mask & LEVEL_MASK}]
    if MOVES_KEY in wanted:
        return [wanted[MOVES_KEY]] if wanted[MOVES_KEY] < 1 << MASK_BITS else []
    return _distinct_masks(ident)
