"""Special ability codes 00 to 99 and their documented effects.

Source: barcodebattler.net/page05.htm, read 2026-09-21. Codes 00 to 49 apply in
every mode; codes 50 to 99 apply only in the C1 and C2 game modes. A back-read
barcode can only carry codes 00 to 29.
"""

from dataclasses import dataclass
from typing import Final

UNDOCUMENTED: Final = "undocumented"
MIN_CODE: Final = 0
MAX_CODE: Final = 99
MAX_BACK_READ_CODE: Final = 29
FIRST_C1_C2_ONLY_CODE: Final = 50

_ON_DEFEAT_HP_GAINS: Final = (1000, 3000, 4000, 5000, 10000)
_PASSCODE_REWARDS: Final = (5, 10, 15, 20, 25, *range(35, 50))

_DESCRIPTIONS: Final[dict[int, str]] = {
    0: "none",
    10: "triple damage against job 0",
    15: "triple damage against race 0",
    16: "own attack halved",
    17: "own attack increased by half",
    18: "own attack doubled",
    19: "hero flag, C1 and C2 only",
    20: "own defence increased by 10 percent",
    21: "own defence increased by 30 percent",
    22: "own defence increased by 50 percent",
    23: "opponent ST reduced by 30 percent",
    24: "opponent ST reduced by 50 percent",
    25: "opponent DF reduced by 30 percent",
    26: "opponent DF reduced by 50 percent",
    27: "opponent DF reduced by 80 percent",
    28: "opponent HP reduced by 30 percent",
    29: "opponent HP reduced by 50 percent",
    30: "HP item may subtract instead of add, one chance in two",
    31: "ST item may subtract instead of add, one chance in two",
    32: "DF item may subtract instead of add, one chance in two",
    37: "own initiative rate increased",
    38: "own hit rate increased",
    39: "opponent hit rate increased",
    40: "own hit rate reduced",
    41: "opponent hit rate reduced",
    42: "opponent recovery forbidden, Famicom version only",
    43: "opponent recovery power reduced",
    44: "own recovery power increased",
    45: "all opponent special abilities nullified",
    50: "hero flag, C1 and C2 only",
    **{code: f"triple damage against job {code}" for code in range(1, 10)},
    **{code: f"triple damage against race {code - 10}" for code in range(11, 15)},
    **{
        code: f"on defeat, HP plus {gain}"
        for code, gain in zip(range(65, 70), _ON_DEFEAT_HP_GAINS, strict=True)
    },
    **{code: f"on defeat, ST plus {200 * (code - 69)}" for code in range(70, 75)},
    **{code: f"on defeat, DF plus {200 * (code - 74)}" for code in range(75, 80)},
    **{
        code: f"on defeat, passcode {reward:02d}"
        for code, reward in zip(range(80, 100), _PASSCODE_REWARDS, strict=True)
    },
}


@dataclass(frozen=True, slots=True)
class SpecialAbility:
    """A special ability code together with its documented effect."""

    code: int
    description: str

    @classmethod
    def from_code(cls, code: int) -> SpecialAbility:
        """Build the ability for a code, raising when the code is out of range."""
        if not MIN_CODE <= code <= MAX_CODE:
            message = f"special ability code {code} is outside {MIN_CODE}-{MAX_CODE}"
            raise ValueError(message)
        return cls(code=code, description=_DESCRIPTIONS.get(code, UNDOCUMENTED))

    @property
    def is_documented(self) -> bool:
        """Whether the published table records an effect for this code."""
        return self.description != UNDOCUMENTED

    @property
    def is_c1_c2_only(self) -> bool:
        """Whether this ability only takes effect in the C1 and C2 game modes."""
        return self.code >= FIRST_C1_C2_ONLY_CODE
