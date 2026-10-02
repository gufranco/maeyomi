"""Densha Daishuugou! Card de Asobou, Sega Toys 2006: train cards for the Advanced Pico Beena.

Each card carries twelve bar places along one edge, and the game takes a card
only when its places spell one of its 50 trains or its test card. The list
comes from MAME's software list; the stripe layout was measured on the scans
of real cards, and every code was scanned in MAME, where the game brought up a
train for each listed card and stayed on its page for every other code tried.
The names are printed on the cards, read off those scans; card 16 keeps its
number, since MAME has no scan of it.
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


NAMES: Final[dict[int, Pair]] = {
    1: ("N700 Series", "N700系"),
    2: ("200 Series Yamabiko", "200系 やまびこ"),
    3: ("400 Series Tsubasa", "400系 つばさ"),
    4: ("E1 Series Max Tanigawa", "E1系 Maxたにがわ"),
    5: ("E2 Series Hayate", "E2系 はやて"),
    6: ("E3 Series Komachi", "E3系 こまち"),
    7: ("E4 Series Max Toki", "E4系 Maxとき"),
    8: ("255 Series View Sazanami", "255系 ビューさざなみ"),
    9: ("E257 Series Wakashio", "E257系 わかしお"),
    10: ("E653 Series Fresh Hitachi", "E653系 フレッシュひたち"),
    11: ("E351 Series Super Azusa", "E351系 スーパーあずさ"),
    12: ("253 Series Narita Express", "253系 成田エクスプレス"),
    13: ("251 Series Super View Odoriko", "251系 スーパービュー踊り子"),
    14: ("E257 Series Kaiji", "E257系 かいじ"),
    15: ("E257 Series Azusa", "E257系 あずさ"),
    17: ("185 Series Kusatsu", "185系 草津"),
    18: ("E26 Series Cassiopeia", "E26系 カシオペア"),
    19: ("24 Series Akebono", "24系 あけぼの"),
    20: ("24 Series Hokutosei and Yume Kukan", "24系 北斗星・夢空間"),
    21: ("E751 Series Tsugaru", "E751系 つがる"),
    22: ("485 Series Yamanami", "485系 やまなみ"),
    23: ("485 Series Seseragi", "485系 せせらぎ"),
    24: ("485 Series NO.DO.KA", "485系 NO.DO.KA"),
    25: ("14 Series Yutori", "14系 ゆとり"),
    26: ("485 Series Utage", "485系 宴"),
    27: ("485 Series Hana", "485系 華"),
    28: ("485 Series Kirakira Uetsu", "485系 きらきらうえつ"),
    29: ("485 Series New Nanohana", "485系 ニューなのはな"),
    30: ("485 Series Resort Express Yu", "485系 リゾートエクスプレス ゆう"),
    31: ("KiHa 48 Series View Coaster Kazekko", "キハ48系 びゅうコースター風っこ"),
    32: ("E926 East i", "E926形 イーストアイ"),
    33: ("C57 180 SL Ban'etsu Monogatari", "C57 180 SLばんえつ物語号"),
    34: ("D51 498", "D51 498"),
    35: ("E231 Series", "E231系"),
    36: ("E231 Series", "E231系"),
    37: ("209 Series", "209系"),
    38: ("201 Series", "201系"),
    39: ("E231 Series", "E231系"),
    40: ("205 Series", "205系"),
    41: ("EF55 1", "EF551"),
    42: ("Ticket card", "きっぷカード"),
    43: ("Wallet card", "おさいふカード"),
    44: ("Station card", "えきカード"),
    45: ("Rail card", "レールカード"),
    46: ("Parts card", "パーツカード"),
    47: ("Point card", "ポイントカード"),
    48: ("Scenery card", "ふうけいカード"),
    49: ("Inspection card", "てんけんカード"),
    50: ("Secret card", "シークレットカード"),
}


def _name(number: int) -> Pair:
    """A card's name as the card prints it, the test card, or its number."""
    if number == TEST_CARD:
        return TEST_NAME
    return NAMES.get(number, (f"Train card {number:02d}", f"でんしゃカード {number:02d}"))


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
