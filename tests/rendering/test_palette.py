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

from dataclasses import replace
from itertools import combinations

import pytest

from maeyomi.models.race import Race
from maeyomi.rendering.colour import (
    ColourVision,
    contrast_ratio,
    delta_e,
    greyscale,
    simulate,
)
from maeyomi.rendering.icons import RACE_COLOURS, STAT_STYLES
from maeyomi.rendering.labels import race_label
from maeyomi.rendering.palette import (
    DISTINCT_DELTA_E,
    FAMILY_TONE_STEP,
    FIGHTERS,
    GRAPHIC_CONTRAST,
    SAME_ICON_PAIRS,
    TEXT_CONTRAST,
    TILE_TONE_STEP,
    TONE_STEP,
    WHITE,
    audit_palette,
)


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


def test_the_audit_agrees_with_every_threshold_checked_above() -> None:
    assert audit_palette() == ()


def test_the_audit_names_two_kinds_that_print_as_one_grey(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first, second = FIGHTERS[0], FIGHTERS[1]
    monkeypatch.setitem(RACE_COLOURS, second, RACE_COLOURS[first])

    failures = audit_palette()

    assert any("print as the same grey" in failure for failure in failures)
    assert any(second.name.lower() in failure for failure in failures)


def test_the_audit_names_a_family_that_lost_its_tone_step(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    single_use, lasting = SAME_ICON_PAIRS[0]
    monkeypatch.setitem(RACE_COLOURS, single_use, RACE_COLOURS[lasting])

    assert any("share a pictogram and a grey" in failure for failure in audit_palette())


def test_the_audit_names_a_band_white_text_cannot_sit_on(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(RACE_COLOURS, Race.HUMAN, WHITE)

    assert any("under 4.5" in failure for failure in audit_palette())


def test_the_audit_names_a_stat_icon_that_vanished_into_its_tile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    style = STAT_STYLES["HP"]
    monkeypatch.setitem(STAT_STYLES, "HP", replace(style, icon=style.tint))

    assert any("on its tile" in failure for failure in audit_palette())


def test_the_audit_names_two_tiles_that_print_as_one_grey(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(STAT_STYLES, "ST", STAT_STYLES["HP"])

    assert any("print as the same grey" in failure for failure in audit_palette())
