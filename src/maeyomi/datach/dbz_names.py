"""The names and effects Datach Dragon Ball Z shows for each fighter and item id.

The Japanese is what the game prints on its barcode data screen, read from the
game running in MAME, in the game's own kana. The English is this project's
translation. Later forms of Frieza and Cell carry the same name as the first,
because the game names them the same.
"""

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class DbzItem:
    """An item's name and what the game says it does, in both languages."""

    english: str
    japanese: str
    effect: str
    effect_japanese: str


FIGHTERS: Final[dict[int, tuple[str, str]]] = {
    0: ("Goku", "ゴクウ"),
    1: ("Krillin", "クリリン"),
    2: ("Yamcha", "ヤムチャ"),
    3: ("Tien", "テンシンハン"),
    4: ("Chiaotzu", "チャオズ"),
    5: ("Piccolo", "ピッコロ"),
    6: ("Gohan", "ゴハン"),
    7: ("Vegeta", "ベジータ"),
    8: ("Trunks", "トランクス"),
    9: ("Super Saiyan Goku", "Sゴクウ"),
    10: ("Super Saiyan Gohan", "Sゴハン"),
    11: ("Super Saiyan Vegeta", "Sベジータ"),
    12: ("Super Saiyan Trunks", "Sトランクス"),
    13: ("Super Piccolo", "Sピッコロ"),
    16: ("Frieza", "フリーザ"),
    17: ("Cell", "セル"),
    18: ("Raditz", "ラディッツ"),
    19: ("Ginyu", "ギニュー"),
    20: ("Zarbon", "ザーボン"),
    21: ("Saibaman", "サイバイマン"),
    22: ("Android 16", "16ごう"),
    23: ("Android 17", "17ごう"),
    24: ("Android 18", "18ごう"),
    25: ("Android 19", "19ごう"),
    26: ("Cell", "セル"),
    27: ("Frieza", "フリーザ"),
    28: ("Frieza", "フリーザ"),
    29: ("Frieza", "フリーザ"),
    30: ("Cell", "セル"),
}


def _dragon_ball(stars: int) -> DbzItem:
    """One of the seven Dragon Balls, which the game only reports as found."""
    return DbzItem(
        f"Dragon Ball, {stars} star",
        f"ドラゴンボール {stars}しんちゅう",
        f"Finds the {stars}-star Dragon Ball",
        f"ドラゴンボール{stars}しんちゅうを みつけた",
    )


def _porunga(level: int) -> DbzItem:
    """Porunga, who opens special moves up to one level."""
    return DbzItem(
        f"Porunga, level {level}",
        f"ポルンガ レベル{level}",
        f"Special moves of level {level} can be used",
        f"レベル{level}の ひっさつわざが つかえる",
    )


ITEMS: Final[dict[int, DbzItem]] = {
    32: DbzItem(
        "Recovery capsule",
        "かいふくカプセル",
        "Restores 20% of HP, BP and DP",
        "HP BP DPを 20パーセント かいふく",
    ),
    33: DbzItem(
        "Senzu bean", "せんず", "Fully restores HP, BP and DP", "HP BP DPを かんぜんかいふく"
    ),
    34: DbzItem("Korin", "カリンさま", "Adds 6000 to HP, BP and DP", "HP BP DPに 6000P プラス"),
    35: DbzItem("Shenron", "シェンロン", "Adds 6000 to HP, BP and DP", "HP BP DPに 6000P プラス"),
    36: DbzItem("Bulma", "ブルマ", "Restores 25% of HP", "HPを 25パーセント かいふく"),
    37: DbzItem("Dende", "デンデ", "Fully restores HP", "HPを かんぜんかいふく"),
    38: DbzItem("Master Roshi", "かめせんにん", "Adds 6000 to HP", "HPに 6000P プラス"),
    39: DbzItem("Kami", "かみさま", "Adds 12000 to HP", "HPに 12000P プラス"),
    40: DbzItem("Mr. Popo", "ミスターポポ", "Restores 25% of BP", "BPを 25パーセント かいふく"),
    41: DbzItem("King Kai", "かいおうさま", "Fully restores BP", "BPを かんぜんかいふく"),
    42: DbzItem("King Yemma", "エンマだいおう", "Adds 6000 to BP", "BPに 6000P プラス"),
    43: DbzItem("Guru", "さいちょうろう", "Adds 12000 to BP", "BPに 12000P プラス"),
    44: DbzItem("Battle suit", "バトルスーツ", "Raises DP by 50%", "DPを 50パーセント アップ"),
    45: DbzItem(
        "Ultra divine water",
        "ちょうしんすい",
        "Raises BP and DP by 50%",
        "BPと DPを 50パーセント アップ",
    ),
    46: DbzItem(
        "Chi-Chi", "チチ", "Lowers the rival's BP by 20%", "あいての BPを 20パーセント ダウン"
    ),
    47: DbzItem(
        "Yajirobe",
        "ヤジロベー",
        "Lowers the rival's BP by 40%",
        "あいての BPを 40パーセント ダウン",
    ),
    48: DbzItem("Puar", "プーアル", "Makes your moves quicker", "おぬしの うごきを すばやく"),
    49: DbzItem(
        "Sea turtle", "うみガメ", "Makes the rival's moves slower", "あいての うごきを にぶく"
    ),
    50: DbzItem(
        "Gregory",
        "グレゴリー",
        "Raises your special move level by one",
        "ひっさつわざの レベルを 1ランク アップ",
    ),
    51: DbzItem(
        "Oolong",
        "ウーロン",
        "Lowers the rival's special move level by one",
        "あいての ひっさつわざの レベルを 1ランク ダウン",
    ),
    52: DbzItem(
        "Bubbles",
        "バブルス",
        "Takes no damage from one beam",
        "こうせんを うけても 1かいだけ ダメージなし",
    ),
    53: DbzItem(
        "Grandpa Gohan",
        "ゴクウの じいちゃん",
        "Seals the rival's special moves for the round",
        "そのラウンドのみ あいての ひっさつわざを ふうじる",
    ),
    54: DbzItem(
        "Fortuneteller Baba",
        "うらないババ",
        "Special moves cost no BP",
        "ひっさつわざを つかっても BPが へらない",
    ),
    55: DbzItem(
        "Dr. Brief",
        "ブリーフはかせ",
        "Makes the round timer half as long again",
        "ラウンドの タイマーを 1/2 えんちょう",
    ),
    56: DbzItem(
        "Bulma's mother",
        "ブルマの はは",
        "Cuts the round timer by half",
        "ラウンドの タイマーを 1/2 たんしゅく",
    ),
    57: DbzItem(
        "Ox-King",
        "ぎゅうまおう",
        "Seals both sides' items for the round",
        "そのラウンドのみ りょうほうの アイテムを ふういん",
    ),
    58: DbzItem(
        "Launch",
        "ランチ",
        "Swaps your fighter during a battle",
        "おぬしの せんしを バトルちゅう こうたい",
    ),
    59: DbzItem(
        "Hoi-Poi capsule",
        "ホイポイカプセル",
        "One of five items, unknown until used",
        "5つの タイプの アイテム つかうまで わからない",
    ),
    **{60 + stars: _dragon_ball(stars) for stars in range(1, 8)},
    **{67 + level: _porunga(level) for level in range(1, 5)},
}


def fighter_name(identifier: int) -> tuple[str, str] | None:
    """A fighter's English and Japanese name, or None for an id the game never produces."""
    return FIGHTERS.get(identifier)


def item_entry(identifier: int) -> DbzItem | None:
    """An item's names and effect, or None for an id the game never produces."""
    return ITEMS.get(identifier)


def character_id(value: str) -> int:
    """A fighter or item id from its number or its English or Japanese name.

    Frieza and Cell have several forms under one name; the name picks the first,
    and the game turns it into a later form when its numbers reach one.
    """
    wanted = value.strip().casefold()
    if wanted.isdigit():
        return int(wanted)
    found = [identifier for identifier, names in _all_names() if wanted in names]
    if not found:
        message = f"unknown character {value!r}; give a name the game shows or an id"
        raise ValueError(message)
    return min(found)


def _all_names() -> list[tuple[int, set[str]]]:
    """Every id with the names it answers to, folded for comparison."""
    fighters = [(key, {name.casefold() for name in names}) for key, names in FIGHTERS.items()]
    items = [
        (key, {item.english.casefold(), item.japanese.casefold()}) for key, item in ITEMS.items()
    ]
    return fighters + items
