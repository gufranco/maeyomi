"""The strongest card the device can be handed, for the cheat code.

Nothing here is invented. The card is found by walking every front-read
fighter at full hit points through the decoder's own stat arithmetic, keeping
the one with the most strength and defence together, and refusing any
combination that passes through one of the two unresolved overflow branches.
The winner is then assembled, decoded, and compared field by field, exactly as
every other generated card is.

What comes out is a mechanical fighter: 99900 HP, 24500 ST and 19900 DF. The
strength is above the 19900 barcodebattler.net publishes, because a
mechanical fighter whose strength digits sit in the dual bonus set collects both
bonuses. See `MAX_STAT_DISPLAY` in `front_solver.py`.
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


def _strength(hp_units: int, race: Race, st_digits: int, df_digits: int) -> tuple[int, int]:
    """Rank by strength and defence together, then by the weaker of the two."""
    st, df = adjusted_stats(race, hp_units=hp_units, st_digits=st_digits, df_digits=df_digits)
    return (st + df, min(st, df))
