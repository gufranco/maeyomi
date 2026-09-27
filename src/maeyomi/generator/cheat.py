"""The strongest card the device can be handed, for the cheat code.

Nothing here is invented. The card is found by walking every front-read
fighter at full hit points through the decoder's own stat arithmetic, keeping
the one that fights with the most strength and defence together, and refusing
any combination that passes through an unresolved branch. The winner is then
assembled, decoded, and compared field by field, exactly as every other
generated card is.

What comes out is a mechanical fighter with 99900 HP that displays 14600 ST and
19900 DF and fights with 24600 ST. The hidden strength is the device's own, per
barcodebattler.net/page21.htm: strength digits of 46 add a second bonus that a
fight uses and the display never shows. See `MAX_BATTLE_STAT` in
`front_solver.py`.
"""

from typing import Final

from maeyomi.decoder.decode import decode
from maeyomi.decoder.front_read import adjusted_stats
from maeyomi.generator.front_solver import (
    MARKER_SPEED_DIGIT,
    MAX_DIGIT_PAIR,
    MAX_HP_DISPLAY,
    assemble,
)
from maeyomi.generator.quarantine import quarantines_digits
from maeyomi.models.character import DISPLAY_SCALE
from maeyomi.models.generated_card import GeneratedCard
from maeyomi.models.race import Race

DEFAULT_CHEAT_NAME: Final = "Maximus Cheatimus"
STRONGEST_MAGICIAN_JOB: Final = 9
ATTACK_DOUBLED: Final = 18


def strongest_card(name: str = DEFAULT_CHEAT_NAME) -> GeneratedCard:
    """Return the strongest front-read fighter, verified through the decoder."""
    hp_units = MAX_HP_DISPLAY // DISPLAY_SCALE
    race, st_digits, df_digits = max(
        _candidates(hp_units), key=lambda candidate: _strength(hp_units, *candidate)
    )
    barcode = assemble(
        hp_units=hp_units,
        st_digits=st_digits,
        df_digits=df_digits,
        race=race,
        job=STRONGEST_MAGICIAN_JOB,
        speed=MARKER_SPEED_DIGIT,
        special=ATTACK_DOUBLED,
    )
    return GeneratedCard(name=name, barcode=barcode, character=decode(barcode))


def _candidates(hp_units: int) -> list[tuple[Race, int, int]]:
    """Every fighter digit combination that avoids an unresolved branch."""
    digits = range(MAX_DIGIT_PAIR + 1)
    return [
        (race, st_digits, df_digits)
        for race in Race
        if race.is_fighter
        for st_digits in digits
        for df_digits in digits
        if not quarantines_digits(race, hp_units=hp_units, st_digits=st_digits, df_digits=df_digits)
    ]


def _strength(hp_units: int, race: Race, st_digits: int, df_digits: int) -> tuple[int, int, int]:
    """Rank by fighting strength and defence together, then the weaker, then the display."""
    stats = adjusted_stats(race, hp_units=hp_units, st_digits=st_digits, df_digits=df_digits)
    fighting = stats.battle_st + stats.battle_df
    return (fighting, min(stats.battle_st, stats.battle_df), stats.st + stats.df)
