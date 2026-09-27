"""The devices a card can be made for, each with its own way of reading a barcode."""

from enum import StrEnum
from typing import Final


class Device(StrEnum):
    """One reader. The value is the short key the command line and the page use."""

    BB2 = "bb2"
    BB1 = "bb1"
    DOUBLE = "double"
    DATACH_DBZ = "dbz"

    @property
    def is_game(self) -> bool:
        """Whether this is a game with a barcode reader rather than a standalone machine."""
        return self is Device.DATACH_DBZ

    @property
    def english(self) -> str:
        """The device's name in English."""
        return _NAMES[self][0]

    @property
    def japanese(self) -> str:
        """The device's name in Japanese, as its maker printed it."""
        return _NAMES[self][1]


_NAMES: Final[dict[Device, tuple[str, str]]] = {
    Device.BB2: ("Barcode Battler 2", "バーコードバトラー2"),
    Device.BB1: ("Barcode Battler", "バーコードバトラー"),
    Device.DOUBLE: ("Barcode Battler 2 Double", "バーコードバトラー2 ダブル"),
    Device.DATACH_DBZ: ("Datach Dragon Ball Z", "データック ドラゴンボールZ"),
}
