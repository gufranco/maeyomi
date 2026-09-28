"""What a PDF says about itself before anyone reads a word of it.

A screen reader opening a PDF announces its title, or, when there is none, the
filename. `DisplayDocTitle` is what makes it prefer the title, and it is off by
default in every PDF, which is why so many of them are announced as
`sheet-final-v2.pdf`.

The language is declared once for the document, and it is the language the
cards are printed in, so a reader picks the voice that can speak them. A sheet
printed in English and Japanese together cannot be split without a structure
tree, which ReportLab does not emit. It declares English, the first of the two
on every card; the Japanese runs are not separately marked, and that limit is
stated in the README rather than papered over.
"""

from typing import Any, Final, cast

from reportlab.pdfgen.canvas import Canvas

from maeyomi.rendering.language import CardLanguage

AUTHOR: Final = "maeyomi"
SUBJECT: Final = "Print playable cards for Barcode Battler machines and barcode games"
KEYWORDS: Final = "barcode battler, barcode, cards, EAN-13, printable"
LANGUAGE: Final = "en"


def describe(canvas: Canvas, title: str, language: CardLanguage) -> None:
    """Give a PDF a spoken title, an author and the language its cards are printed in."""
    canvas.setTitle(title)
    canvas.setAuthor(AUTHOR)
    canvas.setSubject(SUBJECT)
    canvas.setKeywords(KEYWORDS)
    canvas.setCreator(AUTHOR)
    untyped = cast("Any", canvas)
    untyped.setCatalogEntry("Lang", declared_language(language))
    untyped.setViewerPreference("DisplayDocTitle", "true")


def declared_language(language: CardLanguage) -> str:
    """The language tag a PDF declares for cards printed in that language."""
    return LANGUAGE if language is CardLanguage.BOTH else language.value
