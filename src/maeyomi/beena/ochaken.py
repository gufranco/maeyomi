"""TV Ocha-Ken, Sega Toys 2005: a machine that reads Ocha-Ken cards and plays on the television.

The machine boots the Advanced Pico Beena's BIOS and keeps its game in flash,
and its RD1831 reader takes cards with sixteen bar places along one edge. The
game takes a card only when its places spell one of its 50 cards. The list
comes from MAME's tvochken software list; the stripe layout was measured on
the scans of real cards there, and every code was scanned in MAME in the
room a new day starts in, where the game answered each listed card and stayed
in the room for every other code tried. The names are printed on the cards,
read off those scans.
"""

from typing import Final

from maeyomi.beena.ochaken_tables import CARDS
from maeyomi.beena.stripe_game import StripeCard, StripeGame
from maeyomi.datach.game_types import Pair
from maeyomi.models.device import Device
from maeyomi.said import Said

STAT_KEYS: Final[tuple[str, ...]] = ()
DETAIL: Final[Pair] = ("Ocha-Ken card", "お茶犬の カード")

NAMES: Final[dict[int, Pair]] = {
    1: ("Japanese tea", "和のお茶"),
    2: ("Western tea", "洋のお茶"),
    3: ("All kinds of drinks", "色々なのみもの"),
    4: ("Japanese sweets", "和菓子"),
    5: ("Western sweets", "洋菓子"),
    6: ("Snacks", "スナック菓子"),
    7: ("Japanese food", "日本料理"),
    8: ("Western food", "西洋料理"),
    9: ("Chinese food", "中華料理"),
    10: ("Change the interior", "内装をかえる"),
    11: ("Change the furniture", "家具をかえる"),
    12: ("Change the ornaments", "小物をかえる"),
    13: ("Medicine", "のみ薬"),
    14: ("Injection", "注射"),
    15: ("Horoscope", "星占い"),
    16: ("Card fortune", "カードおみくじ"),
    17: ("Ocha-Ken fortune", "お茶犬占い"),
    18: ("Memory game", "神経衰弱"),
    19: ("Picture slot machine", "絵合わせスロット"),
    20: ("Find Ryoku!", "リョクをさがせ!"),
    21: ("Go to the garden", "庭に行く"),
    22: ("Go to the veranda", "縁側に行く"),
    23: ("Go to the park", "公園に行く"),
    24: ("Go to the main street", "大通りに行く"),
    25: ("Go to the shopping street", "商店街に行く"),
    26: ("Go to the meadow", "原っぱに行く"),
    27: ("Go to the flower field", "お花畑に行く"),
    28: ("Go to the riverside", "川辺に行く"),
    29: ("Go to the seaside", "海辺に行く"),
    30: ("Go to the hot spring", "温泉に行く"),
    31: ("Dress-up", "きせかえあそび"),
    32: ("Good night", "おやすみなさい"),
    33: ("Clean the room", "部屋そうじ"),
    34: ("Clean the garden", "庭そうじ"),
    35: ("Watch TV", "テレビをみる"),
    36: ("Go to the toilet", "トイレに行く"),
    37: ("Read the letters", "手紙を読む"),
    38: ("Look at the items", "アイテムを見る"),
    39: ("Shall we make good tea?", "おいしいお茶いれよう?"),
    40: ("Pet Ryoku", "リョクをなでなで"),
    41: ("Ryoku, the green tea dog", "緑茶犬〈リョク〉"),
    42: ("Earl, the black tea dog", "紅茶犬〈アール〉"),
    43: ("Ron, the oolong tea dog", "烏龍茶犬〈ロン〉"),
    44: ("Hana, the herb tea dog", "ハーブ茶犬〈ハナ〉"),
    45: ("Chai, the black tea dog", "紅茶犬〈チャイ〉"),
    46: ("Cafe, the coffee dog", "コーヒー犬〈カフェ〉"),
    47: ("Muha, the barley tea dog", "麦茶犬〈ムハ〉"),
    48: ("Sakura, the cherry blossom tea cat", "さくら茶猫〈サクラ〉"),
    49: ("Ran, the lavender tea cat", "ラベンダー茶猫〈ラン〉"),
    50: ("Min, the jasmine tea cat", "ジャスミン茶猫〈ミン〉"),
}

GAME: Final = StripeGame(
    device=Device.OCHAKEN,
    title=("TV Ocha-Ken", "テレビとお茶札 お茶犬「ほっ」と生活"),
    cards=tuple(StripeCard(number, code, NAMES[number], DETAIL) for number, code in CARDS),
    unknown=Said(
        "no TV Ocha-Ken card carries these bars",
        "テレビとお茶札 お茶犬「ほっ」と生活に この バーの カードは ない",
    ),
)
PRINTED: Final = GAME.cards
match: Final = GAME.match
decode_ochaken: Final = GAME.decode
build_ochaken: Final = GAME.build
ochaken_entries: Final = GAME.entries
ochaken_named: Final = GAME.named
ochaken_text: Final = GAME.text
