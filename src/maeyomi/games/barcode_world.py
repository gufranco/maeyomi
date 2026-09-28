"""Read and build barcodes the way Barcode World reads them.

Sunsoft's Barcode World, a Famicom game of 1992, takes its cards through a
Barcode Battler II on the Famicom's expansion port, which sends the thirteen
digits as they are, so every valid EAN reads. The game decodes them itself in
bank 12 of its program, confirmed against the game running in MAME on 211
codes, its 24 released cards among them:

1. Two Epoch product codes are first rewritten into special cards ($9422).
2. A code is read one of two ways ($914F). The second takes the digits in
   place: HP from the first three, ST and DF from the next two pairs, then the
   kind, job, speed and a two-digit ability. HP above 199 needs a 9 as its
   last digit and speed 5, and then the kind digit 0, 1 or 2 adds 100 to ST,
   to DF or to both ($9198). The first way works the digits from the end.
3. Five listed codes become job 3 with a fixed ability ($945A).
4. A kind below 5 is a fighter: every fighter gets 5 herbs, and a job of 7 or
   more is a magician with 10 magic ($8E4E). A kind from 5 is a weapon,
   protector or item, which the character screen refuses.

Numbers are in hundreds on the screen, as on the Barcode Battler II.
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
from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.decoder.validation import validate_barcode
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device

SWAPS: Final = (("4905040352507", "052150100250"), ("4905040352521", "052150118250"))
"""Bank 12 $8000: two product codes and the twelve digits each is read as instead."""

SPECIALS: Final = (
    ("012040115418", 7),
    ("012020104418", 2),
    ("012010230818", 8),
    ("015060415418", 4),
    ("018050630818", 5),
)
"""Bank 12 $8034: codes whose first twelve digits make a job 3 card with this ability."""

WARRIOR: Final = 0
MAGICIAN: Final = 1
JOB_KEY: Final = "job"
SPEED_KEY: Final = "speed"
ABILITY_KEY: Final = "ability"
FIRST_MAGICIAN_JOB: Final = 7
FIRST_ITEM_KIND: Final = 5
HERBS: Final = 5
MAGIC: Final = 10
HUNDRED: Final = 100
BIG_HP: Final = 200
BOOST: Final = 100
TOP_HP: Final = 499
TOP_STAT: Final = 199
SPECIAL_JOB: Final = 3
MARKER_SPEED: Final = 5
BYTE: Final = 0xFF
WORD: Final = 0xFFFF
DECIMAL: Final = 10
STRENGTH_WRAP: Final = 12
MARKER_DIGIT: Final = 9
PLAIN_KIND: Final = 4
BOOSTS: Final = {0: (True, False), 1: (False, True), 2: (True, True)}


@dataclass(frozen=True, slots=True)
class BarcodeWorldOrder:
    """A warrior or a magician, what HP, ST and DF must be, and its job, speed and ability."""

    ident: int | None
    stats: tuple[Constraint, Constraint, Constraint]
    picks: tuple[tuple[str, int], ...] = ()


def decode_barcode_world(code: str) -> DatachCard:
    """Read a barcode, raising a typed error when it is not a valid EAN."""
    normalised = validate_barcode(code)
    text = _rewritten(normalised.rjust(13).encode("ascii"))
    fields = _positional(text) if _in_place(text) else _from_end(text)
    for pattern, ability in SPECIALS:
        if text[:12] == pattern.encode("ascii"):
            fields = {**fields, "job": SPECIAL_JOB, "ability": ability}
    return _card(normalised, fields)


def _rewritten(text: bytes) -> bytes:
    """The two product codes the game swaps for special cards, and any other as it is."""
    for source, target in SWAPS:
        if text == source.encode("ascii"):
            return target.encode("ascii") + text[12:]
    return text


def _in_place(text: bytes) -> bool:
    """Whether the game reads the digits in place, per its test at $914F."""
    if text[0] == ord(" "):
        return False
    if text[0] >= ord("2"):
        return text[2] == ord("9") and text[9] == ord("5")
    return text[7] < ord("5") or not (text[3] >= ord("2") or text[5] >= ord("2"))


def _number(text: bytes, start: int, width: int) -> int:
    """Digits read as one decimal number, the way the game subtracts '0' from each."""
    value = 0
    for character in text[start : start + width]:
        value = (value * 10 + character - ord("0")) & WORD
    return value


def _positional(text: bytes) -> dict[str, int]:
    """The second way: every field taken straight from its digits, then the big-HP boosts."""
    fields = {
        "hp": _number(text, 0, 3),
        "st": ((text[3] & 0x0F) * 10 + (text[4] & 0x0F)) & BYTE,
        "df": ((text[5] & 0x0F) * 10 + (text[6] & 0x0F)) & BYTE,
        "kind": (text[7] - ord("0")) & BYTE,
        "job": (text[8] - ord("0")) & BYTE,
        "speed": (text[9] - ord("0")) & BYTE,
        "ability": _number(text, 10, 2) & BYTE,
    }
    if text[0] >= ord("2") and text[2] == ord("9") and text[9] == ord("5"):
        st, df = BOOSTS.get(text[7] - ord("0"), (False, False))
        fields = {
            **fields,
            "st": (fields["st"] + BOOST * st) & BYTE,
            "df": (fields["df"] + BOOST * df) & BYTE,
        }
    return fields


def _digit(character: int) -> int:
    """A digit's value; the first way only reads positions a valid code fills with digits."""
    return character - ord("0")


def _wrapped(character: int, offset: int) -> int:
    """A digit shifted by the game's offset and brought back under 10 once."""
    value = (character - offset) & BYTE
    return (value - DECIMAL) & BYTE if value >= DECIMAL else value


def _from_end(text: bytes) -> dict[str, int]:
    """The first way, picked by the check digit: 0 to 4 a fighter, 5 to 9 anything else."""
    kind = _digit(text[12])
    fighter = kind < FIRST_ITEM_KIND
    return {
        "hp": _end_hp(text, 1 if fighter else 3),
        "st": _end_st(text, fighter=fighter),
        "df": _end_df(text, fighter=fighter),
        "kind": kind,
        "job": _digit(text[5]) if fighter else 0,
        "speed": _digit(text[10]),
        "ability": _end_ability(text),
    }


def _end_hp(text: bytes, shift: int) -> int:
    """HP from digits 12, 11 and 10 ($9232 for a fighter, $9293 otherwise)."""
    hundreds, tens, units = (_digit(text[index]) for index in (11, 10, 9))
    return (hundreds >> shift) * HUNDRED + tens * DECIMAL + units


def _end_st(text: bytes, *, fighter: bool) -> int:
    """ST from digits 11 and 10 ($92F6 for a fighter, $9329 otherwise)."""
    if fighter:
        tens = (2 + text[10] - 0x2B) & BYTE
        tens = (tens - DECIMAL) & BYTE if tens >= STRENGTH_WRAP else tens
        return (tens * 10 + _wrapped(text[9], 0x2B)) & BYTE
    tens = ((_wrapped(text[10], 0x2B) >> 2) + 1) * 10
    return (tens + text[9] - 0x2B) & BYTE


def _end_df(text: bytes, *, fighter: bool) -> int:
    """DF from digits 10 and 9 ($9357 for a fighter, $9387 otherwise)."""
    tens = _wrapped(text[9], 0x29)
    tens = tens if fighter else tens >> 2
    return (tens * 10 + _wrapped(text[8], 0x29)) & BYTE


def _end_ability(text: bytes) -> int:
    """The ability from digits 9 and 11 ($93F2)."""
    return (_digit(text[8]) >> 2) * DECIMAL + _digit(text[10])


def _card(code: str, fields: dict[str, int]) -> DatachCard:
    """The card the fields make: a fighter with its numbers, or anything else by kind."""
    kind = fields.get("kind", 0)
    traits = (
        fields.get("job", 0),
        fields.get("speed", 0),
        fields.get("ability", 0),
        fields.get("hp", 0),
    )
    if kind >= FIRST_ITEM_KIND:
        return DatachCard(code, Device.BARCODE_WORLD, GameKind.ITEM, kind, (), traits)
    magic = MAGIC if fields.get("job", 0) >= FIRST_MAGICIAN_JOB else 0
    stats = (
        GameStat("WHP", fields.get("hp", 0) * HUNDRED),
        GameStat("WST", fields.get("st", 0) * HUNDRED),
        GameStat("WDF", fields.get("df", 0) * HUNDRED),
        GameStat("WMP", magic),
        GameStat("WPP", HERBS),
    )
    return DatachCard(code, Device.BARCODE_WORLD, GameKind.FIGHTER, kind, stats, traits)


def build_barcode_world(order: BarcodeWorldOrder) -> DatachCard | None:
    """The first code the game reads in place as the fighter ordered, or None."""
    wanted = dict(order.picks)
    bodies = ("".join(str(digit) for digit in digits) for digits in _candidates(order, wanted))
    cards = (decode_barcode_world(body + str(expected_check_digit(body))) for body in bodies)
    return next((card for card in cards if _meets(card, order, wanted)), None)


def _candidates(order: BarcodeWorldOrder, wanted: dict[str, int]) -> Iterator[list[int]]:
    """Every twelve-digit body that reads in place with the numbers and choices ordered."""
    health, attack, defence = (
        list(_hundreds(constraint, top))
        for constraint, top in zip(order.stats, (TOP_HP, TOP_STAT, TOP_STAT), strict=True)
    )
    jobs = _jobs(order.ident, wanted.get(JOB_KEY))
    speeds = [wanted[SPEED_KEY]] if SPEED_KEY in wanted else list(range(DECIMAL))
    small = [value for value in health if value < BIG_HP]
    big = [value for value in health if value >= BIG_HP and value % DECIMAL == MARKER_DIGIT]
    plain = itertools.product(small, _below(attack), _below(defence), jobs, speeds)
    marked = itertools.product(
        big, attack, defence, jobs, [MARKER_SPEED] if MARKER_SPEED in speeds else []
    )
    for hp, st, df, job, speed in itertools.chain(plain, marked):
        kind = _kind_for(hp, st, df)
        yield [
            *_split(hp, 3),
            *_split(st % BOOST, 2),
            *_split(df % BOOST, 2),
            kind,
            job,
            speed,
            *_split(wanted.get(ABILITY_KEY, 0), 2),
        ]


def _below(values: list[int]) -> list[int]:
    """The values that need no boost."""
    return [value for value in values if value < BOOST]


def _hundreds(constraint: Constraint, top: int) -> Iterator[int]:
    """Every number in hundreds, up to the top one, that the constraint admits."""
    return (value for value in range(top + 1) if constraint.admits(value * HUNDRED))


def _jobs(ident: int | None, job: int | None) -> list[int]:
    """The jobs of the class asked for, or only the one picked when it belongs to it."""
    allowed = {
        None: range(DECIMAL),
        WARRIOR: range(FIRST_MAGICIAN_JOB),
        MAGICIAN: range(FIRST_MAGICIAN_JOB, DECIMAL),
    }.get(ident, range(0))
    return [value for value in allowed if job in {None, value}]


def _kind_for(hp: int, st: int, df: int) -> int:
    """The kind digit that gives these numbers: the boost selector above 199 HP, else 4."""
    needed = (st >= BOOST, df >= BOOST)
    if hp < BIG_HP or needed == (False, False):
        return PLAIN_KIND
    return next(kind for kind, boost in BOOSTS.items() if boost == needed)


def _split(value: int, width: int) -> list[int]:
    """A number as its decimal digits, zero-padded to a width."""
    return [int(character) for character in f"{value:0{width}d}"]


def _meets(card: DatachCard, order: BarcodeWorldOrder, wanted: dict[str, int]) -> bool:
    """Whether a read card is the fighter the order asks for, numbers and choices alike."""
    numbers = (card.value("WHP"), card.value("WST"), card.value("WDF"))
    admitted = all(
        constraint.admits(value) for constraint, value in zip(order.stats, numbers, strict=True)
    )
    job, speed, ability, _ = card.traits
    chosen = {JOB_KEY: job, SPEED_KEY: speed, ABILITY_KEY: ability}
    picked = all(chosen[key] == value for key, value in wanted.items() if key in chosen)
    return card.kind is GameKind.FIGHTER and admitted and picked


def picks_for(ident: int) -> tuple[GamePick, ...]:
    """A warrior's or a magician's jobs, and the speed and ability any fighter takes."""
    jobs = range(FIRST_MAGICIAN_JOB) if ident == WARRIOR else range(FIRST_MAGICIAN_JOB, DECIMAL)
    return (
        GamePick(JOB_KEY, "Job", "しょくぎょう", _numbered(jobs)),
        GamePick(SPEED_KEY, "Speed", "すばやさ", _numbered(range(DECIMAL))),
        GamePick(ABILITY_KEY, "Ability", "とくしゅ のうりょく", _numbered(range(DECIMAL**2))),
    )


def _numbered(values: range) -> tuple[GameOption, ...]:
    """Options named by their own number."""
    return tuple(GameOption(value, str(value), str(value)) for value in values)


def strongest_barcode_world() -> DatachCard:
    """A magician with HP, ST and DF at the most the game can read."""
    top = (
        Constraint.exactly(TOP_HP * HUNDRED),
        Constraint.exactly(TOP_STAT * HUNDRED),
        Constraint.exactly(TOP_STAT * HUNDRED),
    )
    card = build_barcode_world(BarcodeWorldOrder(MAGICIAN, top, ((JOB_KEY, 9),)))
    return required(card, "the strongest Barcode World card cannot be printed")
