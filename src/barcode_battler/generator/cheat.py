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

from barcode_battler.decoder.decode import decode
from barcode_battler.decoder.front_read import adjusted_stats
from barcode_battler.generator.front_solver import (
    MARKER_SPEED_DIGIT,
    MAX_DIGIT_PAIR,
    MAX_HP_DISPLAY,
    assemble,
)
from barcode_battler.generator.quarantine import quarantines_digits
from barcode_battler.models.character import DISPLAY_SCALE
from barcode_battler.models.generated_card import GeneratedCard
from barcode_battler.models.race import Race

DEFAULT_CHEAT_NAME: Final = "Maximus Cheatimus"
STRONGEST_MAGICIAN_JOB: Final = 9
ATTACK_DOUBLED: Final = 18
CHEAT_CODES: Final = frozenset({"IDDQD", "UUDDLRLRBA", "KONAMI", "MAXIMUS", "BATTLER"})
"""Words the interface accepts. They are a joke, not a lock: the endpoint is open."""


def accepted_codes() -> frozenset[str]:
    """Every code the interface accepts, including the card's own barcode.

    The barcode is in the list so that the unlabelled symbol printed at the foot
    of the page is a way in: read it with a phone, type the digits, and the card
    appears.
    """
    return CHEAT_CODES | {strongest_card().barcode}


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
