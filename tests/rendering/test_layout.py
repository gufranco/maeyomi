"""Tests for the printed sheet layout."""

import pytest

from barcode_battler.rendering.layout import A4_HEIGHT_MM, A4_WIDTH_MM, SheetLayout


def test_the_default_layout_is_a4_portrait() -> None:
    layout = SheetLayout()

    assert (layout.page_width_mm, layout.page_height_mm) == (A4_WIDTH_MM, A4_HEIGHT_MM)


def test_the_default_layout_fits_nine_poker_sized_cards() -> None:
    layout = SheetLayout()

    assert (layout.columns, layout.rows) == (3, 3)
    assert layout.cards_per_page == 9


def test_every_card_position_sits_inside_the_page() -> None:
    layout = SheetLayout()

    for x_mm, y_mm in layout.positions():
        assert x_mm >= 0
        assert x_mm + layout.card_width_mm <= layout.page_width_mm
        assert y_mm >= 0
        assert y_mm + layout.card_height_mm <= layout.page_height_mm


def test_positions_are_returned_in_reading_order() -> None:
    layout = SheetLayout()

    positions = layout.positions()

    assert positions[0][1] > positions[-1][1]
    assert positions[0][0] < positions[1][0]


def test_a_landscape_page_fits_a_different_grid() -> None:
    layout = SheetLayout(page_width_mm=A4_HEIGHT_MM, page_height_mm=A4_WIDTH_MM)

    assert layout.columns * layout.rows == layout.cards_per_page
    assert layout.columns >= 4


def test_a_card_larger_than_the_usable_page_is_rejected() -> None:
    with pytest.raises(ValueError, match="does not fit"):
        SheetLayout(card_width_mm=300)


def test_a_negative_margin_is_rejected() -> None:
    with pytest.raises(ValueError, match="margin"):
        SheetLayout(margin_mm=-1)


def test_the_grid_is_centred_on_the_page() -> None:
    layout = SheetLayout()

    used = layout.columns * layout.card_width_mm + (layout.columns - 1) * layout.gutter_mm
    left = layout.positions()[0][0]

    assert left == pytest.approx((layout.page_width_mm - used) / 2)


def test_paging_splits_a_batch_across_sheets() -> None:
    layout = SheetLayout()

    assert layout.page_count(0) == 0
    assert layout.page_count(1) == 1
    assert layout.page_count(9) == 1
    assert layout.page_count(10) == 2
    assert layout.page_count(24) == 3
