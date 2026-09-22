"""A bound on one requested attribute value.

A request states each attribute as an exact value, a range, a one-sided bound,
or nothing at all. The solver walks the admitted values in ascending order, so
a given request always produces the same barcode.
"""

from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Constraint:
    """An inclusive lower and upper bound, either of which may be absent."""

    minimum: int | None = None
    maximum: int | None = None

    def __post_init__(self) -> None:
        """Reject a range whose ends are the wrong way round."""
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            message = f"minimum {self.minimum} is above maximum {self.maximum}"
            raise ValueError(message)

    @classmethod
    def anything(cls) -> Constraint:
        """Build a constraint that admits every value."""
        return cls()

    @classmethod
    def exactly(cls, value: int) -> Constraint:
        """Build a constraint that admits one value."""
        return cls(minimum=value, maximum=value)

    @classmethod
    def at_least(cls, value: int) -> Constraint:
        """Build a constraint with a lower bound only."""
        return cls(minimum=value)

    @classmethod
    def at_most(cls, value: int) -> Constraint:
        """Build a constraint with an upper bound only."""
        return cls(maximum=value)

    @classmethod
    def between(cls, minimum: int, maximum: int) -> Constraint:
        """Build a constraint with both bounds."""
        return cls(minimum=minimum, maximum=maximum)

    def __str__(self) -> str:
        """Render the bounds for a report."""
        if self.is_exact:
            return str(self.minimum)
        if self.minimum is None and self.maximum is None:
            return "any"
        if self.maximum is None:
            return f"at least {self.minimum}"
        if self.minimum is None:
            return f"at most {self.maximum}"
        return f"{self.minimum} to {self.maximum}"

    def admits(self, value: int) -> bool:
        """Whether the value satisfies both bounds."""
        if self.minimum is not None and value < self.minimum:
            return False
        return not (self.maximum is not None and value > self.maximum)

    @property
    def is_exact(self) -> bool:
        """Whether exactly one value satisfies this constraint."""
        return self.minimum is not None and self.minimum == self.maximum

    @property
    def exact_value(self) -> int | None:
        """The single admitted value, or None when more than one is admitted."""
        return self.minimum if self.is_exact else None

    def values(self, *, step: int, ceiling: int, floor: int = 0) -> Iterator[int]:
        """Walk every admitted value in ascending order, bounded by floor and ceiling."""
        start = floor if self.minimum is None else max(floor, self.minimum)
        stop = ceiling if self.maximum is None else min(ceiling, self.maximum)
        aligned = start + (-start) % step
        return iter(range(aligned, stop + 1, step))
