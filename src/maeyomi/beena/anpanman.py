"""Soreike! Anpanman Card de Tanoshiku ABC, Sega Toys 2006: letter cards for the Beena.

The game reads 26 cards for the letters A to Z, 24 picture cards for English
words, and a test card that brings up the game's congratulations screen. The
list and each card's twelve bar places come from MAME's software list; the
names are printed on the cards, read off the scans in that list. Scanned in
MAME, the game took each card whatever its second place held, so that place is
left unread.
"""

from typing import Final

from maeyomi.beena.anpanman_tables import CARDS
from maeyomi.beena.stripe_game import StripeCard, StripeGame
from maeyomi.datach.game_types import Pair
from maeyomi.models.device import Device
from maeyomi.said import Said

STAT_KEYS: Final[tuple[str, ...]] = ()
LETTER_READINGS: Final = (
    "エー",
    "ビー",
    "シー",
    "ディー",
    "イー",
    "エフ",
    "ジー",
    "エイチ",
    "アイ",
    "ジェー",
    "ケー",
    "エル",
    "エム",
    "エヌ",
    "オー",
    "ピー",
    "キュー",
    "アール",
    "エス",
    "ティー",
    "ユー",
    "ブイ",
    "ダブリュー",
    "エックス",
    "ワイ",
    "ゼット",
)
LETTERS: Final[tuple[Pair, ...]] = tuple(
    zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", LETTER_READINGS, strict=True)
)
WORDS: Final[tuple[Pair, ...]] = (
    ("Apple", "りんご"),
    ("Banana", "バナナ"),
    ("Melon", "メロン"),
    ("Grapes", "ぶどう"),
    ("Carrot", "にんじん"),
    ("Onion", "たまねぎ"),
    ("Potato", "じゃがいも"),
    ("Tomato", "トマト"),
    ("Car", "くるま"),
    ("Truck", "トラック"),
    ("Bus", "バス"),
    ("Police car", "パトカー"),
    ("Ambulance", "きゅうきゅうしゃ"),
    ("Fire engine", "しょうぼうしゃ"),
    ("Airplane", "ひこうき"),
    ("Helicopter", "ヘリコプター"),
    ("Elephant", "ぞう"),
    ("Lion", "ライオン"),
    ("Zebra", "しまうま"),
    ("Hippopotamus", "かば"),
    ("Gorilla", "ゴリラ"),
    ("Tiger", "とら"),
    ("Bear", "くま"),
    ("Chimpanzee", "チンパンジー"),
)
LETTER_CARD: Final[Pair] = ("Letter card", "アルファベットの カード")
WORD_CARD: Final[Pair] = ("Word card", "ことばの カード")
TEST_CARD: Final[Pair] = ("Test card", "テストカード")
NAMES: Final[tuple[tuple[Pair, Pair], ...]] = (
    *((letter, LETTER_CARD) for letter in LETTERS),
    *((word, WORD_CARD) for word in WORDS),
    (TEST_CARD, TEST_CARD),
)
GAME: Final = StripeGame(
    device=Device.ANPANMAN,
    title=("Anpanman ABC", "アンパンマン ABC"),
    cards=tuple(
        StripeCard(number, code, *names) for (number, code), names in zip(CARDS, NAMES, strict=True)
    ),
    unknown=Said(
        "no Anpanman ABC card carries these bars",
        "アンパンマン ABC に この バーの カードは ない",
    ),
    ignored=frozenset({1}),
)
PRINTED: Final = GAME.cards
match: Final = GAME.match
decode_anpanman: Final = GAME.decode
build_anpanman: Final = GAME.build
anpanman_entries: Final = GAME.entries
anpanman_named: Final = GAME.named
anpanman_text: Final = GAME.text
