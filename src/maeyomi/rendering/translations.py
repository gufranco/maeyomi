"""A card's words in the one language it is printed in.

English and Japanese are written beside each other at their source, so a card
in one language picks its half, and a card in both keeps the pair.
"""

from maeyomi.rendering.labels import Bilingual
from maeyomi.rendering.language import CardLanguage


def localise(text: Bilingual, language: CardLanguage) -> Bilingual:
    """The text as a card in that language prints it, in both slots when it is one language."""
    if language is CardLanguage.ENGLISH:
        return Bilingual(text.english, text.english)
    if language is CardLanguage.JAPANESE:
        return Bilingual(text.japanese, text.japanese)
    return text
