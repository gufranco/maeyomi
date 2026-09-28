"""The barcodes Doraemon 3: Nobita to Toki no Hougyoku reads.

Epoch's Super Famicom game of 1994 stores a code's digits last first
($CC:D622) and reads it in two places. On the password screen, $CC:D647 tests
the check digit with one more digit; a check digit of 0 or 2 is always
accepted and sets the lives or the world from the digits. In play, the Select
equipment menu ($CC:D5FE) gives a weapon or protector when the second and
fourth digits from the end agree, or one of eight items when the third and
fifth do, which wins. Confirmed against the game in MAME on every code
recorded on both screens.
"""

from typing import Final

from maeyomi.games.effects import Effect, EffectGame, Screen
from maeyomi.models.device import Device

LIVES: Final = 1
WORLD: Final = 10
WORLD_CHECK: Final = 2
TESTS: Final = (
    (2, 7, 8, 0),
    (3, 8, 3, 8),
    (4, 4, 3, 7),
    (5, 1, 5, 3),
    (6, 9, 2, 3),
    (7, 5, 2, 4),
    (8, 3, 4, 5),
    (9, 6, 1, 0),
)
"""$CC:D647: the result, the check digit it needs, a place from the end and its digit."""
IN_PLAY: Final = 100
GEAR: Final = (1, 3, 2, 5, 4, 6, 7, 8, 9, 10)
"""$CC:0F69: the item each matching digit 0 to 9 gives, before the item pairs."""
ITEM_OFFSET: Final = 10
LAST_ITEM_DIGIT: Final = 8

PASSWORD: Final = (
    Effect(
        LIVES,
        ("Lives from the code", "コードの ライフ"),
        (
            "The eleventh digit sets the lives, 3 at least; this card gives 9",
            "11けためで ライフ、3より すくなく ならない、この カードは 9",
        ),
        "4955944610920",
    ),
    Effect(
        2,
        ("Ending", "エンディング"),
        ("Goes straight to the ending", "すぐに エンディング"),
        "4903075736927",
    ),
    Effect(
        3,
        ("Invincible", "むてき"),
        ("Nothing hurts Doraemon", "ドラえもんが ダメージを うけない"),
        "4948212378998",
    ),
    Effect(
        4,
        ("All weapons", "ぶき ぜんぶ"),
        ("Starts with every weapon", "すべての ぶきで スタート"),
        "4929219637844",
    ),
    Effect(
        5,
        ("All protectors", "ぼうぐ ぜんぶ"),
        ("Starts with every protector", "すべての ぼうぐで スタート"),
        "4963660365321",
    ),
    Effect(
        6, ("Music", "おんがく"), ("Opens the music player", "おんがくを きく"), "4945645873359"
    ),
    Effect(
        7,
        ("Most hearts", "ハート さいだい"),
        ("Starts with the most hearts", "ハート さいだいで スタート"),
        "4919848151415",
    ),
    Effect(8, ("Fast run", "はやく はしる"), ("Runs faster", "はやく はしれる"), "4970513253933"),
    Effect(
        9,
        ("Safe on spikes", "トゲで へいき"),
        ("Spikes do no harm", "トゲに さわっても へいき"),
        "4977273866106",
    ),
    Effect(
        WORLD,
        ("Later world", "あとの ワールド"),
        (
            "The twelfth digit chooses the world; this card starts world 5",
            "12けためで ワールド、この カードは ワールド 5",
        ),
        "4525066031042",
    ),
)
ITEMS: Final = (
    ("Boomerang, level 3", "ブーメラン L3", "4968180960803"),
    ("Air Cannon, level 3", "くうきほう L3", "4979496582429"),
    ("Koekatamarin, level 3", "コエカタマリン L3", "4973043201719"),
    ("Mic, level 3", "マイク L3", "4979612144647"),
    ("Small Light, level 3", "スモールライト L3", "4957735643636"),
    ("Styrofoam Sprinkle", "スチロールふりかけ", "4954412625855"),
    ("Ganjou, level 2", "ガンジョウ L2", "4942949206661"),
    ("Typhoon Armour", "たいふうのよろい", "4982736397479"),
    ("Iron Sprinkle", "てつふりかけ", "4934217178183"),
    ("Barrier Point", "バリヤーポイント", "4928260979996"),
    ("15 Shooting-Star Hammers", "ながれぼしトンカチ 15こ", "4986891712184"),
    ("15 Korobashiya", "ころばしや 15こ", "4993764625298"),
    ("15 Air-Block Makers", "くうきブロックせいぞうき 15こ", "4992622439336"),
    ("15 Hirari Mantles", "ヒラリマント 15こ", "4922970241459"),
    ("Nine lives", "ライフ 9", "4923796551548"),
    ("Lucky Glove", "こううんのてぶくろ", "4951217267617"),
    ("Heart Pot", "ハートのつぼ", "4919195673769"),
    ("Jewel Pot", "ほうせきのつぼ", "4956977781885"),
)
IN_PLAY_EFFECTS: Final = tuple(
    Effect(
        IN_PLAY + number,
        (english, japanese),
        ("Given in play from the Select equipment menu", "セレクトの そうび メニューで もらえる"),
        example,
        1,
    )
    for number, (english, japanese, example) in enumerate(ITEMS, start=1)
)


def password_rule(digits: str) -> int | None:
    """What the password screen does with the digits, read last first."""
    back = [int(character) for character in reversed(digits)]
    if back[0] == 0:
        return LIVES
    return next(
        (
            result
            for result, check, place, needed in TESTS
            if back[0] == check and back[place] == needed
        ),
        WORLD if back[0] == WORLD_CHECK else None,
    )


def play_rule(digits: str) -> int | None:
    """The equipment menu's item: a matching third and fifth digit, else second and fourth."""
    back = [int(character) for character in reversed(digits)]
    if 1 <= back[4] <= LAST_ITEM_DIGIT and back[4] == back[2]:
        return IN_PLAY + ITEM_OFFSET + back[4]
    if back[3] == back[1]:
        return IN_PLAY + GEAR[back[3]]
    return None


DORAEMON3: Final = EffectGame(
    device=Device.DORAEMON3,
    rule=password_rule,
    effects=(*PASSWORD, *IN_PLAY_EFFECTS),
    strongest=WORLD,
    screen=("Scan it on the title password screen", "タイトルの パスワード がめんで よませる"),
    more=(
        Screen(
            (
                "Scan it in play, in the Select equipment menu",
                "あそびの とちゅう、セレクトの そうび メニューで よませる",
            ),
            play_rule,
        ),
    ),
)
