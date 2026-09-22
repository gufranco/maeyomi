"""Tests for the printed sheet layout."""

import pytest

from barcode_battler.rendering.layout import (
    A4_HEIGHT_MM,
    A4_WIDTH_MM,
    CARD_HEIGHT_MM,
    CARD_WIDTH_MM,
    MARK_BAND_MM,
    SheetLayout,
)


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


def test_cards_are_spaced_apart_so_a_guillotine_can_cut_each_one() -> None:
    layout = SheetLayout()

    assert layout.gutter_mm >= 2 * layout.bleed_mm
    assert layout.bleed_mm > 0


def test_nine_cards_still_fit_a_page_with_the_spacing() -> None:
    layout = SheetLayout()

    assert (layout.columns, layout.rows) == (3, 3)


def test_the_spacing_leaves_room_for_both_bleeds_between_neighbours() -> None:
    layout = SheetLayout()
    positions = layout.positions()

    first, second = positions[0], positions[1]
    assert second[0] - (first[0] + layout.card_width_mm) == pytest.approx(layout.gutter_mm)


def test_a_print_shop_page_holds_one_card_with_its_bleed() -> None:
    layout = SheetLayout.print_shop()

    assert layout.cards_per_page == 1
    assert layout.page_width_mm == pytest.approx(layout.card_width_mm + 2 * layout.bleed_mm)
    assert layout.page_height_mm == pytest.approx(layout.card_height_mm + 2 * layout.bleed_mm)
    assert layout.bleed_mm == pytest.approx(3.0)


def test_the_grid_leaves_the_marks_their_band() -> None:
    layout = SheetLayout()
    lowest = min(y for _, y in layout.positions())
    highest = max(y for _, y in layout.positions()) + layout.card_height_mm

    assert lowest >= MARK_BAND_MM
    assert layout.page_height_mm - highest >= MARK_BAND_MM


def test_a_card_is_taller_than_it_is_wide() -> None:
    layout = SheetLayout()

    assert (layout.card_width_mm, layout.card_height_mm) == (CARD_WIDTH_MM, CARD_HEIGHT_MM)
    assert layout.card_height_mm > layout.card_width_mm


def test_nine_cards_fill_a_page() -> None:
    assert SheetLayout().cards_per_page == 9
