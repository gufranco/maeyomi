"""What a caller asks for when it wants a card.

The name is metadata for the printed card and never reaches the barcode. Every
attribute the device actually reads is expressed as a `Constraint`, or as an
exact categorical value.
"""

from dataclasses import dataclass, field

from maeyomi.models.character_class import CharacterClass
from maeyomi.models.constraint import Constraint
from maeyomi.models.race import Race

MAX_JOB_DIGIT = 9
MAX_SPEED_DIGIT = 9
MAX_SPECIAL_CODE = 99


@dataclass(frozen=True, slots=True)
class CardRequest:
    """A set of constraints a generated barcode must satisfy exactly."""

    name: str = ""
    hp: Constraint = field(default_factory=Constraint.anything)
    st: Constraint = field(default_factory=Constraint.anything)
    df: Constraint = field(default_factory=Constraint.anything)
    race: Race | None = None
    job: int | None = None
    character_class: CharacterClass | None = None
    special: int | None = None
    speed: int | None = None

    def __post_init__(self) -> None:
        """Reject a categorical value the barcode cannot carry."""
        self._check("job", self.job, MAX_JOB_DIGIT)
        self._check("speed", self.speed, MAX_SPEED_DIGIT)
        self._check("special", self.special, MAX_SPECIAL_CODE)

    @staticmethod
    def _check(name: str, value: int | None, maximum: int) -> None:
        """Raise when a categorical value falls outside the digits available to it."""
        if value is not None and not 0 <= value <= maximum:
            message = f"{name} must be 0-{maximum}, got {value}"
            raise ValueError(message)
