"""The first Barcode Battler's flag table, which is not the Barcode Battler II's.

The two devices store a two-digit ability code in the same place and mean
different things by it: 18 is the hero on the first device and a doubled attack
on the second. Codes 00 to 39 are published twice, in English on
barcodebattler.co.uk, "Barcode Battler Museum: Original Barcode Battler",
technical info, and in Japanese in the note.com analysis by sakigomyway. The
two agree on every code but 01, which one calls a turn of accuracy and the
other a better initiative, so both languages print both readings. For 40 to 99
only the English source makes a claim, so those codes say so.
"""

from dataclasses import dataclass
from typing import Final

MIN_CODE: Final = 0
MAX_CODE: Final = 99
FIRST_UNLISTED_CODE: Final = 40
_B1: Final = ", B1 mode"
_COM: Final = ", COM mode"

_PASSCODES: Final[dict[int, str]] = {
    15: "355",
    16: "590",
    17: "766",
    35: "092",
    36: "169",
    37: "229",
    38: "348",
}
_JOB_TARGETS: Final[dict[int, int]] = {9: 2, 10: 4, 11: 7, 12: 9}

_ENGLISH: Final[dict[int, str]] = {
    0: "No ability",
    1: "Increase own initiative, or accuracy for one turn; the sources differ",
    2: "Reduce opponent accuracy",
    3: "Increase own accuracy",
    4: "Increase own damage output a lot",
    5: "Double own ST",
    6: "Increase own DF by 50%",
    7: "Increase own damage output a little",
    8: "Increase own damage output a little more",
    13: "Reduce opponent DF to 0",
    14: "Subtracts HP instead of adding, on an HP item",
    18: "Hero",
    19: "Boss" + _B1,
    39: "Reduce opponent DF to 0",
    **{code: f"Triple damage to occupation {job}" for code, job in _JOB_TARGETS.items()},
    **{code: f"Rewards player with passcode {pass_}{_B1}" for code, pass_ in _PASSCODES.items()},
    **{code: f"Rewards player with +{100 * (code - 19)} ST{_B1}" for code in range(20, 23)},
    **{code: f"Rewards player with +{100 * (code - 22)} DF{_B1}" for code in range(23, 26)},
    **{code: f"Only works on clan {code - 24} or higher{_COM}" for code in range(26, 34)},
    34: "Only works on clan 0 or higher" + _COM,
}

_JAPANESE: Final[dict[int, str]] = {
    0: "特殊能力なし",
    1: "自分の先攻率アップ。別の資料では1ターンだけ命中率アップ",
    2: "相手の命中率ダウン",
    3: "自分の命中率アップ",
    4: "自分の破壊力が大幅アップ(？)",
    5: "自分の破壊力100％アップ(2倍剣)",
    6: "自分の防御力50％アップ(受けるダメージが0.5倍になる)",
    7: "自分の破壊力が少しアップ",
    8: "自分の破壊力がもう少しアップ",
    13: "相手のDFダウン(相手のDFを0にする)",
    14: "使用するとHPダウン？(※HPアイテムである場合のみ有効)",
    18: "主人公フラグ(COM/B1モードで主人公として使える)",
    19: "B1モード ボスフラグ",
    39: "相手のDFダウン(相手のDFを0にする)",
    **{code: f"職業「{job}」の相手に対して3倍剣" for code, job in _JOB_TARGETS.items()},
    **{code: f"B1モード パスコード{pass_}" for code, pass_ in _PASSCODES.items()},
    **{code: f"B1モード 倒すとST+{100 * (code - 19)}" for code in range(20, 23)},
    **{code: f"B1モード 倒すとDF+{100 * (code - 22)}" for code in range(23, 26)},
    **{code: f"COMモード C{code - 24}以降使用可能" for code in range(26, 34)},
    34: "COMモード C0以降使用可能",
}

_UNLISTED_ENGLISH: Final = (
    "Rewards player with the enemy's HP value, B1 mode, according to one source"
)
_UNLISTED_JAPANESE: Final = "不明。英語の資料1つだけが、B1モードで相手のHPの値がもらえるとする"


@dataclass(frozen=True, slots=True)
class Flag:
    """One flag code of the first Barcode Battler and its published effect."""

    code: int
    description: str
    japanese: str

    @classmethod
    def from_code(cls, code: int) -> Flag:
        """Build the flag for a code, refusing one outside two digits."""
        if not MIN_CODE <= code <= MAX_CODE:
            message = f"flag code {code} is outside 00-99"
            raise ValueError(message)
        if code >= FIRST_UNLISTED_CODE:
            return cls(code, _UNLISTED_ENGLISH, _UNLISTED_JAPANESE)
        return cls(code, _ENGLISH[code], _JAPANESE[code])

    @property
    def is_documented(self) -> bool:
        """Whether both sources agree on this code's effect."""
        return self.code < FIRST_UNLISTED_CODE
