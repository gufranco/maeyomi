"""The languages a card can be printed in.

The values are the page's language tags, so the page passes its own choice
straight through. `both` prints English and Japanese side by side, as every
card did before a single language could be chosen.
"""

from enum import StrEnum


class CardLanguage(StrEnum):
    """One language for every word on a card, or English and Japanese together."""

    BOTH = "both"
    ENGLISH = "en"
    JAPANESE = "ja"
