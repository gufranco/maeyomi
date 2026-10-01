"""Ryuusei no Rockman Dragon, Capcom 2006: Wave Cards read through the Wave Scanner.

Every Wave Card carries a twelve-digit Code 128 C barcode that starts 040000.
The Wave Scanner sends the game only its last three pairs, each as six bits,
after the constant 0x10 and before a check byte that XORs the three bytes above
it. The card list and that layout come from GBE+'s Wave Scanner notes; the
game's own reading of them has not been traced yet. Three character cards
carry the code of a battle card and are named beside it.
"""

from dataclasses import dataclass
from functools import reduce
from typing import Final

from maeyomi.datach.game_card import DatachCard, GameKind
from maeyomi.datach.game_types import CardText, GameEntry, GameOrder, Pair
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.models.device import Device
from maeyomi.nds.rockman_tables import CARDS
from maeyomi.said import Said

STAT_KEYS: Final[tuple[str, ...]] = ()
PREFIX: Final = "040000"
LENGTH: Final = 12
PAIR_DIGITS: Final = 2
PAIR_BITS: Final = 6
LARGEST_PAIR: Final = (1 << PAIR_BITS) - 1
HEADER: Final = 0x10 << 26
CHECK_SHIFTS: Final = (8, 16, 24)
BYTE: Final = 0xFF
PAIR_SHIFTS: Final = (20, 14, 8)
CHARACTER: Final = "C-"
DETAILS: Final[dict[str, Pair]] = {
    "S-": ("Standard card", "スタンダードカード"),
    "BC-": ("Standard card", "スタンダードカード"),
    "M-": ("Mega card", "メガカード"),
    "G-": ("Giga card", "ギガカード"),
    CHARACTER: ("Character card", "キャラクターカード"),
}
WRONG_FORM: Final = Said(
    "a Wave Card barcode is 040000 and six more digits",
    "ウェーブカードの バーコードは 040000 と 6けたの すうじ",
)
TOO_LARGE: Final = Said(
    "the Wave Scanner sends each of the last three pairs as a number up to 63",
    "ウェーブスキャナーは さいごの 3くみを 63までの かずで おくる",
)
UNKNOWN: Final = Said(
    "no Wave Card carries this code",
    "この コードの ウェーブカードは ない",
)


@dataclass(frozen=True, slots=True)
class Card:
    """One code the game is sent: the card listed first for it and any card that shares it."""

    number: str
    code: str
    english: str
    japanese: str
    sharing: tuple[tuple[str, str, str], ...] = ()


def _card_for(code: str) -> Card:
    """The first card listed with a code, and the cards listed after it with the same code."""
    (number, _, english, japanese), *others = [card for card in CARDS if card[1] == code]
    sharing = tuple(
        (other, other_english, other_japanese) for other, _, other_english, other_japanese in others
    )
    return Card(number, code, english, japanese, sharing)


PRINTED: Final = tuple(_card_for(code) for code in dict.fromkeys(card[1] for card in CARDS))


def _xor(left: int, right: int) -> int:
    """Two bytes combined the way the check byte combines them."""
    return left ^ right


def sent(code: str) -> int:
    """The 32 bits the Wave Scanner sends for a barcode."""
    pairs = (int(code[place : place + PAIR_DIGITS]) for place in range(6, LENGTH, PAIR_DIGITS))
    body = HEADER | sum(pair << shift for pair, shift in zip(pairs, PAIR_SHIFTS, strict=True))
    return body | reduce(_xor, (body >> shift & BYTE for shift in CHECK_SHIFTS))


def _detail(number: str) -> Pair:
    """What kind of card a card number names."""
    return next(detail for prefix, detail in DETAILS.items() if number.startswith(prefix))


def _kind(number: str) -> GameKind:
    """A character card is a fighter; every battle card is an item."""
    return GameKind.FIGHTER if number.startswith(CHARACTER) else GameKind.ITEM


def decode_rockman(code: str) -> DatachCard:
    """A Wave Card's twelve digits as the Wave Scanner sends them."""
    body = code.strip()
    if len(body) != LENGTH or not body.isdigit() or not body.startswith(PREFIX):
        raise UnsupportedBarcodeError(barcode=code, reason=WRONG_FORM)
    pairs = [int(body[place : place + PAIR_DIGITS]) for place in range(6, LENGTH, PAIR_DIGITS)]
    if max(pairs) > LARGEST_PAIR:
        raise UnsupportedBarcodeError(barcode=code, reason=TOO_LARGE)
    ident = next((place for place, card in enumerate(PRINTED) if card.code == body[6:]), None)
    if ident is None:
        raise UnsupportedBarcodeError(barcode=code, reason=UNKNOWN)
    return DatachCard(body, Device.ROCKMAN_DRAGON, _kind(PRINTED[ident].number), ident)


def build_rockman(order: GameOrder) -> DatachCard | None:
    """The card asked for, or the first card when none is named."""
    ident = 0 if order.ident is None else order.ident
    if ident not in range(len(PRINTED)):
        return None
    return decode_rockman(PREFIX + PRINTED[ident].code)


def rockman_entries() -> tuple[GameEntry, ...]:
    """Every code the game is sent, in the order of the card numbers."""
    return tuple(
        GameEntry(ident, _kind(card.number), card.english, card.japanese)
        for ident, card in enumerate(PRINTED)
    )


def _names(card: Card) -> set[str]:
    """Everything a card can be typed as besides its place in the list."""
    numbers = {card.number, *(number for number, _, _ in card.sharing)}
    return {*numbers, card.code, PREFIX + card.code, card.japanese}


def rockman_named(typed: str) -> int:
    """A card typed by place, barcode, card number, English name or Japanese name."""
    text = typed.strip()
    for ident, card in enumerate(PRINTED):
        if text in {str(ident), *_names(card)} or text.casefold() == card.english.casefold():
            return ident
    message = Said(
        f"no Wave Card named {typed!r}",
        f"{typed!r} という ウェーブカードは ない",
    )
    raise ValueError(message)


def rockman_text(card: DatachCard) -> CardText:
    """The card's name, what kind of card it is, and its card number."""
    entry = PRINTED[card.ident]
    english = ", ".join([entry.number, *(f"{number} {name}" for number, name, _ in entry.sharing)])
    japanese = "、".join([entry.number, *(f"{number} {name}" for number, _, name in entry.sharing)])
    return CardText(
        (entry.english, entry.japanese),
        _detail(entry.number),
        ("Card number", "カードばんごう"),
        (english, japanese),
    )
