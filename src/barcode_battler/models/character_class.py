"""The two character classes the device distinguishes.

Source: barcodebattler.net/page01.htm, job digit 0-6 warrior, 7-9 magician.
"""

from enum import Enum


class CharacterClass(Enum):
    """Warrior or magician, derived from the job digit."""

    WARRIOR = "warrior"
    MAGICIAN = "magician"
