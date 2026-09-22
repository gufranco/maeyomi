"""Tests for the pictogram that tells a child what a special power does."""

from pathlib import Path

import pytest
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from barcode_battler.barcode.rasterise import ink_box, render_pdf_pages
from barcode_battler.models.special_ability import MAX_CODE, MIN_CODE, SpecialAbility
from barcode_battler.rendering.ability_icons import (
    Badge,
    Glyph,
    ability_icon,
    draw_ability_icon,
)

BOX_MM = 10.0
MARGIN_MM = 3.0


@pytest.mark.parametrize("code", range(MIN_CODE, MAX_CODE + 1))
def test_every_code_has_an_icon(code: int) -> None:
    icon = ability_icon(SpecialAbility.from_code(code))

    assert isinstance(icon.glyph, Glyph)


@pytest.mark.parametrize(
    ("code", "glyph", "badge"),
    [
        (0, Glyph.NONE, Badge.NONE),
        (5, Glyph.SWORD, Badge.TRIPLE),
        (16, Glyph.SWORD, Badge.DOWN),
        (18, Glyph.SWORD, Badge.UP),
        (19, Glyph.CROWN, Badge.NONE),
        (21, Glyph.SHIELD, Badge.UP),
        (24, Glyph.SWORD, Badge.DOWN),
        (27, Glyph.SHIELD, Badge.DOWN),
        (29, Glyph.HEART, Badge.DOWN),
        (30, Glyph.HEART, Badge.CHANCE),
        (38, Glyph.TARGET, Badge.UP),
        (41, Glyph.TARGET, Badge.DOWN),
        (42, Glyph.HEART, Badge.FORBIDDEN),
        (45, Glyph.CANCEL, Badge.NONE),
        (50, Glyph.CROWN, Badge.NONE),
        (69, Glyph.HEART, Badge.UP),
        (74, Glyph.SWORD, Badge.UP),
        (79, Glyph.SHIELD, Badge.UP),
        (85, Glyph.KEY, Badge.NONE),
        (57, Glyph.UNKNOWN, Badge.NONE),
    ],
)
def test_an_ability_shows_what_it_changes_and_which_way(
    code: int, glyph: Glyph, badge: Badge
) -> None:
    icon = ability_icon(SpecialAbility.from_code(code))

    assert (icon.glyph, icon.badge) == (glyph, badge)


@pytest.mark.parametrize("code", range(1, MAX_CODE + 1))
def test_every_icon_draws_inside_its_box(code: int, tmp_path: Path) -> None:
    path = tmp_path / "icon.pdf"
    side = (BOX_MM + 2 * MARGIN_MM) * mm
    canvas = Canvas(str(path), pagesize=(side, side))

    draw_ability_icon(
        canvas, SpecialAbility.from_code(code), x_mm=MARGIN_MM, y_mm=MARGIN_MM, size_mm=BOX_MM
    )

    canvas.showPage()
    canvas.save()
    box = ink_box(render_pdf_pages(path, dpi=100)[0])
    assert box is not None
    per_mm = 100 / 25.4
    assert box[0] >= (MARGIN_MM - 0.5) * per_mm
    assert box[2] <= (MARGIN_MM + BOX_MM + 0.5) * per_mm


def test_code_zero_draws_nothing(tmp_path: Path) -> None:
    path = tmp_path / "none.pdf"
    side = (BOX_MM + 2 * MARGIN_MM) * mm
    canvas = Canvas(str(path), pagesize=(side, side))

    draw_ability_icon(
        canvas, SpecialAbility.from_code(0), x_mm=MARGIN_MM, y_mm=MARGIN_MM, size_mm=BOX_MM
    )

    canvas.showPage()
    canvas.save()
    assert ink_box(render_pdf_pages(path, dpi=100)[0]) is None
