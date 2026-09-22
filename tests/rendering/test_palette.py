"""Tests that the printed palette survives a grey printer and colour blindness.

Two things are being guarded. A commercial printer often runs the job in black
and white, so every colour has to carry its meaning as a tone. And roughly one
boy in twelve does not see red and green apart, so no two things a player must
tell apart may differ by hue alone.

The thresholds are WCAG 2.2: 4.5 to 1 for text on a background, 3 to 1 for a
graphic against its background. The 20 unit floor on colour difference is the
CIE 1976 distance at which two colours read as clearly different rather than as
two shades of one colour.
"""

from itertools import combinations

import pytest

from barcode_battler.models.race import Race
from barcode_battler.rendering.colour import (
    ColourVision,
    contrast_ratio,
    delta_e,
    greyscale,
    simulate,
)
from barcode_battler.rendering.icons import RACE_COLOURS, STAT_STYLES
from barcode_battler.rendering.labels import race_label

WHITE = (1.0, 1.0, 1.0)
TEXT_CONTRAST = 4.5
GRAPHIC_CONTRAST = 3.0
DISTINCT_DELTA_E = 20.0
TONE_STEP = 1.15
TILE_TONE_STEP = 1.08
FAMILY_TONE_STEP = 1.5

FIGHTERS = [race for race in Race if race.is_fighter]
SAME_ICON_PAIRS = [
    (Race.SINGLE_USE_WEAPON, Race.WEAPON),
    (Race.SINGLE_USE_ARMOUR, Race.ARMOUR),
]


@pytest.mark.parametrize("race", list(Race))
def test_white_text_is_readable_on_every_band(race: Race) -> None:
    assert contrast_ratio(RACE_COLOURS[race], WHITE) >= TEXT_CONTRAST


@pytest.mark.parametrize("race", list(Race))
def test_every_band_stays_readable_once_the_page_is_printed_in_grey(race: Race) -> None:
    assert contrast_ratio(greyscale(RACE_COLOURS[race]), WHITE) >= TEXT_CONTRAST


@pytest.mark.parametrize("vision", [None, *ColourVision])
def test_the_fighter_bands_stay_apart_for_every_kind_of_colour_vision(
    vision: ColourVision | None,
) -> None:
    for first, second in combinations(FIGHTERS, 2):
        one, other = RACE_COLOURS[first], RACE_COLOURS[second]
        if vision is not None:
            one, other = simulate(one, vision), simulate(other, vision)
        assert delta_e(one, other) >= DISTINCT_DELTA_E, f"{first.name} and {second.name}"


def test_the_fighter_bands_print_as_different_tones_of_grey() -> None:
    for first, second in combinations(FIGHTERS, 2):
        tone = contrast_ratio(greyscale(RACE_COLOURS[first]), greyscale(RACE_COLOURS[second]))
        assert tone >= TONE_STEP, f"{first.name} and {second.name} print as the same grey"


@pytest.mark.parametrize(("first", "second"), SAME_ICON_PAIRS)
def test_two_races_sharing_an_icon_are_told_apart_without_colour(first: Race, second: Race) -> None:
    assert race_label(first).english != race_label(second).english
    tone = contrast_ratio(greyscale(RACE_COLOURS[first]), greyscale(RACE_COLOURS[second]))
    assert tone >= FAMILY_TONE_STEP


def test_no_two_races_are_told_apart_by_colour_alone() -> None:
    assert len({race_label(race).english for race in Race}) == len(Race)


@pytest.mark.parametrize("key", list(STAT_STYLES))
def test_a_stat_icon_stands_out_against_its_tile(key: str) -> None:
    style = STAT_STYLES[key]

    assert contrast_ratio(style.icon, style.tint) >= GRAPHIC_CONTRAST


@pytest.mark.parametrize("key", list(STAT_STYLES))
def test_a_stat_icon_stands_out_on_a_grey_printer(key: str) -> None:
    style = STAT_STYLES[key]

    assert contrast_ratio(greyscale(style.icon), greyscale(style.tint)) >= GRAPHIC_CONTRAST


def test_the_three_stat_tiles_print_as_different_tones_of_grey() -> None:
    for first, second in combinations(STAT_STYLES, 2):
        tone = contrast_ratio(
            greyscale(STAT_STYLES[first].tint), greyscale(STAT_STYLES[second].tint)
        )
        assert tone >= TILE_TONE_STEP, f"{first} and {second} print as the same grey"
