"""Setting text on a card: choosing a face, wrapping, and fitting a width.

A card carries English and Japanese side by side, or one language alone, so
every string is set in the face that has its glyphs. Latin text uses the PDF
base fonts. Chinese uses a song face of its own script, and anything else a
Japanese gothic; PDF readers carry all three.
"""

import importlib
from functools import cache
from typing import Any, Final, cast

from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import CIDFont, UnicodeCIDFont

from maeyomi.rendering.language import CardLanguage

LATIN_FONT: Final = "Helvetica"
LATIN_BOLD_FONT: Final = "Helvetica-Bold"
JAPANESE_FONT: Final = "HeiseiKakuGo-W5"
"""A Japanese gothic for text the Latin faces have no glyphs for.

It is one of the Adobe Japan1 fonts PDF readers carry, so it needs no file here.
It is referenced rather than embedded, which is what that font class is for;
see the README on printing.
"""

SIMPLIFIED_FONT: Final = "STSong-Light"
"""The Adobe GB1 song face PDF readers carry, for Simplified Chinese."""
TRADITIONAL_FONT: Final = "MSung-Light"
"""The Adobe CNS1 song face PDF readers carry, for Hong Kong Chinese."""
TRADITIONAL_MAP: Final = "UniCNS-UCS2-H"
TRADITIONAL_LANGUAGE: Final = "cht"
CID_DATA: Final = "reportlab.pdfbase._cidfontdata"
KANA: Final = range(0x3040, 0x3100)

LATIN_1_LIMIT: Final = 0xFF
ELLIPSIS: Final = "..."


def is_latin(text: str) -> bool:
    """Whether every character is one the Latin faces can draw."""
    return all(ord(character) <= LATIN_1_LIMIT for character in text)


def font_for(text: str, *, bold: bool = False, language: CardLanguage = CardLanguage.BOTH) -> str:
    """The face a string is set in: Latin where it can be, then the card's CJK face.

    A Chinese card sets Chinese in its own face, except a string with kana,
    such as a Japanese name, which only the Japanese face can draw.
    """
    if is_latin(text):
        return LATIN_BOLD_FONT if bold else LATIN_FONT
    if language.is_chinese and not any(ord(character) in KANA for character in text):
        return _register_chinese_font(language)
    _register_japanese_font()
    return JAPANESE_FONT


@cache
def _register_chinese_font(language: CardLanguage) -> str:
    """Register the Chinese face of one language once, and name it."""
    face = SIMPLIFIED_FONT if language is CardLanguage.SIMPLIFIED else TRADITIONAL_FONT
    font = UnicodeCIDFont(face) if face == SIMPLIFIED_FONT else _TraditionalFont()
    cast("Any", pdfmetrics).registerFont(font)
    return face


class _TraditionalFont(UnicodeCIDFont):
    """MSung-Light read through the CNS map, which its Adobe CNS1 glyphs need.

    ReportLab pairs this face with the GB map, which sends a Traditional
    character to a Simplified glyph number, so the face is built by hand.
    """

    def __init__(self) -> None:
        cast("Any", CIDFont).__init__(self, TRADITIONAL_FONT, TRADITIONAL_MAP)
        self.name = self.fontName = TRADITIONAL_FONT
        self.language = TRADITIONAL_LANGUAGE
        self.vertical = False
        self.isHalfWidth = False
        self.unicodeWidths = cast("Any", importlib.import_module(CID_DATA)).widthsByUnichar[
            TRADITIONAL_FONT
        ]


@cache
def _register_japanese_font() -> None:
    """Register the Japanese face once, the first time a string needs it."""
    cast("Any", pdfmetrics).registerFont(UnicodeCIDFont(JAPANESE_FONT))


def text_width_mm(text: str, font: str, size_pt: float) -> float:
    """How wide a string is set, in millimetres."""
    return pdfmetrics.stringWidth(text, font, size_pt) / mm


def fit_size(text: str, font: str, available_mm: float, size_pt: float) -> float:
    """The largest size up to the preferred one at which the text fits the width."""
    width = text_width_mm(text, font, size_pt)
    if width <= available_mm:
        return size_pt
    return size_pt * available_mm / width


def wrap(
    text: str,
    available_mm: float,
    *,
    font: str,
    size_pt: float,
    max_lines: int,
) -> list[str]:
    """Break text to fit the width.

    Latin text breaks between words. Japanese is written without spaces between
    words, so it breaks between characters. Text that still does not fit is cut
    and the cut is marked, so a reader can see it was shortened rather than read
    something different.
    """
    limit = available_mm * mm
    by_word = is_latin(text)
    joiner = " " if by_word else ""
    tokens = text.split() if by_word else list(text.strip())
    lines: list[str] = []
    current = ""
    truncated = False
    for token in tokens:
        candidate = f"{current}{joiner}{token}" if current else token.strip()
        if current and pdfmetrics.stringWidth(candidate, font, size_pt) > limit:
            lines.append(current.rstrip())
            current = token.strip()
            if len(lines) == max_lines:
                truncated = True
                current = ""
                break
        else:
            current = candidate
    if current:
        lines.append(current)
    wrapped = [_trim(line, limit, font, size_pt) for line in lines]
    if truncated and wrapped:
        wrapped[-1] = _cut(wrapped[-1], limit, font, size_pt)
    return wrapped


def _trim(text: str, limit: float, font: str, size_pt: float) -> str:
    """Return the text unchanged when it fits, and cut it when it does not."""
    if pdfmetrics.stringWidth(text, font, size_pt) <= limit:
        return text
    return _cut(text, limit, font, size_pt)


def _cut(text: str, limit: float, font: str, size_pt: float) -> str:
    """Shorten text until it and an ellipsis fit, and mark the cut."""
    trimmed = text
    while trimmed and pdfmetrics.stringWidth(trimmed + ELLIPSIS, font, size_pt) > limit:
        trimmed = trimmed[:-1]
    return trimmed + ELLIPSIS
