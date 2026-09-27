"""The Double's special powers, which are not the Barcode Battler II's.

Source: "BBIIダブルC0" on barcodebattler.net, by alba, last updated 2003. Its
table is partial and marks some rows as guesses; those rows say so here, and
every code it does not list is undocumented. It disagrees with the II on code
18, which it gives as the hero rather than a doubled attack. The Japanese is
the page's own wording; the English is this project's translation of it.
"""

from dataclasses import dataclass
from typing import Final

UNDOCUMENTED: Final = ("undocumented", "不明")
PROBABLY: Final = ", probably"

_TABLE: Final[dict[int, tuple[str, str]]] = {
    0: ("none; on an HP item, an information card", "なにもなし、HPのアイテムのとき情報カード？"),
    18: ("hero in C1 and C2", "C1、C2モードで主人公キャラとして使える"),
    23: ("opponent ST down 30%", "ST30%ダウン"),
    24: ("opponent ST down 50%", "ST50%ダウン"),
    25: ("opponent DF down 30%", "DF30%ダウン"),
    26: ("opponent DF down 50%", "DF50%ダウン"),
    27: ("opponent DF down 80%", "DF80%ダウン"),
    28: ("opponent HP down 30%", "HP30%ダウン"),
    29: ("opponent HP down 50%", "HP50%ダウン"),
    30: ("an HP item may lower HP instead", "HPアイテムの時、副作用で下がる可能性がある"),
    31: ("a weapon may lower ST instead", "武器の時、副作用で下がる可能性がある"),
    32: ("armour may lower DF instead", "防具の時、副作用で下がる可能性がある"),
    35: ("puts the opponent to sleep at the start", "スタート時、相手を眠り状態"),
    37: ("always strikes first", "先手が必ずとれるようになる（素早さアップ？）"),
    38: ("own hit rate up" + PROBABLY, "自分の命中率アップ？"),
    40: ("puts itself to sleep at the start", "スタート時、自分を眠り状態に"),
    41: ("opponent hit rate down" + PROBABLY, "相手の命中率ダウン？"),
    44: ("critical hit rate up" + PROBABLY, "会心率アップ？"),
    45: ("immune to having its stats lowered", "能力ダウン無効"),
    50: ("hero in C1 and C2", "C1、C2モードで主人公キャラとして使える"),
    51: ("puts the opponent to sleep at the start", "スタート時、相手を眠り状態"),
    52: ("puts itself to sleep at the start", "スタート時、自分を眠り状態"),
    56: (
        "immune to magic; F1 and F2 land as plain attacks",
        "魔法無効（F1、F2は通常攻撃として、他の魔法は全く効かなくなります）",
    ),
    57: ("carries Kieteera on itself", "自分にキエテーラがかかっている"),
    78: ("opponent hit rate down" + PROBABLY, "相手の命中率ダウン？"),
    **dict.fromkeys(range(80, 100), ("a password in C2 mode", "C2モードでパスワードを出す")),
}


@dataclass(frozen=True, slots=True)
class DoubleAbility:
    """One special power code as the Double documents it."""

    code: int
    description: str
    japanese: str

    @classmethod
    def from_code(cls, code: int) -> DoubleAbility:
        """Build the power for a code, refusing one outside two digits."""
        if not 0 <= code <= 99:  # noqa: PLR2004
            message = f"special power code {code} is outside 00-99"
            raise ValueError(message)
        description, japanese = _TABLE.get(code, UNDOCUMENTED)
        return cls(code, description, japanese)

    @property
    def is_documented(self) -> bool:
        """Whether the source lists this code at all."""
        return self.code in _TABLE
