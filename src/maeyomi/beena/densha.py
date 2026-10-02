"""Densha Daishuugou! Card de Asobou, Sega Toys 2006: train cards for the Advanced Pico Beena.

Each card carries twelve bar places along one edge, and the game takes a card
only when its places spell one of its 50 trains or its test card. The list
comes from MAME's software list; the stripe layout was measured on the scans
of real cards, and every code was scanned in MAME, where the game brought up a
train for each listed card and stayed on its page for every other code tried.
"""

from typing import Final

from maeyomi.beena.densha_tables import CARDS
from maeyomi.beena.stripe_game import StripeCard, StripeGame
from maeyomi.datach.game_types import Pair
from maeyomi.models.device import Device
from maeyomi.said import Said

STAT_KEYS: Final[tuple[str, ...]] = ()
TEST_CARD: Final = 51
DETAIL: Final[Pair] = ("Train card", "でんしゃの カード")
TEST_NAME: Final[Pair] = ("Test card", "テストカード")


def _name(number: int) -> Pair:
    """A card's name: the test card, or its number."""
    if number == TEST_CARD:
        return TEST_NAME
    return f"Train card {number:02d}", f"でんしゃカード {number:02d}"


GAME: Final = StripeGame(
    device=Device.DENSHA,
    title=("Densha Daishuugou", "でんしゃだいしゅうごう"),
    cards=tuple(StripeCard(number, code, _name(number), DETAIL) for number, code in CARDS),
    unknown=Said(
        "no Densha Daishuugou card carries these bars",
        "でんしゃだいしゅうごうに この バーの カードは ない",
    ),
)
PRINTED: Final = GAME.cards
match: Final = GAME.match
decode_densha: Final = GAME.decode
build_densha: Final = GAME.build
densha_entries: Final = GAME.entries
densha_named: Final = GAME.named
densha_text: Final = GAME.text
