"""Tests for the printed sheet layout."""

import pytest

from barcode_battler.rendering.layout import (
    A4_HEIGHT_MM,
    A4_WIDTH_MM,
    ID1_LONG_MM,
    ID1_SHORT_MM,
    MARK_BAND_MM,
    CardOrientation,
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


def test_a_card_is_exactly_credit_card_sized() -> None:
    assert (ID1_LONG_MM, ID1_SHORT_MM) == (85.60, 53.98)


def test_the_default_card_is_a_credit_card_standing_up() -> None:
    layout = SheetLayout()

    assert (layout.card_width_mm, layout.card_height_mm) == (ID1_SHORT_MM, ID1_LONG_MM)
    assert layout.orientation is CardOrientation.PORTRAIT


def test_a_landscape_card_is_the_same_card_turned_over() -> None:
    layout = SheetLayout.of(CardOrientation.LANDSCAPE)

    assert (layout.card_width_mm, layout.card_height_mm) == (ID1_LONG_MM, ID1_SHORT_MM)
    assert layout.card_width_mm * layout.card_height_mm == pytest.approx(
        SheetLayout().card_width_mm * SheetLayout().card_height_mm
    )


def test_both_orientations_fill_a_page() -> None:
    assert SheetLayout.of(CardOrientation.PORTRAIT).cards_per_page == 9
    assert SheetLayout.of(CardOrientation.LANDSCAPE).cards_per_page == 8


def test_a_print_shop_page_follows_the_orientation() -> None:
    landscape = SheetLayout.print_shop(CardOrientation.LANDSCAPE)

    assert landscape.card_width_mm == ID1_LONG_MM
    assert landscape.page_width_mm == pytest.approx(ID1_LONG_MM + 2 * landscape.bleed_mm)


def test_the_grid_leaves_the_marks_their_band() -> None:
    layout = SheetLayout()
    lowest = min(y for _, y in layout.positions())
    highest = max(y for _, y in layout.positions()) + layout.card_height_mm

    assert lowest >= MARK_BAND_MM
    assert layout.page_height_mm - highest >= MARK_BAND_MM


def test_a_landscape_grid_also_leaves_the_band() -> None:
    layout = SheetLayout.of(CardOrientation.LANDSCAPE)
    lowest = min(y for _, y in layout.positions())

    assert lowest >= MARK_BAND_MM


def test_a_layout_built_by_hand_reports_its_orientation() -> None:
    wide = SheetLayout(card_width_mm=85.6, card_height_mm=53.98)

    assert wide.orientation is CardOrientation.LANDSCAPE
