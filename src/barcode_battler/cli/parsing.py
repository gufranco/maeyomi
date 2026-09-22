"""Turn command line text into typed constraints.

A stat option accepts an exact value, a range, or a one-sided bound, so the
same option serves both the custom and the random command.
"""

import re
from typing import Final

from barcode_battler.models.character_class import CharacterClass
from barcode_battler.models.constraint import Constraint
from barcode_battler.models.race import Race

_EXACT: Final = re.compile(r"^\s*(\d+)\s*$")
_AT_LEAST: Final = re.compile(r"^\s*>=?\s*(\d+)\s*$")
_AT_MOST: Final = re.compile(r"^\s*<=?\s*(\d+)\s*$")
_RANGE: Final = re.compile(r"^\s*(\d+)?\s*-\s*(\d+)?\s*$")
_EXAMPLES: Final = "use 5000, 5000-6000, >=1500 or <=3000"


def parse_constraint(text: str | None) -> Constraint:
    """Parse `5000`, `5000-6000`, `>=1500` or `<=3000` into a constraint."""
    if text is None or not text.strip():
        return Constraint.anything()
    for pattern, build in (
        (_EXACT, Constraint.exactly),
        (_AT_LEAST, Constraint.at_least),
        (_AT_MOST, Constraint.at_most),
    ):
        match = pattern.match(text)
        if match:
            return build(int(match.group(1)))
    return _parse_range(text)


def _parse_range(text: str) -> Constraint:
    """Parse a hyphenated range, with either end optional."""
    span = _RANGE.match(text)
    low = span.group(1) if span else None
    high = span.group(2) if span else None
    if low and high:
        return Constraint.between(int(low), int(high))
    if low:
        return Constraint.at_least(int(low))
    if high:
        return Constraint.at_most(int(high))
    message = f"cannot read {text!r} as a value; {_EXAMPLES}"
    raise ValueError(message)


def parse_race(text: str | None) -> Race | None:
    """Parse a race by name, accepting spaces or hyphens between words."""
    if text is None:
        return None
    key = text.strip().upper().replace(" ", "_").replace("-", "_")
    try:
        return Race[key]
    except KeyError:
        names = ", ".join(race.name.lower() for race in Race)
        message = f"unknown race {text!r}; choose one of {names}"
        raise ValueError(message) from None


def parse_character_class(text: str | None) -> CharacterClass | None:
    """Parse warrior or magician."""
    if text is None:
        return None
    key = text.strip().lower()
    for member in CharacterClass:
        if member.value == key:
            return member
    names = ", ".join(member.value for member in CharacterClass)
    message = f"unknown class {text!r}; choose one of {names}"
    raise ValueError(message)
