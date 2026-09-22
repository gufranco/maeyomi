"""Race and item-type values carried by a single barcode digit.

Source: barcodebattler.net/page01.htm.
"""

from enum import IntEnum


class Race(IntEnum):
    """Digit 0-9 selecting a fighter race or an item type."""

    MECHANICAL = 0
    ANIMAL = 1
    AQUATIC = 2
    BIRD = 3
    HUMAN = 4
    SINGLE_USE_WEAPON = 5
    WEAPON = 6
    SINGLE_USE_ARMOUR = 7
    ARMOUR = 8
    SUPPORT_ITEM = 9

    @property
    def is_fighter(self) -> bool:
        """Whether this race denotes a playable character rather than an item."""
        return self <= Race.HUMAN

    @property
    def is_weapon(self) -> bool:
        """Whether this race denotes a weapon, which carries an ST modifier."""
        return self in (Race.SINGLE_USE_WEAPON, Race.WEAPON)

    @property
    def is_armour(self) -> bool:
        """Whether this race denotes armour, which carries a DF modifier."""
        return self in (Race.SINGLE_USE_ARMOUR, Race.ARMOUR)
