"""The rescaling the C1 and C2 game modes apply to a back-read hero card.

Source: `calc_c1_reading` in `src/BarcodeRead.as` of
finalfighter/BarcodeBattler2-Simulator (MIT). It is a separate step rather than
part of the read, because an ordinary battle never applies it.
"""

import dataclasses
from typing import Final

from barcode_battler.models.character import DISPLAY_SCALE, BarcodeBattlerCharacter

HP_DIVISOR: Final = 10
ST_DIVISOR: Final = 10
DF_DIVISOR: Final = 10
ST_BONUS_UNITS: Final = 1
DF_BONUS_UNITS: Final = 3


def rescale_for_c1(character: BarcodeBattlerCharacter) -> BarcodeBattlerCharacter:
    """Return a copy rescaled as the C1 and C2 modes rescale a hero card."""
    return dataclasses.replace(
        character,
        hp=character.hp_units // HP_DIVISOR * DISPLAY_SCALE,
        st=(character.st_units // ST_DIVISOR + ST_BONUS_UNITS) * DISPLAY_SCALE,
        df=(character.df_units // DF_DIVISOR + DF_BONUS_UNITS) * DISPLAY_SCALE,
    )
