"""Tests for the sizes a card face is laid out with."""

from maeyomi.rendering.card_style import CardStyle


def test_a_card_is_bordered_with_rounded_corners_by_default() -> None:
    style = CardStyle()

    assert (style.border, style.corner_mm) == (True, 2.4)


def test_a_style_can_drop_the_border() -> None:
    assert CardStyle(border=False).border is False
