"""The barcodes Donald Duck no Mahou no Boushi reads on its password screen.

Epoch's Super Famicom game of 1995 reads a code on its title password screen
through $C2:D451, which jumps on the check digit ($C2:D47C). A 2 in the ninth
place opens the stage or scene the check digit names ($C2:D52D); a check
digit of 4 or 5 is refused. Two codes under Epoch's own prefix are the only
way to the staff roll and to the hat shop, $C2:D555 and $C2:D54B. The type
chosen loads its record from $C2:C507. Confirmed against the game in MAME on
247 codes.
"""

from typing import Final

from maeyomi.games.effects import Effect, EffectGame
from maeyomi.models.device import Device

MARKER_PLACE: Final = 8
MARKER: Final = "2"
REFUSED: Final = frozenset("45")
EPOCH_PREFIX: Final = "4905040"
EPOCH_PRODUCT: Final = "4905040098"
STAFF_ROLL: Final = 7
HAT_SHOP: Final = 5

EFFECTS: Final = (
    Effect(
        0,
        ("Sky stage, full power", "そらの ステージ、パワー まんたん"),
        ("A playable sky stage with every power and 12 hearts", "すべての パワーと ハート12こ"),
        "4906274126940",
    ),
    Effect(
        1,
        ("Forest stage", "もりの ステージ"),
        ("The old man's scene, then the forest", "おじいさんの あと もりへ"),
        "4934626721871",
    ),
    Effect(
        2,
        ("Snow stage", "ゆきの ステージ"),
        ("The field scene, then the snow", "のはらの あと ゆきへ"),
        "4960591721752",
    ),
    Effect(
        3,
        ("Gear stage", "はぐるまの ステージ"),
        ("The sold-out hat shop, then the gears", "うりきれの ぼうしやの あと はぐるまへ"),
        "4991976820173",
    ),
    Effect(
        HAT_SHOP,
        ("Gear stage, by Epoch's code", "はぐるまの ステージ、エポックの コード"),
        (
            "The same as the gear stage, from Epoch's own barcode",
            "エポックの バーコードで はぐるまへ",
        ),
        "4905040098290",
    ),
    Effect(
        6,
        ("Castle stage", "おしろの ステージ"),
        ("The castle gate, then the castle", "おしろの もんの あと おしろへ"),
        "4963321326296",
    ),
    Effect(
        STAFF_ROLL,
        ("Staff roll", "スタッフロール"),
        ("Plays the staff roll", "スタッフロールを みる"),
        "4905040228437",
    ),
    Effect(
        8,
        ("Birthday ending", "たんじょうび エンディング"),
        (
            "The birthday party, then the staff roll",
            "たんじょうび パーティーの あと スタッフロール",
        ),
        "4918927022578",
    ),
    Effect(
        9,
        ("King's ending", "おうさまの エンディング"),
        ("The king, the party, then the staff roll", "おうさま、パーティー、スタッフロール"),
        "4932105322359",
    ),
)


def donald_rule(digits: str) -> int | None:
    """The type the check digit, the ninth digit and Epoch's prefix select, or None."""
    check = digits[-1]
    if check in REFUSED:
        return None
    if digits[MARKER_PLACE] == MARKER:
        return _marked(digits, int(check))
    return HAT_SHOP if digits.startswith(EPOCH_PRODUCT) else None


def _marked(digits: str, check: int) -> int | None:
    """A marked code's type: the check digit, where 7 needs Epoch's prefix too."""
    if check == STAFF_ROLL and not digits.startswith(EPOCH_PREFIX):
        return None
    return check


DONALD: Final = EffectGame(
    device=Device.DONALD,
    rule=donald_rule,
    effects=EFFECTS,
    strongest=0,
    screen=("Scan it on the title password screen", "タイトルの パスワード がめんで よませる"),
)
