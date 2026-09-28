"""Setting a card's words: a line in one or two languages, and the ability panel.

A card prints English and Japanese side by side, or one language alone. Every
function here localises its text first, so a card in one language sets each
line once, in that language's face.
"""

from dataclasses import dataclass
from typing import Final

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from maeyomi.rendering.labels import SPECIAL_POWER, Bilingual
from maeyomi.rendering.language import CardLanguage
from maeyomi.rendering.text import font_for, text_width_mm, wrap
from maeyomi.rendering.translations import localise

PAIR_GAP_MM: Final = 1.6


@dataclass(frozen=True, slots=True)
class Line:
    """Where a line of text goes, how big, and in which language."""

    x: float
    baseline: float
    size_pt: float
    available: float
    bold: bool = False
    centred: bool = False
    gap: float = PAIR_GAP_MM
    language: CardLanguage = CardLanguage.BOTH


@dataclass(frozen=True, slots=True)
class AbilityPanel:
    """The ability panel's line height, text size and language."""

    line_mm: float
    size_pt: float
    language: CardLanguage


def draw_pair(canvas: Canvas, text: Bilingual, line: Line) -> None:
    """Set the English and then the Japanese on one line, shrinking both to fit.

    A centred line is centred on `x`; otherwise it starts there. Text that reads
    the same in both languages, or a card in one language, is set once.
    """
    text = localise(text, line.language)
    if text.english == text.japanese:
        draw_single(canvas, text.english, line)
        return
    english_font = font_for(text.english, bold=line.bold)
    japanese_font = font_for(text.japanese, bold=line.bold)
    natural = (
        text_width_mm(text.english, english_font, line.size_pt)
        + line.gap
        + text_width_mm(text.japanese, japanese_font, line.size_pt)
    )
    scale = min(1.0, line.available / natural)
    size = line.size_pt * scale
    left = line.x - natural * scale / 2 if line.centred else line.x
    canvas.setFont(english_font, size)
    canvas.drawString(left * mm, line.baseline * mm, text.english)
    japanese_left = left + text_width_mm(text.english, english_font, size) + line.gap * scale
    canvas.setFont(japanese_font, size)
    canvas.drawString(japanese_left * mm, line.baseline * mm, text.japanese)


def draw_single(canvas: Canvas, text: str, line: Line) -> None:
    """Set one piece of text on a line, shrinking it to fit."""
    font = font_for(text, bold=line.bold, language=line.language)
    natural = text_width_mm(text, font, line.size_pt)
    size = line.size_pt * min(1.0, line.available / natural)
    width = text_width_mm(text, font, size)
    canvas.setFont(font, size)
    canvas.drawString(
        (line.x - width / 2 if line.centred else line.x) * mm, line.baseline * mm, text
    )


def power_header(code: int, language: CardLanguage) -> Bilingual:
    """The ability panel's heading: its number after the words, once per card."""
    if language is CardLanguage.BOTH:
        return Bilingual(f"{SPECIAL_POWER.english} {code:02d}", SPECIAL_POWER.japanese)
    words = f"{localise(SPECIAL_POWER, language).english} {code:02d}"
    return Bilingual(words, words)


def ability_lines(
    text: Bilingual, available: float, height: float, panel: AbilityPanel
) -> list[tuple[str, str]]:
    """Share the panel's lines between the two languages, English first.

    Japanese always keeps at least one line. Whatever English does not use goes
    to Japanese. A card in one language gives that language every line.
    """
    budget = max(2, int((height - 3.4) / panel.line_mm))
    text = localise(text, panel.language)
    if text.english == text.japanese:
        font = font_for(text.english, language=panel.language)
        lines = wrap(text.english, available, font=font, size_pt=panel.size_pt, max_lines=budget)
        return [(line, font) for line in lines]
    english_font = font_for(text.english)
    japanese_font = font_for(text.japanese)
    english = wrap(
        text.english,
        available,
        font=english_font,
        size_pt=panel.size_pt,
        max_lines=budget - 1,
    )
    japanese = wrap(
        text.japanese,
        available,
        font=japanese_font,
        size_pt=panel.size_pt,
        max_lines=budget - len(english),
    )
    return [(line, english_font) for line in english] + [(line, japanese_font) for line in japanese]
