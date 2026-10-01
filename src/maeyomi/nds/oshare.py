"""Oshare Majo Love and Berry DS Collection, Sega 2006: arcade cards read through the HCV-1000.

The HCV-1000 reads Code 39; the game takes the text after the start character,
eleven characters ending in the stop, and runs it through the routine at
$020022EC. The first character must be O. Each later one is looked up in one
of four alphabets the second character chooses, the digits become two
base-33 numbers, and the nibbles of those numbers, reversed, are the fields:
a category, a two-letter code, a number and checks the card must pass, a sum
taken mod 15 among them. A card that passes names an item such as DUP  CB004,
a dress; one that starts ON and ends A takes a shorter path with its own
tables. Every reading here was checked against that routine running in the
Unicorn engine. An item the game keeps no card image for is one no card was
printed for, so only the 281 items with an image are listed.
"""

from dataclasses import dataclass
from itertools import product
from typing import Final

from maeyomi.barcode.symbol import CODE39_CHARACTERS, CODE39_FRAME, CODE39_ONLY
from maeyomi.datach.game_card import DatachCard, GameKind
from maeyomi.datach.game_types import CardText, GameEntry, GameOrder, Pair
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.models.device import Device
from maeyomi.nds.oshare_tables import (
    ALPHABETS,
    CARD_FILES,
    DRESS_CODES,
    FOOTWEAR_CODES,
    SHORT_DRESS_CODES,
    SHORT_FOOTWEAR_CODES,
    SHORT_SPECIAL_CODES,
    SPECIAL_CODES,
)
from maeyomi.said import Said

STAT_KEYS: Final[tuple[str, ...]] = ()
LENGTH: Final = 11
LEAD: Final = "O"
STOP: Final = "*"
SHORT_LEAD: Final = "N"
SHORT_TAIL: Final = "A"
BASE: Final = 33
NIBBLE: Final = 15
CHECK: Final = 15
MISSING: Final = 45
FIRST_SHIFT: Final = 0x14
NINTH_SHIFT: Final = 10
DRESS: Final = "DUP  "
HAIR: Final = "H&M  Hr"
FOOTWEAR: Final = "FtW  "
SPECIAL: Final = "Spe  "
HAIR_HIGH: Final = 500
HIGH_HAIR_CODE: Final = 2
HAIR_KEY: Final = 11
MAX_PAIR: Final = 5
MAX_REST: Final = 6
ITEM_CODE_LENGTH: Final = 5
UNPRINTABLE: Final = frozenset("!#&*")
ORDERS: Final = {1: (0, 2, 3), 2: (1, 0, 2), 3: (3, 1, 0)}
DEFAULT_ORDER: Final = (2, 3, 1)
NINTH: Final = {1: 3, 2: 1, 3: 0}
DEFAULT_NINTH: Final = 2
FOLDERS: Final = {"dress": DRESS, "foot": FOOTWEAR, "hair": HAIR, "special": SPECIAL}
CATEGORIES: Final[dict[str, Pair]] = {
    DRESS: ("Dress", "ドレス"),
    HAIR: ("Hair and make-up", "ヘアメイク"),
    FOOTWEAR: ("Shoes", "くつ"),
    SPECIAL: ("Special", "スペシャル"),
}
REFUSED: Final = Said("Oshare Majo refuses this card", "オシャレ魔女は この カードを うけつけない")
WRONG_LENGTH: Final = Said(
    "an Oshare Majo card carries 11 characters between its start and stop",
    "オシャレ魔女の カードは スタートと ストップの あいだに 11もじ",
)


@dataclass(frozen=True, slots=True)
class Fields:
    """What the two numbers a card spells out say, under the game's own names."""

    group: int
    category: int
    spare: int
    number: int
    parity: int
    pair: int
    check: int
    spread: int
    code: int
    rest: int
    echo: int
    tail: int


def _index(alphabet: int, character: str) -> int:
    """The character's place in one of the four alphabets, or 45 when it is not there."""
    place = ALPHABETS[alphabet].find(character)
    return MISSING if place < 0 else place


def _mod4(value: int) -> int:
    """The remainder C gives for division by 4, negative for a negative value."""
    remainder = abs(value) % 4
    return -remainder if value < 0 else remainder


def _number(places: list[int]) -> int:
    """Four base-33 digits as one number."""
    return ((places[0] * BASE + places[1]) * BASE + places[2]) * BASE + places[3]


def _nibble(value: int, shift: int) -> int:
    """Four bits of a number."""
    return (value >> shift) & NIBBLE


def _reversed_nibbles(value: int) -> int:
    """The low five nibbles of a number in the opposite order."""
    return sum(_nibble(value, 4 * place) << (16 - 4 * place) for place in range(5))


def _long_places(body: str) -> list[int]:
    """The digit each character stands for, through the alphabets the second one picks."""
    first = _index(2, body[0]) - FIRST_SHIFT
    alphabets = ORDERS.get(_mod4(first), DEFAULT_ORDER)
    chosen = (alphabets[0],) * 3 + (alphabets[1],) * 3 + (alphabets[2],) * 2
    return [first, *(_index(alphabet, body[1 + place]) for place, alphabet in enumerate(chosen))]


def _long_fields(body: str) -> Fields:
    """The fields of a card read the long way."""
    places = _long_places(body)
    first, second = _number(places[1:5]), _number(places[5:9])
    a = _reversed_nibbles(first)
    b = _nibble(second, 12) << 12 | _nibble(second, 8) << 8 | _nibble(second, 4) << 4
    b |= _nibble(second, 16)
    return Fields(
        places[0] & NIBBLE,
        a >> 18,
        (a >> 15) & 7,
        (a >> 7) & 0xFF,
        (a >> 3) & NIBBLE,
        a & 7,
        second & NIBBLE,
        (b >> 13) & 7,
        (b >> 9) & NIBBLE,
        (b >> 5) & NIBBLE,
        (b >> 2) & 7,
        b & 3,
    )


def _long_passes(fields: Fields) -> bool:
    """The parity, range and mod-15 checks of the long way."""
    total = fields.group + (fields.category & 3) + fields.spare + fields.number
    total += fields.pair + fields.spread + fields.code + fields.rest
    return (
        fields.pair == fields.echo
        and (fields.group & 3) == (fields.parity & 3)
        and (fields.category & 3) == fields.tail
        and fields.group <= CHECK - 1
        and fields.pair <= MAX_PAIR
        and fields.rest <= MAX_REST
        and total % CHECK == fields.check
        and fields.rest == 0
    )


def _long_item(fields: Fields) -> str:
    """The item a card read the long way names, or nothing when its category has no such code."""
    key = fields.category * 10 + fields.tail
    number = f"{fields.number:03d}"
    if key == 0 and fields.code < len(DRESS_CODES):
        return DRESS + DRESS_CODES[fields.code] + number
    if key == HAIR_KEY and fields.code <= HIGH_HAIR_CODE:
        return HAIR + f"{fields.number + HAIR_HIGH * (fields.code == HIGH_HAIR_CODE):03d}"
    tables = {22: (FOOTWEAR, FOOTWEAR_CODES), 33: (SPECIAL, SPECIAL_CODES)}
    if key in tables and fields.code <= HIGH_HAIR_CODE:
        prefix, codes = tables[key]
        return prefix + codes[fields.code] + number
    return ""


def _short_fields(body: str) -> tuple[int, int, int]:
    """The two numbers a card read the short way spells, and the check it carries."""
    chosen = (2, 2, 2, 3, 3, 3, 1, 1, 1)
    places = [_index(alphabet, body[place]) for place, alphabet in enumerate(chosen)]
    first, second = _number(places[1:5]), _number(places[5:9])
    b = _nibble(second, 12) << 12 | _nibble(second, 8) << 8 | _nibble(second, 4) << 4
    return _reversed_nibbles(first), b | _nibble(second, 16), second & NIBBLE


def _short_item(body: str) -> str:
    """The item a card starting N and ending A names, or nothing when it fails its checks."""
    a, b, check = _short_fields(body)
    group, code, number = b >> 10 & 3, b >> 12 & NIBBLE, a >> 5 & 0xFF
    passes = (
        check == (a + b) % CHECK
        and a >> 18 == group
        and 7 - (a >> 2 & 7) == b & 7
        and 31 - (a >> 13 & 31) == b >> 5 & 31
        and a & 3 == b >> 3 & 3
    )
    tables = {
        0: (DRESS, SHORT_DRESS_CODES),
        2: (FOOTWEAR, SHORT_FOOTWEAR_CODES),
        3: (SPECIAL, SHORT_SPECIAL_CODES),
    }
    if not passes:
        return ""
    if group == 1:
        high = HAIR_HIGH * (code == HIGH_HAIR_CODE)
        return HAIR + f"{number + high:03d}" if code <= HIGH_HAIR_CODE else ""
    prefix, codes = tables[group]
    if code >= len(codes):
        return ""
    return prefix + codes[code] + f"{number:03d}" if codes[code] else prefix


def item_of(text: str) -> str:
    """The item the game names for a card's text, or nothing when it refuses the card."""
    body = text.strip().strip(CODE39_FRAME)
    if len(body) != LENGTH or not body.startswith(LEAD):
        return ""
    if body[1] == SHORT_LEAD and body[10] == SHORT_TAIL:
        return _short_item(body[1:])
    fields = _long_fields(body[1:])
    return _long_item(fields) if _long_passes(fields) else ""


def _item_name(folder: str, code: str) -> str:
    """The item a card image stands for, or nothing when no card could name it."""
    prefix = FOLDERS.get(folder, "")
    codes = {DRESS: DRESS_CODES, FOOTWEAR: FOOTWEAR_CODES[:3], SPECIAL: SPECIAL_CODES[:3]}
    readable = code[2:].isdigit() and len(code) == ITEM_CODE_LENGTH
    if prefix == HAIR:
        return HAIR + code[2:] if readable and code.startswith("Hr") else ""
    return prefix + code if readable and code[:2] in codes.get(prefix, ()) else ""


ITEMS: Final = tuple(
    name for name in (_item_name(folder, code) for folder, code in CARD_FILES) if name
)


def _wanted(item: str) -> tuple[int, int, int]:
    """The category key, code and number a long-way card for the item carries."""
    if item.startswith(HAIR):
        number = int(item[len(HAIR) :])
        return HAIR_KEY, HIGH_HAIR_CODE * (number >= HAIR_HIGH), number % HAIR_HIGH
    tables = {DRESS: (0, DRESS_CODES), FOOTWEAR: (22, FOOTWEAR_CODES), SPECIAL: (33, SPECIAL_CODES)}
    key, codes = tables[item[:5]]
    return key, codes.index(item[5:7]), int(item[7:])


def _digits(value: int) -> list[int]:
    """A number as four base-33 digits."""
    return [value // BASE**power % BASE for power in (3, 2, 1, 0)]


def _spelled(first: int, alphabets: tuple[int, int, int], a: int, b: int, check: int) -> str:
    """The eight characters that spell two numbers through the chosen alphabets."""
    one = _reversed_nibbles(a)
    two = check | _nibble(b, 4) << 4 | _nibble(b, 8) << 8 | _nibble(b, 12) << 12
    places = _digits(one) + _digits(two | (b & NIBBLE) << 16)
    chosen = (alphabets[0],) * 3 + (alphabets[1],) * 3 + (alphabets[2],) * 2
    return ALPHABETS[2][first + FIRST_SHIFT] + "".join(
        ALPHABETS[alphabet][place] for alphabet, place in zip(chosen, places, strict=True)
    )


def _candidate(item: str, first: int, free: tuple[int, int, int, int]) -> str:
    """The card text one choice of the free fields makes, or nothing when it cannot be printed."""
    key, code, number = _wanted(item)
    group, (pair, parity_high, spare, spread) = first & NIBBLE, free
    parity = (group & 3) | parity_high << 2
    category, tail = divmod(key, 10)
    check = (group + category + spare + number + pair + spread + code) % CHECK
    a = category << 18 | spare << 15 | number << 7 | parity << 3 | pair
    b = spread << 13 | code << 9 | pair << 2 | tail
    alphabets = ORDERS.get(_mod4(first), DEFAULT_ORDER)
    body = _spelled(first, alphabets, a, b, check)
    ninth = ALPHABETS[NINTH.get(_mod4(first), DEFAULT_NINTH)]
    last = next(c for c in ninth[:BASE] if c not in UNPRINTABLE and c != SHORT_TAIL)
    text = LEAD + body + last
    return "" if set(text) & UNPRINTABLE else text


def code_for(item: str) -> str:
    """The first printable card text the game reads as the item."""
    firsts = (first for first in range(-FIRST_SHIFT, 24) if first & NIBBLE <= CHECK - 1)
    candidates = (
        _candidate(item, first, free)
        for first in firsts
        for free in product(range(6), range(4), range(8), range(8))
    )
    return next(text for text in candidates if text)


def decode_oshare(code: str) -> DatachCard:
    """A card's Code 39 text as the game reads it, with or without its start and stop."""
    body = code.strip().strip(CODE39_FRAME)
    if not CODE39_CHARACTERS.fullmatch(body):
        raise UnsupportedBarcodeError(barcode=code, reason=CODE39_ONLY)
    if len(body) != LENGTH:
        raise UnsupportedBarcodeError(barcode=code, reason=WRONG_LENGTH)
    item = item_of(body)
    if not item:
        raise UnsupportedBarcodeError(barcode=code, reason=REFUSED)
    if item not in ITEMS:
        reason = Said(
            f"the game reads it as {item.strip()}, which has no card",
            f"ゲームは {item.strip()} と よむが、その カードは ない",
        )
        raise UnsupportedBarcodeError(barcode=code, reason=reason)
    return DatachCard(body, Device.OSHARE_MAJO, GameKind.ITEM, ITEMS.index(item))


def build_oshare(order: GameOrder) -> DatachCard | None:
    """A card for the item asked for, the first item when none is."""
    ident = 0 if order.ident is None else order.ident
    if ident not in range(len(ITEMS)):
        return None
    return decode_oshare(code_for(ITEMS[ident]))


def _name(item: str) -> Pair:
    """An item's category and code, in both languages."""
    prefix = next(prefix for prefix in CATEGORIES if item.startswith(prefix))
    code = item[len(prefix) - 2 :] if prefix == HAIR else item[len(prefix) :]
    english, japanese = CATEGORIES[prefix]
    return f"{english} {code}", f"{japanese} {code}"


def oshare_entries() -> tuple[GameEntry, ...]:
    """Every item a card can give, in the order the game keeps their images."""
    return tuple(GameEntry(ident, GameKind.ITEM, *_name(item)) for ident, item in enumerate(ITEMS))


def oshare_named(typed: str) -> int:
    """A card typed by number, item code, English name or Japanese name."""
    text = typed.strip()
    for entry in oshare_entries():
        code = entry.english.rsplit(" ", 1)[-1]
        if (
            text in {str(entry.ident), code, entry.japanese}
            or text.casefold() == entry.english.casefold()
        ):
            return entry.ident
    message = Said(
        f"no Oshare Majo card named {typed!r}",
        f"オシャレ魔女に {typed!r} という カードは ない",
    )
    raise ValueError(message)


def oshare_text(card: DatachCard) -> CardText:
    """The item the card gives and its category."""
    item = ITEMS[card.ident]
    prefix = next(prefix for prefix in CATEGORIES if item.startswith(prefix))
    return CardText(_name(item), CATEGORIES[prefix], ("", ""), ("", ""))
