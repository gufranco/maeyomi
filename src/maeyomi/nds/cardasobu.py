"""Card de Asobu! Hajimete no DS, Sega 2007: a DS game that reads kana cards through the HCV-1000.

Sega's HCV-1000 reads Code 39 and hands the game the text between the start and
stop characters. The game takes a card when its first ten characters match one
of the codes in its table and the rest is V01, checked in GBE+ on every card
and on codes that differ only there. Each card teaches one kana: its place in
the table is its kana in order, あ first. Slot 5, か, holds a code no card
carries; the か card, かえる, is the last entry. A card carries no numbers.

The Japanese names are the ones GBE+'s HCV-1000 notes list, corrected where a
name cannot belong to its slot: the card for ぬ is ぬいぐるみ, for ら らっぱ, and
しょうぼうしゃ and むぎわらぼうし are spelled with ぼう. The English names are this
project's translation.
"""

from typing import Final

from maeyomi.barcode.symbol import CODE39_CHARACTERS, CODE39_FRAME, CODE39_ONLY
from maeyomi.datach.game_card import DatachCard, GameKind
from maeyomi.datach.game_types import CardText, GameEntry, GameOrder, Pair
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.models.device import Device
from maeyomi.nds.cardasobu_tables import CODES
from maeyomi.romaji import romanised
from maeyomi.said import Said

STAT_KEYS: Final[tuple[str, ...]] = ()
VERSION: Final = "V01"
NO_CARD: Final = 5
SEARCH: Final = 44
UNKNOWN: Final = Said(
    "no Card de Asobu card carries this text",
    "カードであそぶに この もじの カードは ない",
)
KANA: Final = (
    "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわ?んか"
)
SEARCH_DETAIL: Final[Pair] = ("Starts the card search", "カードさがしを はじめる")
NO_HEADING: Final[Pair] = ("", "")
NAMES: Final[tuple[Pair, ...]] = (
    ("Duck", "あひる"),
    ("Dog", "いぬ"),
    ("Rabbit", "うさぎ"),
    ("Pencil", "えんぴつ"),
    ("Rice ball", "おにぎり"),
    ("", ""),
    ("Hot-air balloon", "ききゅう"),
    ("Whale", "くじら"),
    ("Caterpillar", "けむし"),
    ("Koala", "こあら"),
    ("Cherry blossom", "さくら"),
    ("Fire engine", "しょうぼうしゃ"),
    ("Watermelon", "すいか"),
    ("Cicada", "せみ"),
    ("Broad bean", "そらまめ"),
    ("Drum", "たいこ"),
    ("Tulip", "ちゅーりっぷ"),
    ("Swallow", "つばめ"),
    ("Ladybird", "てんとうむし"),
    ("Triangle", "とらいあんぐる"),
    ("Aubergine", "なす"),
    ("Chicken", "にわとり"),
    ("Soft toy", "ぬいぐるみ"),
    ("Cat", "ねこ"),
    ("Saw", "のこぎり"),
    ("Pigeon", "はと"),
    ("Sunflower", "ひまわり"),
    ("Boat", "ふね"),
    ("Helicopter", "へりこぷたー"),
    ("Firefly", "ほたる"),
    ("Pillow", "まくら"),
    ("Honeybee", "みつばち"),
    ("Straw hat", "むぎわらぼうし"),
    ("Glasses", "めがね"),
    ("Xylophone", "もっきん"),
    ("Goat", "やぎ"),
    ("Lily", "ゆり"),
    ("Yacht", "よっと"),
    ("Trumpet", "らっぱ"),
    ("Apple", "りんご"),
    ("Ruby", "るびー"),
    ("Lemon", "れもん"),
    ("Rocket", "ろけっと"),
    ("Crocodile", "わに"),
    ("Find the card", "カードをさがす"),
    ("N", "ん"),
    ("Frog", "かえる"),
)


def _slot(text: str) -> int | None:
    """The table slot a card's text matches, or None when it matches none."""
    return next(
        (slot for slot, code in enumerate(CODES) if slot != NO_CARD and text == code + VERSION),
        None,
    )


def _kind(slot: int) -> GameKind:
    """What a slot is: the search card starts a search, every other card is a kana."""
    return GameKind.EFFECT if slot == SEARCH else GameKind.ITEM


def decode_cardasobu(code: str) -> DatachCard:
    """A card's Code 39 text as the game reads it, with or without its start and stop."""
    text = code.strip().strip(CODE39_FRAME)
    if not CODE39_CHARACTERS.fullmatch(text):
        raise UnsupportedBarcodeError(barcode=code, reason=CODE39_ONLY)
    slot = _slot(text)
    if slot is None:
        raise UnsupportedBarcodeError(barcode=code, reason=UNKNOWN)
    return DatachCard(text, Device.CARD_DE_ASOBU, _kind(slot), slot)


def build_cardasobu(order: GameOrder) -> DatachCard | None:
    """The card in the slot asked for, the duck when none is, or None for the empty slot."""
    slot = 0 if order.ident is None else order.ident
    if slot == NO_CARD or slot not in range(len(CODES)):
        return None
    return decode_cardasobu(CODES[slot] + VERSION)


def cardasobu_entries() -> tuple[GameEntry, ...]:
    """Every card the game takes, in kana order."""
    return tuple(
        GameEntry(slot, _kind(slot), english, japanese)
        for slot, (english, japanese) in enumerate(NAMES)
        if slot != NO_CARD
    )


def cardasobu_named(typed: str) -> int:
    """A card typed by number, English name or Japanese name."""
    text = typed.strip()
    for entry in cardasobu_entries():
        if (
            text in {str(entry.ident), entry.japanese}
            or text.casefold() == entry.english.casefold()
        ):
            return entry.ident
    message = Said(
        f"no Card de Asobu card named {typed!r}",
        f"カードであそぶに {typed!r} という カードは ない",
    )
    raise ValueError(message)


def cardasobu_text(card: DatachCard) -> CardText:
    """The card's picture and the kana it teaches."""
    if card.ident == SEARCH:
        return CardText(NAMES[SEARCH], SEARCH_DETAIL, NO_HEADING, NO_HEADING)
    kana = KANA[card.ident]
    detail = (f"The card for {romanised(kana)}", f"「{kana}」の カード")
    return CardText(NAMES[card.ident], detail, NO_HEADING, NO_HEADING)
