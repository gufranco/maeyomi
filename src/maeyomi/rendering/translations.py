"""A card's words in the one language it is printed in.

English and Japanese are written beside each other at their source, so either
is a pick. Chinese comes from a catalogue per language, keyed by the English
text with every run of digits made a numbered placeholder, so one entry serves
"Raises it by 7" and "Raises it by 104" alike. Text the same in English and
Japanese is a proper name or a code and prints as it is. A label joined from
parts with "; " is translated part by part. Text the catalogue lacks prints in
English; a test holds every card the program makes to a full catalogue.
"""

import json
import re
from functools import cache
from importlib import resources
from typing import Final

from maeyomi.rendering.labels import Bilingual
from maeyomi.rendering.language import CardLanguage

NUMBER: Final = re.compile(r"\d+")
PLACEHOLDER: Final = re.compile(r"\{(\d+)\}")
PART_SEPARATOR: Final = "; "
CHINESE_SEPARATOR: Final = "\uff1b"
CATALOGUE_DIR: Final = "card_text"


def localise(text: Bilingual, language: CardLanguage) -> Bilingual:
    """The text as a card in that language prints it, in both slots when it is one language."""
    if language is CardLanguage.BOTH:
        return text
    if language is CardLanguage.ENGLISH:
        return Bilingual(text.english, text.english)
    if language is CardLanguage.JAPANESE:
        return Bilingual(text.japanese, text.japanese)
    if text.english == text.japanese:
        return text
    words = translate(text.english, language)
    return Bilingual(words, words)


def translate(english: str, language: CardLanguage) -> str:
    """English card text in a Chinese catalogue's words, or unchanged when it has none."""
    found = _from_catalogue(english, language)
    if found is not None:
        return found
    if PART_SEPARATOR not in english:
        return english
    parts = [translate(part, language) for part in english.split(PART_SEPARATOR)]
    return CHINESE_SEPARATOR.join(parts)


def template_of(text: str) -> tuple[str, tuple[str, ...]]:
    """The text with each number made a numbered placeholder, and the numbers in order."""
    numbers = tuple(NUMBER.findall(text))
    counter = iter(range(len(numbers)))
    return NUMBER.sub(lambda _: f"{{{next(counter)}}}", text), numbers


def _from_catalogue(english: str, language: CardLanguage) -> str | None:
    """The catalogue's translation with the numbers put back, or None."""
    key, numbers = template_of(english)
    found = catalogue(language).get(key)
    if found is None:
        return None
    return PLACEHOLDER.sub(lambda match: numbers[int(match.group(1))], found)


@cache
def catalogue(language: CardLanguage) -> dict[str, str]:
    """Every translated template of one Chinese language."""
    source = resources.files("maeyomi.rendering").joinpath(CATALOGUE_DIR, f"{language}.json")
    loaded: dict[str, str] = json.loads(source.read_text("utf-8"))
    return loaded
