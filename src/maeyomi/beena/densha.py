"""Densha Daishuugou! Card de Asobou, Sega Toys 2006: train cards for the Advanced Pico Beena.

Each card carries twelve bar places along one edge, and the game takes a card
only when its places spell one of its 50 trains or its test card. The list
comes from MAME's software list; the stripe layout was measured on the scans
of real cards, and every code was scanned in MAME, where the game brought up a
train for each listed card and stayed on its page for every other code tried.
"""

from dataclasses import dataclass
from typing import Final

from maeyomi.barcode.stripes import validate_stripes
from maeyomi.beena.densha_tables import CARDS
from maeyomi.datach.game_card import DatachCard, GameKind
from maeyomi.datach.game_types import CardText, GameEntry, GameOrder, Pair
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.models.device import Device
from maeyomi.said import Said

STAT_KEYS: Final[tuple[str, ...]] = ()
TEST_CARD: Final = 51
DETAIL: Final[Pair] = ("Train card", "でんしゃの カード")
TEST_NAME: Final[Pair] = ("Test card", "テストカード")
NUMBER_HEADING: Final[Pair] = ("Card number", "カードばんごう")
UNKNOWN: Final = Said(
    "no Densha Daishuugou card carries these bars",
    "でんしゃだいしゅうごうに この バーの カードは ない",
)


@dataclass(frozen=True, slots=True)
class Card:
    """One card the game reads: its number and its twelve bar places."""

    number: int
    code: str


PRINTED: Final = tuple(Card(number, code) for number, code in CARDS)


def match(code: str) -> int | None:
    """The number of the card whose bars a code spells, or None when no card has them."""
    return next((card.number for card in PRINTED if card.code == code.strip()), None)


def _label(card: Card) -> str:
    """A card's number as the card prints it."""
    return f"{card.number:02d}"


def _name(card: Card) -> Pair:
    """A card's name: the test card, or its number."""
    if card.number == TEST_CARD:
        return TEST_NAME
    return f"Train card {_label(card)}", f"でんしゃカード {_label(card)}"


def decode_densha(code: str) -> DatachCard:
    """A card's twelve bar places as the game reads them."""
    body = validate_stripes(code)
    ident = next((place for place, card in enumerate(PRINTED) if card.code == body), None)
    if ident is None:
        raise UnsupportedBarcodeError(barcode=code, reason=UNKNOWN)
    return DatachCard(body, Device.DENSHA, GameKind.ITEM, ident)


def build_densha(order: GameOrder) -> DatachCard | None:
    """The card asked for, or the first card when none is named."""
    ident = 0 if order.ident is None else order.ident
    if ident not in range(len(PRINTED)):
        return None
    return decode_densha(PRINTED[ident].code)


def densha_entries() -> tuple[GameEntry, ...]:
    """Every card the game reads, in the order of their numbers."""
    return tuple(
        GameEntry(ident, GameKind.ITEM, *_name(card)) for ident, card in enumerate(PRINTED)
    )


def densha_named(typed: str) -> int:
    """A card typed by its place in the list, its bars, its card number or its name."""
    text = typed.strip()
    for ident, card in enumerate(PRINTED):
        names = {str(ident), card.code, _label(card), *_name(card)}
        if text in names or text.casefold() == _name(card)[0].casefold():
            return ident
    message = Said(
        f"no Densha Daishuugou card named {typed!r}",
        f"でんしゃだいしゅうごうに {typed!r} という カードは ない",
    )
    raise ValueError(message)


def densha_text(card: DatachCard) -> CardText:
    """The card's name, what it is, and its card number."""
    entry = PRINTED[card.ident]
    return CardText(_name(entry), DETAIL, NUMBER_HEADING, (_label(entry), _label(entry)))
