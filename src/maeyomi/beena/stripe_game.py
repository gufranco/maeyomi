"""The reading, building, listing and naming every Beena stripe game shares.

A Beena game takes a card only when its twelve bar places spell one of the
codes in its own list, so a game is its list: each card's number, its places,
its name and what kind of card it is. A game may leave some places unread, and
then a code matches a card whatever those places hold. The functions a surface
needs are the same for every game and are bound to that list.
"""

from dataclasses import dataclass
from typing import Final

from maeyomi.barcode.stripes import validate_stripes
from maeyomi.datach.game_card import DatachCard, GameKind
from maeyomi.datach.game_types import CardText, GameEntry, GameOrder, Pair
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.models.device import Device
from maeyomi.said import Said

NUMBER_HEADING: Final[Pair] = ("Card number", "カードばんごう")
ANY_BAR: Final = "x"


@dataclass(frozen=True, slots=True)
class StripeCard:
    """One card a game reads: its number, its twelve bar places, its name and its kind."""

    number: int
    code: str
    name: Pair
    detail: Pair

    @property
    def label(self) -> str:
        """The card's number as the card prints it."""
        return f"{self.number:02d}"


@dataclass(frozen=True, slots=True)
class StripeGame:
    """A Beena game's card list and the reading every surface asks of it."""

    device: Device
    title: Pair
    cards: tuple[StripeCard, ...]
    unknown: Said
    ignored: frozenset[int] = frozenset()

    def _key(self, code: str) -> str:
        """A code with the places the game does not read blanked out."""
        return "".join(ANY_BAR if place in self.ignored else bit for place, bit in enumerate(code))

    def _place(self, code: str) -> int | None:
        """The place in the list of the card a code reads as, or None when none does."""
        key = self._key(code.strip())
        return next(
            (place for place, card in enumerate(self.cards) if self._key(card.code) == key), None
        )

    def match(self, code: str) -> int | None:
        """The number of the card a code reads as, or None when no card has its places."""
        place = self._place(code)
        return None if place is None else self.cards[place].number

    def decode(self, code: str) -> DatachCard:
        """A card's twelve bar places as the game reads them."""
        body = validate_stripes(code)
        ident = self._place(body)
        if ident is None:
            raise UnsupportedBarcodeError(barcode=code, reason=self.unknown)
        return DatachCard(body, self.device, GameKind.ITEM, ident)

    def build(self, order: GameOrder) -> DatachCard | None:
        """The card asked for, or the first card when none is named."""
        ident = 0 if order.ident is None else order.ident
        if ident not in range(len(self.cards)):
            return None
        return self.decode(self.cards[ident].code)

    def entries(self) -> tuple[GameEntry, ...]:
        """Every card the game reads, in the order of their numbers."""
        return tuple(
            GameEntry(ident, GameKind.ITEM, *card.name) for ident, card in enumerate(self.cards)
        )

    def named(self, typed: str) -> int:
        """A card typed by its place in the list, its places, its card number or its name."""
        text = typed.strip()
        for ident, card in enumerate(self.cards):
            names = {str(ident), card.code, card.label, card.name[1]}
            if text in names or text.casefold() == card.name[0].casefold():
                return ident
        english, japanese = self.title
        message = Said(
            f"no {english} card named {typed!r}",
            f"{japanese}に {typed!r} という カードは ない",
        )
        raise ValueError(message)

    def text(self, card: DatachCard) -> CardText:
        """The card's name, what kind of card it is, and its card number."""
        entry = self.cards[card.ident]
        return CardText(entry.name, entry.detail, NUMBER_HEADING, (entry.label, entry.label))
