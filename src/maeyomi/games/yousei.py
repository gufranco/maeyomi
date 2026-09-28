"""The barcodes Doraemon: Nobita to Yousei no Kuni reads.

Epoch's Super Famicom game of 1993 reads a code in two places. On the
password screen ($C5:ED8A), $C0:9135 jumps on the check digit ($C0:91EA) and
tests one more digit; a check digit of 0 is always accepted and sets the
lives from two digits. On the item screen of the town map ($C0:9208), a
matching tenth and twelfth digit give one of eight gadgets ($C3:144E); the
first is the one Doraemon starts with, so it changes nothing. Confirmed
against the game in MAME on every code recorded on both screens.
"""

from typing import Final

from maeyomi.games.effects import Effect, EffectGame, Screen
from maeyomi.models.device import Device

LIVES: Final = 0
INVINCIBLE: Final = 2
NO_ENEMIES: Final = 9
NO_ENEMIES_CHECK: Final = 2
TESTS: Final = {
    1: (9, 2, 6),
    3: (7, 0, 3),
    4: (8, 9, 1),
    5: (6, 9, 5),
    6: (5, 1, 4),
    7: (11, 0, 8),
    8: (10, 4, 7),
    9: (5, 4, INVINCIBLE),
}
"""$C0:91EA: per check digit, the place from the start, the digit it needs, the result."""
GADGET: Final = 10
STARTING_GADGET: Final = 1
LAST_GADGET: Final = 8

PASSWORD: Final = (
    Effect(
        LIVES,
        ("99 lives", "ライフ 99"),
        (
            "The seventh and ninth digits set the lives; this card gives 99",
            "7けためと 9けためで ライフ、この カードは 99",
        ),
        "4977589297700",
    ),
    Effect(
        1,
        ("Ending", "エンディング"),
        ("Goes straight to the ending", "すぐに エンディング"),
        "4975441591454",
    ),
    Effect(
        INVINCIBLE,
        ("Invincible", "むてき"),
        ("Nothing hurts Doraemon", "ドラえもんが ダメージを うけない"),
        "4973043201719",
    ),
    Effect(
        3,
        ("Most attack", "こうげき さいだい"),
        ("Attack at its highest", "こうげきりょく さいだい"),
        "4969432079243",
    ),
    Effect(
        4,
        ("Full equipment", "そうび ぜんぶ"),
        ("Every gadget from the start", "さいしょから すべての どうぐ"),
        "4966619345146",
    ),
    Effect(
        5,
        ("Sound test", "サウンドテスト"),
        ("Opens the sound test", "サウンドテストを ひらく"),
        "4969549131735",
    ),
    Effect(
        6,
        ("Most life", "ライフ さいだい"),
        ("Starts with the most life", "ライフ さいだいで スタート"),
        "4985133742071",
    ),
    Effect(7, ("High jump", "ハイジャンプ"), ("Jumps higher", "たかく とべる"), "4913361485408"),
    Effect(8, ("Fast run", "はやく はしる"), ("Runs faster", "はやく はしれる"), "4967929081007"),
    Effect(
        NO_ENEMIES,
        ("No enemies", "てき なし"),
        ("The stages have no enemies", "てきが でない"),
        "4959320079042",
    ),
)
GADGETS: Final = (
    ("Air Pistol", "くうきピストル", "4979496582429"),
    ("Air Cannon", "くうきほう", "4957735643636"),
    ("Tornado Straw", "たつまきストロー", "4916707654742"),
    ("Shock-Wave Pistol", "しょうげきはピストル", "4954412625855"),
    ("Thunder Drum", "カミナリだいこ", "4925147436962"),
    ("Korobashiya", "ころばしや", "4982736397479"),
    ("Atarugan", "アタールガン", "4983171008982"),
)
ITEM_EFFECTS: Final = tuple(
    Effect(
        GADGET + number,
        (english, japanese),
        ("Gives and equips this gadget", "この どうぐを もらって そうび"),
        example,
        1,
    )
    for number, (english, japanese, example) in enumerate(GADGETS, start=STARTING_GADGET + 1)
)


def password_rule(digits: str) -> int | None:
    """What the password screen does with the digits, the check digit choosing the test."""
    code = [int(character) for character in digits]
    check = code[-1]
    if check == LIVES:
        return LIVES
    if check == NO_ENEMIES_CHECK:
        return NO_ENEMIES if code[6] == 0 and code[7] == 0 else None
    place, needed, result = TESTS[check]
    return result if code[place] == needed else None


def item_rule(digits: str) -> int | None:
    """The gadget a matching tenth and twelfth digit give, bar the one Doraemon starts with."""
    kind = int(digits[11])
    if STARTING_GADGET < kind <= LAST_GADGET and int(digits[9]) == kind:
        return GADGET + kind
    return None


YOUSEI: Final = EffectGame(
    device=Device.YOUSEI,
    rule=password_rule,
    effects=(*PASSWORD, *ITEM_EFFECTS),
    strongest=INVINCIBLE,
    screen=("Scan it on the title password screen", "タイトルの パスワード がめんで よませる"),
    more=(
        Screen(
            ("Scan it on the town map's item screen", "まちの マップの どうぐ がめんで よませる"),
            item_rule,
        ),
    ),
)
