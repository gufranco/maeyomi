"""Read and build barcodes the way Datach SD Gundam Wars reads them.

Derived from the game's program, bank 13 at $9130 with its tables in the fixed
bank, and confirmed against the game running in MAME on its barcode lab:

1. The ten digits scatter into the 40-bit stream through `PERMUTATION`.
2. The first byte's low seven bits pick a slot: a unit, or from 101 up a
   command card, which carries nothing more.
3. A unit starts from its own record of HP, AP, DP, a hidden rank and CP, then
   5 bits add to HP, 5 to AP, 5 to DP, 3 to the rank and 2 to CP, and one bit
   each picks its short-range and its long-range weapon from its own pair.

Each number is the unit's base plus one of 32 bonuses, so a card asked for a
number between two of them gets the closest one; the registry says when a card
is not exactly what was asked. The lab never shows the rank, so nothing here
chooses it; the first printable one is kept.
"""

import itertools
from collections.abc import Iterator
from dataclasses import dataclass
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
from maeyomi.datach.sdgundam_names import COMMANDS, UNITS, WEAPONS, command_number
from maeyomi.datach.sdgundam_tables import (
    AP_BONUS,
    ARMS,
    BASES,
    CP_BONUS,
    DP_BONUS,
    FIRST_COMMAND,
    HP_BONUS,
    PERMUTATION,
    RANK_BONUS,
    SLOTS,
)
from maeyomi.datach.stream import STREAM_BITS, code_for, eight_bit, field, stream_of
from maeyomi.decoder.validation import validate_barcode
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device

SR_KEY: Final = "sr"
LR_KEY: Final = "lr"
CP_KEY: Final = "cp"
STAT_KEYS: Final = ("GHP", "AP", "GDP")
BONUSES: Final = (HP_BONUS, AP_BONUS, DP_BONUS)
SLOT_FIELD: Final = (1, 7)
TOP_FIELD: Final = (0, 1)
STAT_FIELDS: Final = ((8, 5), (13, 5), (18, 5))
RANK_FIELD: Final = (23, 3)
CP_FIELD: Final = (26, 2)
SR_FIELD: Final = (28, 1)
LR_FIELD: Final = (29, 1)
FREE_FIELD: Final = (8, 22)
FREE_TRIES: Final = 64
FREE_STEP: Final = 0x9E3779
STREAM_LIMIT: Final = 4000
PREFIXES: Final = tuple(f"{number:02d}" for number in range(100))
MASK_16: Final = 0xFFFF


@dataclass(frozen=True, slots=True)
class SdGundamOrder:
    """The card wanted, or any unit, what HP, AP and DP must be, and its other choices."""

    ident: int | None
    stats: tuple[Constraint, Constraint, Constraint]
    picks: tuple[tuple[str, int], ...] = ()


def decode_sdgundam(code: str) -> DatachCard:
    """Read a barcode, raising a typed error when it is not a valid EAN."""
    normalised = validate_barcode(code)
    stream = stream_of(normalised, PERMUTATION)
    slot = SLOTS[field(stream, *SLOT_FIELD)]
    if slot >= FIRST_COMMAND:
        return DatachCard(normalised, Device.DATACH_SD_GUNDAM, GameKind.COMMAND, slot)
    hp, ap, dp, rank, cp = BASES[slot]
    stats = tuple(
        GameStat(key, (base + bonus[field(stream, *place)]) & MASK_16)
        for key, base, bonus, place in zip(
            STAT_KEYS, (hp, ap, dp), BONUSES, STAT_FIELDS, strict=True
        )
    )
    short, long = ARMS[slot]
    traits = (
        short[field(stream, *SR_FIELD)],
        long[field(stream, *LR_FIELD)],
        rank + RANK_BONUS[field(stream, *RANK_FIELD)],
    )
    carried = (*stats, GameStat("CP", cp + CP_BONUS[field(stream, *CP_FIELD)]))
    return DatachCard(normalised, Device.DATACH_SD_GUNDAM, GameKind.UNIT, slot, carried, traits)


def build_sdgundam(order: SdGundamOrder) -> DatachCard | None:
    """The first card every Datach reader accepts that the game reads as ordered."""
    streams = itertools.islice(_streams(order), STREAM_LIMIT)
    codes = (code for stream in streams for code in codes_of(stream))
    return next(map(decode_sdgundam, codes), None)


def strongest_sdgundam(unit: int | None = None) -> DatachCard:
    """A unit, by default the one with the most HP, AP and DP, at every top bonus."""
    if unit is None:
        unit = max(range(len(BASES)), key=lambda ident: sum(BASES[ident][:3]))
    if unit not in UNITS:
        message = f"SD Gundam Wars has no unit {unit}"
        raise ValueError(message)
    tops = tuple(
        Constraint.exactly(base + max(bonus))
        for base, bonus in zip(BASES[unit][:3], BONUSES, strict=True)
    )
    cp = BASES[unit][4] + max(CP_BONUS)
    card = build_sdgundam(SdGundamOrder(unit, (tops[0], tops[1], tops[2]), ((CP_KEY, cp),)))
    return required(card, f"no printable SD Gundam Wars card is unit {unit} at its top numbers")


def picks_for(ident: int) -> tuple[GamePick, ...]:
    """The weapons and CP a unit can carry; a command offers nothing."""
    if ident not in UNITS:
        return ()
    short, long = ARMS[ident]
    cps = sorted({BASES[ident][4] + bonus for bonus in CP_BONUS})
    return (
        GamePick(SR_KEY, "Short-range weapon", "SR", _weapons(short)),
        GamePick(LR_KEY, "Long-range weapon", "LR", _weapons(long)),
        GamePick(CP_KEY, "CP", "CP", tuple(GameOption(cp, str(cp), str(cp)) for cp in cps)),
    )


def codes_of(stream: int) -> Iterator[str]:
    """Every code for the stream, with and without an 8, that every reader accepts."""
    for extra, prefix in itertools.product((0, eight_bit(PERMUTATION)), PREFIXES):
        code = code_for(stream | extra, PERMUTATION, prefix)
        if code is not None and printable(code):
            yield code


def _weapons(pair: tuple[int, int]) -> tuple[GameOption, ...]:
    """A unit's weapon choices, each once."""
    return tuple(GameOption(weapon, *WEAPONS[weapon]) for weapon in dict.fromkeys(pair))


def _put(value: int, place: tuple[int, int]) -> int:
    """A field's value moved to its place in the stream."""
    start, width = place
    return value << (STREAM_BITS - start - width)


def _streams(order: SdGundamOrder) -> Iterator[int]:
    """Every stream the order allows, one card at a time."""
    idents = list(UNITS) if order.ident is None else [order.ident]
    for ident in idents:
        slots = [index for index, slot in enumerate(SLOTS) if slot == ident]
        if ident >= FIRST_COMMAND:
            yield from _command_streams(slots)
        else:
            yield from _unit_streams(ident, slots, order)


def _command_streams(slots: list[int]) -> Iterator[int]:
    """A command's streams: its slot, and a spread of values in the bits it ignores."""
    for slot, top, tries in itertools.product(slots, (0, 1), range(FREE_TRIES)):
        free = tries * FREE_STEP % (1 << FREE_FIELD[1])
        yield _put(slot, SLOT_FIELD) | _put(top, TOP_FIELD) | _put(free, FREE_FIELD)


def _unit_streams(ident: int, slots: list[int], order: SdGundamOrder) -> Iterator[int]:
    """A unit's streams, closest numbers first, with the weapons and CP it was asked for."""
    wanted = dict(order.picks)
    stats = [
        _closest(base, bonus, constraint)
        for base, bonus, constraint in zip(BASES[ident][:3], BONUSES, order.stats, strict=True)
    ]
    short, long = ARMS[ident]
    choices = itertools.product(
        slots,
        *stats,
        range(len(RANK_BONUS)),
        [
            index
            for index, bonus in enumerate(CP_BONUS)
            if _allowed(wanted, CP_KEY, BASES[ident][4] + bonus)
        ],
        [index for index, weapon in enumerate(short) if _allowed(wanted, SR_KEY, weapon)],
        [index for index, weapon in enumerate(long) if _allowed(wanted, LR_KEY, weapon)],
        (0, 1),
    )
    for slot, hp, ap, dp, rank, cp, sr, lr, top in choices:
        yield (
            _put(slot, SLOT_FIELD)
            | _put(top, TOP_FIELD)
            | _put(hp, STAT_FIELDS[0])
            | _put(ap, STAT_FIELDS[1])
            | _put(dp, STAT_FIELDS[2])
            | _put(rank, RANK_FIELD)
            | _put(cp, CP_FIELD)
            | _put(sr, SR_FIELD)
            | _put(lr, LR_FIELD)
        )


def _allowed(wanted: dict[str, int], key: str, value: int) -> bool:
    """Whether a choice is the one asked for, or anything when none was."""
    return key not in wanted or wanted[key] == value


def _closest(base: int, bonus: tuple[int, ...], constraint: Constraint) -> list[int]:
    """The bonus indices the constraint admits, or the one nearest it when it admits none."""
    admitted = [index for index, add in enumerate(bonus) if constraint.admits(base + add)]
    if admitted:
        return admitted
    return [min(range(len(bonus)), key=lambda index: _distance(base + bonus[index], constraint))]


def _distance(value: int, constraint: Constraint) -> int:
    """How far a value falls outside a constraint's bounds."""
    below = 0 if constraint.minimum is None else max(0, constraint.minimum - value)
    above = 0 if constraint.maximum is None else max(0, value - constraint.maximum)
    return below + above


def command_names(ident: int) -> tuple[str, str]:
    """A command card's name in both languages."""
    command = COMMANDS[command_number(ident)]
    return command.english, command.japanese
