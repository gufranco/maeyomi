"""Tests for the pictograms drawn on a card.

Colour emoji cannot be printed: ReportLab's built-in fonts carry no emoji, and
an embedded emoji font renders flat black. The icons are therefore drawn as
vectors, which print in colour and stay sharp at any size. These tests check
that each one puts ink where it was asked to and nowhere else.
"""

from pathlib import Path

import pytest
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from barcode_battler.barcode.rasterise import ink_box, render_pdf_pages
from barcode_battler.models.race import Race
from barcode_battler.rendering.icons import (
    RACE_COLOURS,
    draw_heart,
    draw_race_icon,
    draw_shield,
    draw_sword,
)
from barcode_battler.rendering.labels import race_label

BOX_MM = 20.0
MARGIN_MM = 5.0
DPI = 300
WHITE_THRESHOLD = 230
MIN_ICON_COVERAGE = 0.08


def drawn(path: Path, draw: object) -> tuple[float, float, float, float]:
    side = (BOX_MM + 2 * MARGIN_MM) * mm
    canvas = Canvas(str(path), pagesize=(side, side))
    assert callable(draw)
    draw(canvas, x_mm=MARGIN_MM, y_mm=MARGIN_MM, size_mm=BOX_MM)
    canvas.showPage()
    canvas.save()
    box = ink_box(render_pdf_pages(path, dpi=DPI)[0])
    assert box is not None
    per_mm = DPI / 25.4
    height_px = (BOX_MM + 2 * MARGIN_MM) * per_mm
    return (
        box[0] / per_mm,
        (height_px - box[3]) / per_mm,
        box[2] / per_mm,
        (height_px - box[1]) / per_mm,
    )


@pytest.mark.parametrize("draw", [draw_heart, draw_sword, draw_shield])
def test_an_icon_draws_inside_the_box_it_was_given(draw: object, tmp_path: Path) -> None:
    left, bottom, right, top = drawn(tmp_path / "icon.pdf", draw)

    assert left >= MARGIN_MM - 0.2
    assert bottom >= MARGIN_MM - 0.2
    assert right <= MARGIN_MM + BOX_MM + 0.2
    assert top <= MARGIN_MM + BOX_MM + 0.2


@pytest.mark.parametrize("draw", [draw_heart, draw_sword, draw_shield])
def test_an_icon_fills_most_of_the_box(draw: object, tmp_path: Path) -> None:
    left, bottom, right, top = drawn(tmp_path / "icon.pdf", draw)

    assert right - left > BOX_MM * 0.5
    assert top - bottom > BOX_MM * 0.5


@pytest.mark.parametrize("race", list(Race))
def test_every_race_paints_its_icon_on_the_band(race: Race, tmp_path: Path) -> None:
    path = tmp_path / f"{race.name}.pdf"
    side = (BOX_MM + 2 * MARGIN_MM) * mm
    canvas = Canvas(str(path), pagesize=(side, side))
    canvas.setFillColorRGB(*RACE_COLOURS[race])
    canvas.rect(0, 0, side, side, stroke=0, fill=1)

    draw_race_icon(canvas, race, x_mm=MARGIN_MM, y_mm=MARGIN_MM, size_mm=BOX_MM)

    canvas.showPage()
    canvas.save()
    assert white_fraction(path) > MIN_ICON_COVERAGE


def white_fraction(path: Path) -> float:
    """Share of the page covered by the white icon."""
    image = render_pdf_pages(path, dpi=150)[0].convert("L")
    grey = image.tobytes()
    return sum(1 for value in grey if value > WHITE_THRESHOLD) / len(grey)


@pytest.mark.parametrize("race", list(Race))
def test_every_race_has_a_colour_and_a_child_readable_label(race: Race) -> None:
    red, green, blue = RACE_COLOURS[race]

    assert 0.0 <= red <= 1.0
    assert 0.0 <= green <= 1.0
    assert 0.0 <= blue <= 1.0
    assert race_label(race).english
    assert race_label(race).english[0].isupper()


def test_the_fighter_races_are_told_apart_by_colour() -> None:
    fighters = [race for race in Race if race.is_fighter]

    assert len({RACE_COLOURS[race] for race in fighters}) == len(fighters)
