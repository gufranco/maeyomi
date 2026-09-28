"""The barcodes Dragon Slayer: Eiyuu Densetsu II reads.

Falcom's role-playing game, released by Epoch for the Super Famicom in 1993,
reads a code in its menu loop ($C1:E2A5) and dispatches it at $C1:E43F by
where the player is. On the title menu the check digit and one or two more
digits choose a cheat: the ending, a status at its highest, doubled growth,
the monster list or the sound mode. In the field, the nine digits of $C1:E50F
followed by any three give the item those three number, modulo 256, and 999
opens every warp; a 7 last with a 1 to 4 in the sixth place uses a lamp, a
Bisna nut, a rest mushroom or the map without owning it. A code with an 8
last gives the chapter's item only once every warp is open, so from a fresh
game it does nothing. Confirmed against the game in MAME on both screens.
"""

from typing import Final

from maeyomi.games.effects import Effect, EffectGame, Screen
from maeyomi.models.device import Device

PREFIX: Final = "038438816"
WARP_DIGITS: Final = "999"
ITEMS_IN_BAG: Final = 256
SUN_SWORD_NUMBER: Final = 0x10
ENDING: Final = 1
FIRST_STATUS: Final = 2
DOUBLE_GROWTH: Final = 6
DOUBLE_STATUS: Final = 7
MONSTERS: Final = 8
ALL_STATUS: Final = 9
SOUND: Final = 10
WARP_ALL: Final = 20
FIRST_USE: Final = 21
ANY_ITEM: Final = 30
SUN_SWORD: Final = 31
USE_DIGITS: Final = "1234"

TITLE: Final = (
    Effect(
        ENDING,
        ("Ending", "エンディング"),
        ("Goes straight to the ending", "すぐに エンディング"),
        "4949420968001",
    ),
    Effect(
        2,
        ("Strength at its highest", "ちから さいだい"),
        ("Starts with the most strength", "ちから さいだいで スタート"),
        "4939876995102",
    ),
    Effect(
        3,
        ("Intelligence at its highest", "かしこさ さいだい"),
        ("Starts with the most intelligence", "かしこさ さいだいで スタート"),
        "4966192164202",
    ),
    Effect(
        4,
        ("Agility at its highest", "すばやさ さいだい"),
        ("Starts with the most agility", "すばやさ さいだいで スタート"),
        "4949318243302",
    ),
    Effect(
        5,
        ("Luck at its highest", "うんの よさ さいだい"),
        ("Starts with the most luck", "うんの よさ さいだいで スタート"),
        "4951430848402",
    ),
    Effect(
        DOUBLE_GROWTH,
        ("Double experience and gold", "けいけんちと ゴールド 2ばい"),
        ("Every fight pays twice", "たたかいの ほうびが 2ばい"),
        "4915079061363",
    ),
    Effect(
        DOUBLE_STATUS,
        ("Double status gains", "のうりょくの のび 2ばい"),
        ("Each level raises the status twice as much", "レベルアップの のびが 2ばい"),
        "4945210092383",
    ),
    Effect(
        MONSTERS,
        ("Monster list", "モンスター リスト"),
        ("Opens the list of monsters", "モンスターの いちらんを ひらく"),
        "4989564891544",
    ),
    Effect(
        ALL_STATUS,
        ("Every status at its highest", "すべての のうりょく さいだい"),
        ("Starts with every status at its highest", "すべての のうりょく さいだいで スタート"),
        "4900000040104",
    ),
    Effect(
        SOUND,
        ("Sound mode", "サウンド モード"),
        ("Opens the sound mode", "サウンド モードを ひらく"),
        "4945069037115",
    ),
)
FIELD: Final = (
    Effect(
        WARP_ALL,
        ("Every warp", "すべての ワープ"),
        ("Opens every warp destination", "すべての ワープさきが ひらく"),
        "0384388169994",
        1,
    ),
    Effect(
        FIRST_USE,
        ("Use a lamp", "ランプを つかう"),
        ("Uses a lamp without owning one", "もっていない ランプを つかう"),
        "4956310970747",
        1,
    ),
    Effect(
        22,
        ("Use a Bisna nut", "ビスナの みを つかう"),
        ("Uses a Bisna nut without owning one", "もっていない ビスナの みを つかう"),
        "4946327948617",
        1,
    ),
    Effect(
        23,
        ("Use a rest mushroom", "やすらぎの キノコを つかう"),
        ("Uses a rest mushroom without owning one", "もっていない キノコを つかう"),
        "4931730936597",
        1,
    ),
    Effect(
        24,
        ("Use the map", "ちずを つかう"),
        ("Uses the map without owning it", "もっていない ちずを つかう"),
        "4910246357287",
        1,
    ),
    Effect(
        ANY_ITEM,
        ("An item by number", "ばんごうの アイテム"),
        (
            "Gives the item the last three digits number, modulo 256",
            "さいごの 3けたの ばんごうの アイテム",
        ),
        "0384388160014",
        1,
    ),
    Effect(
        SUN_SWORD,
        ("Sun Holy Sword", "たいようの せいけん"),
        (
            "Gives the Sun Holy Sword, the last weapon in the game's list",
            "たいようの せいけんを もらう",
        ),
        "0384388160168",
        1,
    ),
)


def title_rule(digits: str) -> int | None:
    """What the title menu does with the digits, the check digit choosing the test."""
    check = digits[12]
    if check == "2" and digits[11] == "0" and digits[10] in USE_DIGITS:
        return FIRST_STATUS + int(digits[10]) - 1
    tests = (
        (check == "1" and digits[10:12] == "00", ENDING),
        (check == "3" and digits[3] == "5" and digits[9] == "1", DOUBLE_GROWTH),
        (check == "3" and digits[3] == "5" and digits[9] == "2", DOUBLE_STATUS),
        (check == "4" and digits[8] == "9", MONSTERS),
        (check == "4" and digits[8] == "4" and digits[11] == "0", ALL_STATUS),
        (check == "5" and digits[7] == "0", SOUND),
    )
    return next((effect for passed, effect in tests if passed), None)


def field_rule(digits: str) -> int | None:
    """What the field menu does with the digits, from a fresh game."""
    if digits.startswith(PREFIX):
        tail = digits[9:12]
        if tail == WARP_DIGITS:
            return WARP_ALL
        return SUN_SWORD if int(tail) % ITEMS_IN_BAG == SUN_SWORD_NUMBER else ANY_ITEM
    if digits[12] == "7" and digits[5] in USE_DIGITS:
        return FIRST_USE + int(digits[5]) - 1
    return None


DSLAYER2: Final = EffectGame(
    device=Device.DSLAYER2,
    rule=title_rule,
    effects=(*TITLE, *FIELD),
    strongest=ALL_STATUS,
    screen=("Scan it on the title menu", "タイトル メニューで よませる"),
    more=(Screen(("Scan it in the field menu", "フィールドの メニューで よませる"), field_rule),),
)
