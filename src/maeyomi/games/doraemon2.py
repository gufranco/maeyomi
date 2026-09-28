"""The barcodes Doraemon 2: Nobita no Toys Land Daibouken reads.

Epoch's Super Famicom game of 1993 stores a code's digits last first
($C0:1A12) and reads it in two places. On the password screen, $C0:1A95 jumps
on the check digit ($C0:1AB4) and tests one more digit from $C0:1BAA; a check
digit of 0 or 2 is always accepted. In the Select item menu of a stage,
$C0:1BC8 gives a stage bonus when two digits agree, or else a secret tool.
Confirmed against the game in MAME on every code recorded on both screens.
"""

from typing import Final

from maeyomi.games.effects import Effect, EffectGame, Screen
from maeyomi.models.device import Device

WARP: Final = 0
LIVES: Final = 2
NO_ENEMIES: Final = 8
TESTS: Final = {1: (4, 3), 3: (1, 5), 4: (2, 9), 5: (7, 6), 6: (6, 2), 7: (3, 8), 9: (4, 0)}
"""$C0:1BAA: per check digit, the place counted from the end and the digit it needs."""
FIRST_TOOL: Final = 10
FIRST_BONUS: Final = 20
LAST_BONUS_DIGIT: Final = 6
LAST_TOOL_DIGIT: Final = 8

PASSWORD: Final = (
    Effect(
        WARP,
        ("Stage warp", "ステージ ワープ"),
        ("Starts at the stage the last two digits choose", "さいごの 2けたの ステージ から"),
        "4992174218090",
    ),
    Effect(
        1,
        ("Invincible", "むてき"),
        ("Nothing hurts Doraemon", "ドラえもんが ダメージを うけない"),
        "4975702934341",
    ),
    Effect(
        LIVES,
        ("99 lives", "ライフ 99"),
        (
            "The ninth and eleventh digits set the lives; this card gives 99",
            "9けためと 11けためで ライフ、この カードは 99",
        ),
        "4916433699932",
    ),
    Effect(3, ("High jump", "ハイジャンプ"), ("Jumps higher", "たかく とべる"), "4921178502553"),
    Effect(4, ("Fast run", "はやく はしる"), ("Runs faster", "はやく はしれる"), "4954981771984"),
    Effect(
        5,
        ("Ending", "エンディング"),
        ("Goes straight to the ending", "すぐに エンディング"),
        "4923267569065",
    ),
    Effect(
        6,
        ("Double attack", "こうげき 2ばい"),
        ("Every hit counts twice", "こうげきりょく 2ばい"),
        "4992622439336",
    ),
    Effect(
        7,
        ("Ten hearts", "ハート 10"),
        ("Starts with ten hearts", "ハート 10こ で スタート"),
        "4955702838337",
    ),
    Effect(
        NO_ENEMIES,
        ("No enemies", "てき なし"),
        ("The stages have no enemies", "てきが でない"),
        "4958480210418",
    ),
    Effect(
        9,
        ("Sound test", "サウンドテスト"),
        ("Opens the sound test", "サウンドテストを ひらく"),
        "4973043201719",
    ),
)
TOOLS: Final = (
    ("Shock Gun", "ショックガン", "4954009171451"),
    ("Shock-Wave Pistol", "しょうげきはピストル", "4939097252909"),
    ("Small Light", "スモールライト", "4999934333833"),
    ("Korobashiya", "ころばしや", "4916630494033"),
    ("Air Cannon", "くうきほう", "4906898575315"),
    ("Object Converter Gun", "ぶったいへんかんじゅう", "4910843646975"),
    ("Pencil Missile", "ペンシルミサイル", "4948358757169"),
    ("Atarugan", "アタールガン", "4986071838468"),
)
BONUSES: Final = (
    "4969091111469",
    "4954412625855",
    "4925953331239",
    "4900994846911",
    "4981985451055",
    "4905136365534",
)
MENU: Final = (
    *(
        Effect(
            FIRST_TOOL + number,
            (english, japanese),
            ("Gives and equips this secret tool", "この ひみつどうぐを もらって そうび"),
            example,
            1,
        )
        for number, (english, japanese, example) in enumerate(TOOLS, start=1)
    ),
    *(
        Effect(
            FIRST_BONUS + number,
            (f"Stage bonus {number}", f"ステージ ボーナス {number}"),
            (
                "Stored for the current stage only; what it does was not found",
                "いまの ステージだけの ボーナス、こうかは わかっていない",
            ),
            example,
            1,
        )
        for number, example in enumerate(BONUSES, start=1)
    ),
)


def password_rule(digits: str) -> int | None:
    """What the password screen does with the digits, read last first."""
    back = [int(character) for character in reversed(digits)]
    check = back[0]
    if check in {WARP, LIVES}:
        return check
    if check == NO_ENEMIES:
        return NO_ENEMIES if back[6] == 0 and back[4] == 1 else None
    place, needed = TESTS[check]
    return check if back[place] == needed else None


def menu_rule(digits: str) -> int | None:
    """A stage bonus when the fifth and seventh digits from the end agree, else a tool."""
    back = [int(character) for character in reversed(digits)]
    if 1 <= back[4] <= LAST_BONUS_DIGIT and back[4] == back[6]:
        return FIRST_BONUS + back[4]
    if 1 <= back[3] <= LAST_TOOL_DIGIT and back[3] == back[5]:
        return FIRST_TOOL + back[3]
    return None


DORAEMON2: Final = EffectGame(
    device=Device.DORAEMON2,
    rule=password_rule,
    effects=(*PASSWORD, *MENU),
    strongest=LIVES,
    screen=("Scan it on the title password screen", "タイトルの パスワード がめんで よませる"),
    more=(
        Screen(
            (
                "Scan it in a stage's Select item menu",
                "ステージの セレクト どうぐ メニューで よませる",
            ),
            menu_rule,
        ),
    ),
)
