"""The words Family Jockey 2 uses for its horses, in both languages.

The Japanese is the game's own, as its screens show it; the bonuses are what the
game says when a card carries one of Namco's own box codes.
"""

from typing import Final

KINDS: Final = (("Racehorse", "競走馬"), ("Mare", "繁殖馬"), ("Stallion", "種馬"))

STATS: Final = (
    ("Speed", "スピード"),
    ("Stamina", "スタミナ"),
    ("Guts", "ガッツ"),
    ("Jump", "ジャンプ"),
    ("Turbo", "ターボ"),
    ("Type", "タイプ"),
)

SHORT: Final = ("SP", "ST", "G", "J", "TB", "TP")

BONUSES: Final = (
    ("A Namco Famicom game: stamina +2", "ナムコの ファミコンソフト: スタミナ2アップ"),
    ("A Namco Super Famicom card: speed +2", "ナムコの スーパーファミコン カード: スピード2アップ"),
    ("A Namco Game Boy game: turbo +2", "ナムコの ゲームボーイ: ターボ2プラス"),
    ("A Namco game: guts +2", "ナムコの ソフト: ガッツ2アップ"),
    ("A Namco card: type +2", "ナムコの カード: タイプ2アップ"),
    ("A Namco card: jump +2", "ナムコの カード: ジャンプ2アップ"),
    ("A Barcode Boy card: plus 1", "バーコードボーイの カード: プラス1"),
)
