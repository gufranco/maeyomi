"""The thresholds the printed colours are held to, and a check against them.

The numbers are WCAG 2.2 for contrast, and the CIE 1976 distance at which two
colours read as different colours rather than two shades of one. They live here
rather than in the tests because two things need them: the suite, which fails a
change that breaks the palette, and `doctor`, which re-measures on the machine
that is about to print.
"""

from itertools import combinations
from typing import Final

from maeyomi.models.race import Race
from maeyomi.rendering.colour import (
    Colour,
    ColourVision,
    contrast_ratio,
    delta_e,
    greyscale,
    simulate,
)
from maeyomi.rendering.icons import RACE_COLOURS, STAT_STYLES

WHITE: Final[Colour] = (1.0, 1.0, 1.0)
TEXT_CONTRAST: Final = 4.5
GRAPHIC_CONTRAST: Final = 3.0
DISTINCT_DELTA_E: Final = 20.0
TONE_STEP: Final = 1.15
TILE_TONE_STEP: Final = 1.08
FAMILY_TONE_STEP: Final = 1.5

FIGHTERS: Final = tuple(race for race in Race if race.is_fighter)
SAME_ICON_PAIRS: Final = (
    (Race.SINGLE_USE_WEAPON, Race.WEAPON),
    (Race.SINGLE_USE_ARMOUR, Race.ARMOUR),
)


def audit_palette() -> tuple[str, ...]:
    """Every threshold the current palette misses, named. Empty means it holds."""
    return tuple(
        failure
        for check in (_bands_carry_text, _fighters_stay_apart, _families_differ, _stat_tiles_work)
        for failure in check()
    )


def _bands_carry_text() -> tuple[str, ...]:
    """White type on a coloured band, in colour and once the page is grey."""
    return tuple(
        f"{race.name.lower()} band gives white text {ratio:.2f}:1, under {TEXT_CONTRAST}"
        for race in Race
        for ratio in (
            min(
                contrast_ratio(RACE_COLOURS[race], WHITE),
                contrast_ratio(greyscale(RACE_COLOURS[race]), WHITE),
            ),
        )
        if ratio < TEXT_CONTRAST
    )


def _fighters_stay_apart() -> tuple[str, ...]:
    """Two kinds a player must tell apart, under every kind of colour vision."""
    failures: list[str] = []
    for first, second in combinations(FIGHTERS, 2):
        one, other = RACE_COLOURS[first], RACE_COLOURS[second]
        for vision in (None, *ColourVision):
            seen = (
                (one, other) if vision is None else (simulate(one, vision), simulate(other, vision))
            )
            distance = delta_e(*seen)
            if distance < DISTINCT_DELTA_E:
                how = "normal vision" if vision is None else vision.name.lower()
                failures.append(
                    f"{first.name.lower()} and {second.name.lower()} differ by "
                    f"{distance:.1f} under {how}, under {DISTINCT_DELTA_E}"
                )
        tone = contrast_ratio(greyscale(one), greyscale(other))
        if tone < TONE_STEP:
            failures.append(
                f"{first.name.lower()} and {second.name.lower()} print as the same grey"
            )
    return tuple(failures)


def _families_differ() -> tuple[str, ...]:
    """Two kinds drawn with one pictogram, which only the tone can separate."""
    return tuple(
        f"{first.name.lower()} and {second.name.lower()} share a pictogram and a grey"
        for first, second in SAME_ICON_PAIRS
        if contrast_ratio(greyscale(RACE_COLOURS[first]), greyscale(RACE_COLOURS[second]))
        < FAMILY_TONE_STEP
    )


def _stat_tiles_work() -> tuple[str, ...]:
    """The three numbers, whose icons have to show on their own tiles."""
    failures = [
        f"the {key} icon gives {ratio:.2f}:1 on its tile, under {GRAPHIC_CONTRAST}"
        for key, style in STAT_STYLES.items()
        for ratio in (
            min(
                contrast_ratio(style.icon, style.tint),
                contrast_ratio(greyscale(style.icon), greyscale(style.tint)),
            ),
        )
        if ratio < GRAPHIC_CONTRAST
    ]
    failures += [
        f"the {first} and {second} tiles print as the same grey"
        for first, second in combinations(STAT_STYLES, 2)
        if contrast_ratio(greyscale(STAT_STYLES[first].tint), greyscale(STAT_STYLES[second].tint))
        < TILE_TONE_STEP
    ]
    return tuple(failures)
