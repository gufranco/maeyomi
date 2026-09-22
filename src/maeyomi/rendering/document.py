"""What a PDF says about itself before anyone reads a word of it.

A screen reader opening a PDF announces its title, or, when there is none, the
filename. `DisplayDocTitle` is what makes it prefer the title, and it is off by
default in every PDF, which is why so many of them are announced as
`sheet-final-v2.pdf`.

The language is declared once for the document. Every card carries English and
Japanese together, and the pair cannot be split without a structure tree, which
ReportLab does not emit. English is declared as the document language because
it is the first of the two on every card; the Japanese runs are not separately
marked, and that limit is stated in the README rather than papered over.
"""

from typing import Any, Final, cast

from reportlab.pdfgen.canvas import Canvas

AUTHOR: Final = "maeyomi"
SUBJECT: Final = "Print playable cards for a 1992 Epoch Barcode Battler II"
KEYWORDS: Final = "barcode battler, barcode, cards, EAN-13, printable"
LANGUAGE: Final = "en"


def describe(canvas: Canvas, title: str) -> None:
    """Give a PDF a spoken title, an author and a declared language."""
    canvas.setTitle(title)
    canvas.setAuthor(AUTHOR)
    canvas.setSubject(SUBJECT)
    canvas.setKeywords(KEYWORDS)
    canvas.setCreator(AUTHOR)
    untyped = cast("Any", canvas)
    untyped.setCatalogEntry("Lang", LANGUAGE)
    untyped.setViewerPreference("DisplayDocTitle", "true")
