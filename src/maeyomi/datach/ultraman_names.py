"""What Datach Ultraman Club calls each type it reads.

The Japanese names are the game's own, copied off its analyzer screen, which
prints the name of the type a barcode reads as; each was photographed from the
game running in MAME. The English names are the ones the Ultraman series uses
in English, or this project's translation where a name has none.
"""

from typing import Final

from maeyomi.said import Said

NAMES: Final[dict[int, tuple[str, str]]] = {
    0: ("Ultraman", "ウルトラマン"),
    1: ("Ultraman Jack", "ジャック"),
    2: ("Ultraseven", "セブン"),
    3: ("Zoffy", "ゾフィー"),
    4: ("Ultraman Ace", "エース"),
    5: ("Ultraman Taro", "タロウ"),
    6: ("Ultraman Leo", "レオ"),
    7: ("Astra", "アストラ"),
    8: ("Zetton", "ゼットン"),
    9: ("Bemstar", "ベムスター"),
    10: ("Eleking", "エレキング"),
    11: ("Garamon", "ガラモン"),
    12: ("Alien Baltan", "バルタン"),
    13: ("Alien Dada", "ダダ"),
    14: ("Alien Metron", "メトロン"),
    15: ("Alien Icarus", "イカルス"),
    16: ("Pigmon", "ピグモン"),
    17: ("Kanegon", "カネゴン"),
    18: ("Red King", "レッドキング"),
    19: ("Seabozu", "シーボーズ"),
    20: ("Pestar", "ペスター"),
    21: ("Seamons", "シーモンス"),
    22: ("Seagorath", "シーゴラス"),
    23: ("Takkong", "タッコング"),
    24: ("Gudon", "グドン"),
    25: ("Twin Tail", "ツインテール"),
    26: ("Antlar", "アントラー"),
    27: ("Gomora", "ゴモラ"),
    32: ("Ultraman King", "キング"),
    33: ("Father of Ultra", "ウルトラのちち"),
    34: ("Mother of Ultra", "ウルトラのはは"),
    35: ("Pandon", "パンドン"),
    36: ("Enmargo", "エンマーゴ"),
    37: ("Woo", "ウー"),
    38: ("Namegon", "ナメゴン"),
    39: ("Gabora", "ガボラ"),
    40: ("Alien Pitt", "ピットせいじん"),
    41: ("Miclas", "ミクラス"),
    42: ("Gandar", "ガンダー"),
    43: ("Dinosaur Tank", "きょうりゅうセンシャ"),
    44: ("Alien Zarab", "ザラブせいじん"),
    45: ("Space Beast Gyeron", "ギエロンせいじゅう"),
    46: ("Pegila", "ペギラ"),
    47: ("Neronga", "ネロンガ"),
    48: ("Ragon", "ラゴン"),
    49: ("Keelah", "キーラ"),
    50: ("Alien Nackle", "ナックルせいじん"),
    51: ("Skydon", "スカイドン"),
    52: ("Alien Pegassa", "ペガッサせいじん"),
    53: ("Alien Hipporit", "ヒッポリトせいじん"),
    54: ("Gavadon", "ガヴァドン"),
}


def type_named(typed: str) -> int:
    """The type a typed name or number means, or a ValueError naming the ones there are."""
    wanted = typed.strip()
    if wanted.isdigit() and int(wanted) in NAMES:
        return int(wanted)
    folded = wanted.casefold()
    for identifier, (english, japanese) in NAMES.items():
        if folded in {english.casefold(), japanese}:
            return identifier
    known = ", ".join(english for english, _ in NAMES.values())
    message = Said(
        f"unknown Ultraman Club type {typed!r}; known types: {known}",
        f"ウルトラマン倶楽部に {typed!r} という タイプは ない。つかえるのは {known}",
    )
    raise ValueError(message)
