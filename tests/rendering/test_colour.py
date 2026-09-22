"""Tests for the colour measurements the palette is chosen against."""

import pytest

from maeyomi.rendering.colour import (
    ColourVision,
    contrast_ratio,
    delta_e,
    greyscale,
    relative_luminance,
    simulate,
)

WHITE = (1.0, 1.0, 1.0)
BLACK = (0.0, 0.0, 0.0)
MID_RED = (0.8, 0.2, 0.2)


def test_white_has_full_luminance_and_black_has_none() -> None:
    assert relative_luminance(WHITE) == pytest.approx(1.0)
    assert relative_luminance(BLACK) == pytest.approx(0.0)


def test_the_extreme_contrast_ratio_is_twenty_one_to_one() -> None:
    assert contrast_ratio(WHITE, BLACK) == pytest.approx(21.0, abs=0.01)


def test_contrast_does_not_depend_on_which_colour_comes_first() -> None:
    assert contrast_ratio(WHITE, MID_RED) == pytest.approx(contrast_ratio(MID_RED, WHITE))


def test_a_colour_has_no_contrast_with_itself() -> None:
    assert contrast_ratio(MID_RED, MID_RED) == pytest.approx(1.0)


def test_greyscale_returns_a_neutral_colour_of_the_same_lightness() -> None:
    grey = greyscale(MID_RED)

    assert grey[0] == grey[1] == grey[2]
    assert relative_luminance(grey) == pytest.approx(relative_luminance(MID_RED), abs=0.01)


@pytest.mark.parametrize("vision", list(ColourVision))
def test_every_simulation_returns_a_colour_inside_the_gamut(vision: ColourVision) -> None:
    simulated = simulate(MID_RED, vision)

    assert len(simulated) == 3
    assert all(0.0 <= channel <= 1.0 for channel in simulated)


@pytest.mark.parametrize("vision", list(ColourVision))
def test_grey_is_unchanged_by_every_simulation(vision: ColourVision) -> None:
    grey = (0.5, 0.5, 0.5)

    simulated = simulate(grey, vision)

    assert simulated == pytest.approx(grey, abs=0.05)


def test_red_and_green_become_alike_to_a_deuteranope() -> None:
    red, green = (0.80, 0.20, 0.20), (0.20, 0.70, 0.20)

    normal = delta_e(red, green)
    deutan = delta_e(
        simulate(red, ColourVision.DEUTERANOPIA), simulate(green, ColourVision.DEUTERANOPIA)
    )

    assert deutan < normal / 2


def test_a_colour_has_no_difference_from_itself() -> None:
    assert delta_e(MID_RED, MID_RED) == pytest.approx(0.0, abs=1e-9)


def test_black_and_white_are_the_largest_difference_there_is() -> None:
    assert delta_e(BLACK, WHITE) == pytest.approx(100.0, abs=0.5)
