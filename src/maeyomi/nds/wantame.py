"""Wantame Music Channel Doko Demo Style, Capcom 2007: cards read through a microphone scanner.

The scanner reads a twelve-digit Code 128 C barcode and sends its six pairs to
the DS as sound, with the Code 128 checksum after them. The game checks the
checksum, picks one of its card tables by the second pair and takes a card only
when all six pairs match one of its records: dogs, outfits, accessories and
effects. The reading was checked against the game's own checksum, card check
and lookup routines running in the Unicorn engine. One outfit card, S36, is
found and then turned away: every scene that scans answers it with a message
of its own and gives nothing, so it is not printed.
"""

import unicodedata
from dataclasses import dataclass
from typing import Final

from maeyomi.datach.game_card import DatachCard, GameKind
from maeyomi.datach.game_types import CardText, GameEntry, GameOrder, Pair
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.models.device import Device
from maeyomi.nds.wantame_tables import CARDS
from maeyomi.romaji import romanised
from maeyomi.said import Said

STAT_KEYS: Final[tuple[str, ...]] = ()
LENGTH: Final = 12
DOGS: Final = 0x11
EFFECTS: Final = 0x31
KINDS: Final = {DOGS: 1, 0x21: 2, 0x22: 3, 0x23: 4, EFFECTS: 5}
TURNED_AWAY: Final = (0x21, 0xA6)
GAP: Final = "・"
SIGNS: Final = (0x25A0, 0x2605, 0x266A)
TIMES: Final = 0xD7
SPELLED: Final = {
    "金": "キン",
    "系": "ケイ" + GAP,
    "玉": "ダマ",
    chr(TIMES): "x",
    **dict.fromkeys(map(chr, SIGNS), GAP),
}
BRACKETS: Final = {"( ": "(", " )": ")"}
DETAILS: Final[dict[int, Pair]] = {
    DOGS: ("Dog card", "いぬの カード"),
    0x21: ("Outfit card", "ふくの カード"),
    0x22: ("Accessory card", "アクセサリの カード"),
    EFFECTS: ("Effect card", "エフェクトの カード"),
}
NUMBER_HEADING: Final[Pair] = ("Card number", "カードばんごう")
UNKNOWN: Final = Said(
    "no Wantame card carries this code",
    "ワンタメに この コードの カードは ない",
)
WRONG_LENGTH: Final = Said(
    "a Wantame card carries 12 digits",
    "ワンタメの カードは 12けたの すうじ",
)
REFUSED: Final = Said(
    "the game finds this card and gives nothing for it",
    "ゲームは この カードを みつけても なにも くれない",
)


@dataclass(frozen=True, slots=True)
class Card:
    """One card the game can read: its table, its place, its code, its name and its number."""

    table: int
    index: int
    code: str
    japanese: str
    number: str


ALL: Final = tuple(Card(*record) for record in CARDS)
PRINTED: Final = tuple(card for card in ALL if (card.table, card.index) != TURNED_AWAY)


def match(code: str) -> tuple[int, int] | None:
    """The kind and place of the record the game finds for a code, or None when none has it."""
    found = next((card for card in ALL if card.code == code.strip()), None)
    return None if found is None else (KINDS[found.table], found.index)


def _english(japanese: str) -> str:
    """A card's name in the Latin alphabet."""
    spelled = "".join(SPELLED.get(character, character) for character in japanese)
    english = unicodedata.normalize("NFKC", romanised(spelled))
    for spaced, tight in BRACKETS.items():
        english = english.replace(spaced, tight)
    return english


def _kind(table: int) -> GameKind:
    """What a table's cards are."""
    if table == DOGS:
        return GameKind.FIGHTER
    return GameKind.EFFECT if table == EFFECTS else GameKind.ITEM


def decode_wantame(code: str) -> DatachCard:
    """A card's twelve digits as the game reads them."""
    body = code.strip()
    if len(body) != LENGTH or not body.isdigit():
        raise UnsupportedBarcodeError(barcode=code, reason=WRONG_LENGTH)
    if match(body) is None:
        raise UnsupportedBarcodeError(barcode=code, reason=UNKNOWN)
    ident = next((place for place, card in enumerate(PRINTED) if card.code == body), None)
    if ident is None:
        raise UnsupportedBarcodeError(barcode=code, reason=REFUSED)
    return DatachCard(body, Device.WANTAME, _kind(PRINTED[ident].table), ident)


def build_wantame(order: GameOrder) -> DatachCard | None:
    """The card asked for, or the first card when none is named."""
    ident = 0 if order.ident is None else order.ident
    if ident not in range(len(PRINTED)):
        return None
    return decode_wantame(PRINTED[ident].code)


def wantame_entries() -> tuple[GameEntry, ...]:
    """Every card the game takes, dogs first, in the order of its tables."""
    return tuple(
        GameEntry(ident, _kind(card.table), _english(card.japanese), card.japanese)
        for ident, card in enumerate(PRINTED)
    )


def wantame_named(typed: str) -> int:
    """A card typed by number, code, English name or Japanese name."""
    text = typed.strip()
    for entry, card in zip(wantame_entries(), PRINTED, strict=True):
        if text in {str(entry.ident), card.code, entry.japanese}:
            return entry.ident
        if text.casefold() == entry.english.casefold():
            return entry.ident
    message = Said(
        f"no Wantame card named {typed!r}",
        f"ワンタメに {typed!r} という カードは ない",
    )
    raise ValueError(message)


def wantame_text(card: DatachCard) -> CardText:
    """The card's name, what kind of card it is, and the number printed on it."""
    entry = PRINTED[card.ident]
    name: Pair = (_english(entry.japanese), entry.japanese)
    return CardText(name, DETAILS[entry.table], NUMBER_HEADING, (entry.number, entry.number))
