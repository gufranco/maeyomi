"""Read and build the robot cards Datach Battle Rush reads in pairs.

Bandai's Battle Rush: Build Up Robot Tournament, a Datach game of 1993, builds
a robot at its Robo Factory from two barcodes read in order. Each card's first
twelve digits are one decimal number, split most significant bit first into
fixed fields ($9292); the thirteenth digit is not a check digit but a mark,
the true check digit less one for the frame card and less two for the weapon
card ($8AA7), so a shop's barcode is refused. The two cards must carry the
same robot number ($93A3). Stats follow from the parts, the levels and the
pilot through the tables at bank 12 $B020. Numbers 0 to 15 are the named
opponents. Confirmed against the game in MAME, whose partly emulated save
chip is passed by writing its two check bytes.
"""

import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Final

from maeyomi.datach.battlerush_tables import (
    BODY_DEFENSE,
    BODY_WEIGHT,
    FOOT_SPEED,
    FOOT_WEIGHT,
    HEAD_ATTACK,
    HEAD_DEFENSE,
    HEAD_RECOVERY,
    HEAD_SPEED,
    LEVEL_SCALE,
    PILOT_BONUSES,
    SHOULDER_ATTACK,
    SHOULDER_WEIGHT,
)
from maeyomi.datach.game_card import DatachCard, GameKind, required
from maeyomi.datach.game_reader import printable
from maeyomi.decoder.check_digit import EAN_8_LENGTH, EAN_13_LENGTH, expected_check_digit
from maeyomi.decoder.errors import InvalidCharacterError, InvalidLengthError
from maeyomi.decoder.validation import validate_barcode
from maeyomi.models.device import Device

FRAME_CARD: Final = 1
WEAPON_CARD: Final = 2
SHOP_CODE: Final = 0
BITS: Final = 40
DIGITS: Final = 12
LIMIT: Final = 10**DIGITS
FRAME_FIELDS: Final = (7, 6, 3, 5, 5, 5, 5, 4)
"""Name, number, colour, head, body, shoulder, foot, pilot."""
WEAPON_FIELDS: Final = (7, 6, 6, 6, 3, 3, 3, 3, 3)
"""Name, number, two weapons, special, and the recovery, defense, attack and speed levels."""
NAMES: Final = 1 << 7
TOP_BYTE: Final = 0xFF
STAT_BYTES: Final = {
    0x2B: "attack",
    0x2C: "defense",
    0x2D: "speed",
    0x2E: "recovery",
    0x2F: "weight",
}
RECOVERY_BASE: Final = 62
RECOVERY_TIMES: Final = 4
PERCENT: Final = 100
_SEPARATORS: Final = re.compile(r"[\s\-_]+")


@dataclass(frozen=True, slots=True)
class RobotOrder:
    """A robot's number, parts, pilot, weapons and the four levels, recovery first."""

    ident: int
    head: int = 0
    body: int = 0
    shoulder: int = 0
    foot: int = 0
    pilot: int = 0
    weapons: tuple[int, int] = (0, 0)
    levels: tuple[int, int, int, int] = (0, 0, 0, 0)


STRONGEST: Final = RobotOrder(
    ident=16, head=3, body=30, shoulder=30, foot=21, pilot=11, levels=(7, 7, 7, 7)
)
"""Found by trying every part: a byte wraps, so the largest parts do not score highest."""


def decode_battlerush(code: str) -> DatachCard:
    """What one card is; an EAN-8 is read and refused, anything else raises a typed error."""
    normalised = _SEPARATORS.sub("", code)
    if not normalised.isdigit():
        raise InvalidCharacterError(barcode=code)
    if len(normalised) == EAN_8_LENGTH:
        short = validate_barcode(normalised)
        return DatachCard(
            short, Device.DATACH_BATTLE_RUSH, GameKind.NO_EFFECT, SHOP_CODE, (), (SHOP_CODE,)
        )
    if len(normalised) != EAN_13_LENGTH:
        raise InvalidLengthError(length=len(normalised))
    mark = (expected_check_digit(normalised) - int(normalised[-1])) % 10
    value = int(normalised[:DIGITS])
    if mark == FRAME_CARD:
        name, ident, *rest = _split(value, FRAME_FIELDS)
        return DatachCard(
            normalised,
            Device.DATACH_BATTLE_RUSH,
            GameKind.UNIT,
            ident,
            (),
            (FRAME_CARD, *rest, name),
        )
    if mark == WEAPON_CARD:
        name, ident, *rest = _split(value, WEAPON_FIELDS)
        return DatachCard(
            normalised,
            Device.DATACH_BATTLE_RUSH,
            GameKind.ITEM,
            ident,
            (),
            (WEAPON_CARD, name, *rest),
        )
    return DatachCard(
        normalised, Device.DATACH_BATTLE_RUSH, GameKind.NO_EFFECT, SHOP_CODE, (), (mark,)
    )


def _split(value: int, widths: tuple[int, ...]) -> list[int]:
    """The fields a 40-bit number holds, most significant first."""
    ends = [BITS - sum(widths[: index + 1]) for index in range(len(widths))]
    return [(value >> end) & ((1 << width) - 1) for end, width in zip(ends, widths, strict=True)]


def robot_stats(frame: DatachCard, weapons: DatachCard) -> dict[str, int] | None:
    """The robot a frame card and a weapon card make, or None when they do not pair."""
    paired = frame.traits[:1] == (FRAME_CARD,) and weapons.traits[:1] == (WEAPON_CARD,)
    if not paired or frame.ident != weapons.ident:
        return None
    _, _, head, body, shoulder, foot, pilot, _ = frame.traits
    recovery, defense, attack, speed = weapons.traits[-4:]
    levels = (recovery, defense, attack, speed)
    order = RobotOrder(frame.ident, head, body, shoulder, foot, pilot, levels=levels)
    return robot_numbers(order)


def robot_numbers(order: RobotOrder) -> dict[str, int]:
    """The attack, defense, speed, recovery and weight a robot's parts and levels give."""
    head, body, shoulder, foot = order.head, order.body, order.shoulder, order.foot
    recovery_level, defense_level, attack_level, speed_level = order.levels
    stats = {
        "attack": _scaled(SHOULDER_ATTACK[shoulder] + HEAD_ATTACK[head], attack_level),
        "defense": _scaled(BODY_DEFENSE[body] + HEAD_DEFENSE[head], defense_level),
        "speed": _scaled(FOOT_SPEED[foot] + HEAD_SPEED[head], speed_level),
        "recovery": _scaled(HEAD_RECOVERY[head] * RECOVERY_TIMES + RECOVERY_BASE, recovery_level),
        "weight": (SHOULDER_WEIGHT[shoulder] + BODY_WEIGHT[body] + FOOT_WEIGHT[foot]) & TOP_BYTE,
    }
    bonuses = {STAT_BYTES[byte]: add for byte, add in PILOT_BONUSES.get(order.pilot, ())}
    return {stat: min(TOP_BYTE, value + bonuses.get(stat, 0)) for stat, value in stats.items()}


def _scaled(total: int, level: int) -> int:
    """A part total times the level's multiplier, kept to a byte as the game keeps it."""
    return (total * LEVEL_SCALE[level] // PERCENT) & TOP_BYTE


def build_robot(order: RobotOrder) -> tuple[DatachCard, DatachCard] | None:
    """The first frame and weapon cards a Datach reads as this robot, or None."""
    frame, weapons = _first_cards(order)
    return None if frame is None or weapons is None else (frame, weapons)


def _first_cards(order: RobotOrder) -> tuple[DatachCard | None, DatachCard | None]:
    """The first printable frame and weapon card, None for any the order's fields cannot fill."""
    frame = (order.ident, 0, order.head, order.body, order.shoulder, order.foot, order.pilot)
    weapons = (order.ident, *order.weapons, 0, *order.levels)
    fits = _fits(frame, FRAME_FIELDS[1:]) and _fits(weapons, WEAPON_FIELDS[1:])
    if not fits:
        return None, None
    return (
        next(_cards(_values(frame, FRAME_FIELDS), FRAME_CARD), None),
        next(_cards(_values(weapons, WEAPON_FIELDS), WEAPON_CARD), None),
    )


def _fits(fields: tuple[int, ...], widths: tuple[int, ...]) -> bool:
    """Whether every field holds a number its width can carry."""
    return all(0 <= field < 1 << width for field, width in zip(fields, widths, strict=True))


def _values(fields: tuple[int, ...], widths: tuple[int, ...]) -> Iterator[int]:
    """Every number with these fields after the name, the name left free."""
    return (_join((name, *fields), widths) for name in range(NAMES))


def _join(fields: tuple[int, ...], widths: tuple[int, ...]) -> int:
    """The 40-bit number fields make, most significant first."""
    value = 0
    for field, width in zip(fields, widths, strict=True):
        value = (value << width) | field
    return value


def _cards(values: Iterator[int], mark: int) -> Iterator[DatachCard]:
    """The cards the numbers make that fit twelve digits and every Datach reads."""
    bodies = (f"{value:0{DIGITS}d}" for value in values if value < LIMIT)
    codes = (body + str((expected_check_digit(body) - mark) % 10) for body in bodies)
    return (decode_battlerush(code) for code in codes if printable(code))


def strongest_robot() -> tuple[DatachCard, DatachCard]:
    """The robot whose attack, defense and speed are highest together, recovery at its top."""
    frame, weapons = _first_cards(STRONGEST)
    message = "the strongest Battle Rush robot cannot be printed"
    return required(frame, message), required(weapons, message)
