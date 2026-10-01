"""Kouchuu Ouja Mushiking Super Collection, Sega 2007: arcade cards read through the HCV-1000.

The HCV-1000 reads Code 39 and the game takes the thirteen characters between
the start and stop. It tries its card lists in order and takes the first card
that matches: five lists its loader reads from data/barcode/m_barcode.bin, then
a list of three and one of eight kept in its program. A card whose code ends in
FFF matches on its first ten characters, and the three after them pick a
version: MKF, RH5, NCI, BTF and KWG each name one, and any other three the
card's own. Every other card must match all thirteen. The comparison gives the
second list's versions numbers of their own, but no card in that list ends in
FFF, so they never arise. The reading was checked
against the game's own comparison routines running in the Unicorn engine. A
card's code that an earlier list already takes can never be read as that card,
so only the cards each code reaches are listed.
"""

import unicodedata
from dataclasses import dataclass
from typing import Final

from maeyomi.barcode.symbol import CODE39_CHARACTERS, CODE39_FRAME, CODE39_ONLY
from maeyomi.datach.game_card import DatachCard, GameKind
from maeyomi.datach.game_types import CardText, GameEntry, GameOrder, Pair
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.models.device import Device
from maeyomi.nds.mushiking_tables import CODES, NAMES, SERIES
from maeyomi.romaji import romanised
from maeyomi.said import Said

STAT_KEYS: Final[tuple[str, ...]] = ()
LENGTH: Final = 13
PREFIX: Final = 10
WILD: Final = "FFF"
FILED_LISTS: Final = 5
PARTNER_LIST: Final = 2
MOVE_LIST: Final = 3
LICENSE_LIST: Final = 4
SECOND_LIST: Final = 1
SERIES_BASE: Final = 16
EXACT: Final = -1
UNWRITTEN: Final = 0
OWN: Final = 0x11
VERSIONS: Final = {"MKF": 0xA, "RH5": 0xB, "NCI": 0xC, "BTF": 0xD, "KWG": 0xE}
KANJI: Final = {"丸": "マル"}
UNKNOWN: Final = Said(
    "no Mushiking card carries this code",
    "ムシキングに この コードの カードは ない",
)
WRONG_LENGTH: Final = Said(
    "a Mushiking card carries 13 characters between its start and stop",
    "ムシキングの カードは スタートと ストップの あいだに 13もじ",
)
NUMBERED: Final[dict[int, Pair]] = {
    MOVE_LIST: ("Move card", "わざカード"),
    LICENSE_LIST: ("License card", "ライセンスカード"),
}
EXTRA: Final[Pair] = ("Extra card", "とくべつカード")
DETAILS: Final[dict[int, Pair]] = {
    0: ("Beetle card", "ムシカード"),
    SECOND_LIST: ("Beetle card", "ムシカード"),
    PARTNER_LIST: ("Partner card", "パートナーカード"),
    MOVE_LIST: ("Move card", "わざカード"),
    LICENSE_LIST: ("License card", "ライセンスカード"),
}
EXTRA_DETAIL: Final[Pair] = (
    "Extra card kept in the game's program",
    "ゲームに はいっている カード",
)


@dataclass(frozen=True, slots=True)
class Card:
    """One card the game can read: its list, its place in the list and its code."""

    group: int
    index: int
    code: str


def _matches(group: int, record: str, text: str) -> bool:
    """Whether a scanned text is the card a record stands for."""
    if group < FILED_LISTS and record.endswith(WILD):
        return text[:PREFIX] == record[:PREFIX]
    return text == record


def _version(group: int, index: int, record: str, suffix: str) -> int:
    """The version the comparison leaves for a matched card."""
    if group >= FILED_LISTS:
        return UNWRITTEN
    if not record.endswith(WILD):
        return EXACT
    if suffix in VERSIONS:
        return VERSIONS[suffix]
    return int(SERIES[index], SERIES_BASE) if group == 0 else OWN


def match(text: str) -> tuple[int, int, int] | None:
    """The list, card and version the game reads a text as, or None when no card has it."""
    body = text.strip().strip(CODE39_FRAME)
    found = next(
        (
            (group, index, record)
            for group, records in enumerate(CODES)
            for index, record in enumerate(records)
            if len(body) == LENGTH and _matches(group, record, body)
        ),
        None,
    )
    if found is None:
        return None
    group, index, record = found
    return group, index, _version(group, index, record, body[PREFIX:])


CARDS: Final = tuple(
    Card(group, index, record)
    for group, records in enumerate(CODES)
    for index, record in enumerate(records)
    if (match(record) or (EXACT, EXACT, EXACT))[:2] == (group, index)
)


def _english(japanese: str) -> str:
    """A beetle or character's name in the Latin alphabet."""
    spelled = "".join(KANJI.get(character, character) for character in japanese)
    return unicodedata.normalize("NFKC", romanised(spelled))


def _kind(group: int) -> GameKind:
    """What a list's cards are."""
    if group <= PARTNER_LIST:
        return GameKind.FIGHTER
    return GameKind.ITEM if group == MOVE_LIST else GameKind.EFFECT


def _name(card: Card) -> Pair:
    """A card's name: its beetle or character, or its list and number."""
    if card.group <= PARTNER_LIST:
        japanese = NAMES[card.group][card.index]
        return _english(japanese), japanese
    if card.group in NUMBERED:
        english, japanese = NUMBERED[card.group]
        return f"{english} {card.index + 1}", f"{japanese} {card.index + 1}"
    number = card.index + 1 + len(CODES[FILED_LISTS]) * (card.group > FILED_LISTS)
    return f"{EXTRA[0]} {number}", f"{EXTRA[1]} {number}"


def decode_mushiking(code: str) -> DatachCard:
    """A card's Code 39 text as the game reads it, with or without its start and stop."""
    body = code.strip().strip(CODE39_FRAME)
    if not CODE39_CHARACTERS.fullmatch(body):
        raise UnsupportedBarcodeError(barcode=code, reason=CODE39_ONLY)
    if len(body) != LENGTH:
        raise UnsupportedBarcodeError(barcode=code, reason=WRONG_LENGTH)
    read = match(body)
    if read is None:
        raise UnsupportedBarcodeError(barcode=code, reason=UNKNOWN)
    group, index, version = read
    ident = next(
        place for place, card in enumerate(CARDS) if (card.group, card.index) == (group, index)
    )
    return DatachCard(body, Device.MUSHIKING, _kind(group), ident, (), (version,))


def build_mushiking(order: GameOrder) -> DatachCard | None:
    """The card asked for, printed with its own code, or the first card when none is named."""
    ident = 0 if order.ident is None else order.ident
    if ident not in range(len(CARDS)):
        return None
    return decode_mushiking(CARDS[ident].code)


def mushiking_entries() -> tuple[GameEntry, ...]:
    """Every card a code can reach, in the order the game tries them."""
    return tuple(
        GameEntry(ident, _kind(card.group), *_name(card)) for ident, card in enumerate(CARDS)
    )


def mushiking_named(typed: str) -> int:
    """A card typed by number, code, English name or Japanese name."""
    text = typed.strip()
    for entry, card in zip(mushiking_entries(), CARDS, strict=True):
        named = {str(entry.ident), card.code, entry.japanese}
        if text in named or text.casefold() == entry.english.casefold():
            return entry.ident
    message = Said(
        f"no Mushiking card named {typed!r}",
        f"ムシキングに {typed!r} という カードは ない",
    )
    raise ValueError(message)


def mushiking_text(card: DatachCard) -> CardText:
    """The card's beetle, character or number, what kind of card it is, and its version."""
    entry = CARDS[card.ident]
    (version,) = card.traits
    suffix = card.barcode[PREFIX:]
    power: Pair = (
        (f"Read as version {suffix}", f"{suffix} の バージョンとして よむ")
        if suffix in VERSIONS
        else ("", "")
    )
    detail = DETAILS.get(entry.group, EXTRA_DETAIL)
    heading: Pair = ("", "") if version in {EXACT, UNWRITTEN} else ("Version", "バージョン")
    return CardText(_name(entry), detail, heading, power)
