"""What Datach Yu Yu Hakusho calls its characters, techniques and items.

The Japanese names and the wording of each item's effect are the game's own,
copied off its analyzer screen, コエンマの判決, for a code of every character
with all four technique bits set and every item, run in MAME. The English is
the name the series uses in English, or this project's translation.
"""

from dataclasses import dataclass
from typing import Final

from maeyomi.said import Said


@dataclass(frozen=True, slots=True)
class Item:
    """An item card: its name, and what it does unless it only adds HP and SP."""

    english: str
    japanese: str
    effect: str
    effect_japanese: str


CHARACTERS: Final[dict[int, tuple[str, str]]] = {
    0: ("Yusuke", "ゆうすけ"),
    1: ("Kuwabara", "くわばら"),
    2: ("Kurama", "くらま"),
    3: ("Hiei", "ひえい"),
    4: ("Genkai", "げんかい"),
    5: ("Rinku", "リンク"),
    6: ("Zeru", "ゼル"),
    7: ("Chu", "チュウ"),
    8: ("Gama", "ガマ"),
    9: ("Touya", "トウヤ"),
    10: ("Jin", "ジン"),
    11: ("Black Momotaro", "クロモモタロウ"),
    12: ("Shishiwakamaru", "シシワカマル"),
    13: ("Old Suzuki", "オンジイ"),
    14: ("Karasu", "カラス"),
    15: ("Bui", "ブイ"),
    16: ("Bui, unarmoured", "ブイ"),
    17: ("Elder Toguro", "トグロ(アニ)"),
    18: ("Younger Toguro, 80 percent", "トグロ(オトウト)"),
    19: ("Younger Toguro, 100 percent", "トグロ(オトウト)"),
    20: ("SP Toguro", "SPトグロ"),
    21: ("Masked Fighter", "ふくめん"),
    22: ("Yoko Kurama", "ようこくらま"),
}

TECHNIQUE_NAMES: Final[dict[int, tuple[str, str]]] = {
    48: ("Demon power punch", "ようりょくのパンチ"),
    49: ("Battle aura", "バトルオーラ"),
    50: ("Throw", "なげ"),
    51: ("Super demon power punch", "ちょうようりょくのパンチ"),
    52: ("Super battle aura", "ちょうバトルオーラ"),
    53: ("Finger bullet", "しでん"),
    54: ("Spirit mirror reflection", "れいこうきょうはんしょう"),
    55: ("Demon-eating plant", "しょくようしょくぶつ"),
    56: ("Demon World mimosa", "まかいオジギソウ"),
    64: ("Spirit Gun", "レイガン"),
    65: ("Spirit Shotgun", "ショットガン"),
    66: ("Headbutt", "ヘッドバット"),
    67: ("Super Spirit Gun", "ちょうレイガン"),
    68: ("Spirit Sword", "れいきのけん"),
    69: ("Extending Spirit Sword", "のびるれいきのけん"),
    70: ("Rose Whip", "ローズウィップ"),
    71: ("Wind Flower Round Dance", "ふうかえんぶじん"),
    72: ("Shimaneki grass sword", "シマネキそうのけん"),
    73: ("Dragon of the Darkness Flame", "えんさつこくりゅうは"),
    74: ("Fist of the Mortal Flame", "じゃおうえんさつけん"),
    75: ("Purgatory flame", "えんさつれんごくしょう"),
    76: ("Devil yo-yo", "デビルヨーヨー"),
    77: ("Anti-air devil yo-yo", "たいくうデビルヨーヨー"),
    78: ("Flame demon ball", "かえんようじゅつのたま"),
    79: ("Flame demon punch", "かえんようじゅつのパンチ"),
    80: ("Linked demon ball", "れんさんようじゅつのたま"),
    81: ("Dash headbutt", "ダッシュヘッドバット"),
    82: ("Rapid punches", "れんぞくパンチ"),
    83: ("Battle makeup", "せんとうのしょう"),
    84: ("Supreme makeup", "ごくじょうのしょう"),
    85: ("Demon flute scattershot", "まてきさんだんしゅ"),
    86: ("Ice sword", "こおりのけん"),
    87: ("Asura whirlwind fist", "しゅらせんぷうけん"),
    88: ("Midair spinning punch", "くうちゅうせんかいパンチ"),
    89: ("Blast wind barrier", "ばくふうしょうへき"),
    90: ("Dash bite", "ダッシュかみつき"),
    91: ("Rock hell wave", "がんせきごくしょうは"),
    92: ("Skull burial", "ばくとどくしょくそう"),
    93: ("Demon wailing sword", "まこくめいざんけん"),
    94: ("Rainbow Cyclone", "レインボーサイクロン"),
    95: ("Trick Tornado", "トリックトルネード"),
    96: ("Trace eye", "トレースアイ"),
    97: ("Muddy bomb", "マッディボム"),
    98: ("Giant axe attack", "おおおのこうげき"),
    99: ("Giant axe whirlwind slash", "おおおののせんぷうぎり"),
    100: ("Battle guard", "バトルガード"),
    101: ("Dash punch", "ダッシュパンチ"),
    102: ("Needle stage", "はりぶたい"),
    103: ("Finger stage", "ゆびぶたい"),
}

ITEMS: Final[dict[int, Item]] = {
    32: Item("Keiko", "けいこ", "", ""),
    33: Item("Botan", "ぼたん", "", ""),
    34: Item("Atsuko", "あつこ", "", ""),
    35: Item("Shizuru", "しずる", "", ""),
    36: Item("Yukina", "ゆきな", "", ""),
    37: Item("Puu", "プーちゃん", "", ""),
    38: Item(
        "Juri",
        "ジュリ",
        "Removes the time limit from versus mode.",
        "これで、たいせんモードの タイムが むせいげんに なったぞ。",
    ),
    39: Item(
        "Koto",
        "コト",
        "Halves the time limit of versus mode.",
        "これで、たいせんモードの タイムが はんぶんに なったぞ。",
    ),
    40: Item(
        "Sakyo",
        "サキョウ",
        "Lets versus mode use the Toguro brothers.",
        "ほうびとして、たいせんモードで とぐろきょうだいの しようを ゆるしてやろう。",
    ),
    41: Item(
        "Koenma",
        "コエンマ",
        "Lets versus mode match a character against itself.",
        "おなじキャラでの たいせんを ゆるしてやろう。",
    ),
}


def bonus_text(hp: int, sp: int) -> tuple[str, str]:
    """What an item that adds HP and SP says it does, in the game's own wording."""
    parts = [(name, amount) for name, amount in (("HP", hp), ("SP", sp)) if amount]
    english = " and ".join(f"{amount} {name}" for name, amount in parts)
    japanese = "・".join(f"{name}が {amount}" for name, amount in parts)
    return f"Adds {english}.", f"このカードは、{japanese} アップするぞ。"


def card_named(typed: str) -> int:
    """The card a typed name or number means, or a ValueError naming what was not found."""
    wanted = typed.strip()
    if wanted.isdigit() and (int(wanted) in CHARACTERS or int(wanted) in ITEMS):
        return int(wanted)
    folded = wanted.casefold()
    names = {
        **CHARACTERS,
        **{ident: (item.english, item.japanese) for ident, item in ITEMS.items()},
    }
    for ident, (english, japanese) in names.items():
        if folded in {english.casefold(), japanese}:
            return ident
    message = Said(
        f"unknown Yu Yu Hakusho card {typed!r}; name a character or an item",
        f"幽遊白書に {typed!r} という カードは ない。キャラクターか アイテムの なまえに して",
    )
    raise ValueError(message)
