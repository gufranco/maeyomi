"""Render what was asked for beside what was produced.

A custom card is never accepted silently when it differs from the request, so
the three columns are printed whether or not anything differs.
"""

from collections.abc import Sequence

from barcode_battler.models.card_request import CardRequest
from barcode_battler.models.character import BarcodeBattlerCharacter

DISCLAIMER = (
    "These cards were verified against this project's own decoder. They have "
    "not been tested on a physical Barcode Battler II."
)
DISCLAIMER_JA = (
    "これらのカードは このプログラムの デコーダーで けんしょう しています。"
    "バーコードバトラーII の 実機では まだ テストされていません。"
)
UNCONSTRAINED = ("any", "-")


def comparison_lines(request: CardRequest, character: BarcodeBattlerCharacter) -> list[str]:
    """Return one line per attribute showing requested, generated and difference."""
    rows = [
        ("HP", str(request.hp), str(character.hp)),
        ("ST", str(request.st), str(character.st)),
        ("DF", str(request.df), str(character.df)),
        ("Race", _race_name(request), character.race.name.lower()),
        ("Job", _optional(request.job), str(character.job)),
        ("Class", _optional(_requested_class(request)), _generated_class(character)),
        ("Speed", _optional(request.speed), _optional(character.speed)),
        ("Ability", _optional(request.special), f"{character.special.code:02d}"),
    ]
    header = f"{'Field':<9}{'Requested':<16}{'Generated':<16}Difference"
    return [header, "-" * len(header), *[_row(*row) for row in rows]]


def shortfall_lines(produced: int, requested: int, reason: str) -> Sequence[str]:
    """Explain a batch that could not be filled."""
    return [f"produced {produced} of {requested} cards", reason]


def _row(field: str, requested: str, generated: str) -> str:
    """Format one comparison row, marking a value that came out different."""
    differs = requested not in UNCONSTRAINED and requested != generated
    return f"{field:<9}{requested:<16}{generated:<16}{'differs' if differs else ''}"


def _optional(value: object) -> str:
    """Render a value that may be absent."""
    return "-" if value is None else str(value)


def _race_name(request: CardRequest) -> str:
    """The requested race name, or a dash when no race was requested.

    Race is an IntEnum whose first member is zero, so this tests for None
    rather than for truth.
    """
    return request.race.name.lower() if request.race is not None else "-"


def _requested_class(request: CardRequest) -> str | None:
    """The requested class name, if one was requested."""
    return request.character_class.value if request.character_class else None


def _generated_class(character: BarcodeBattlerCharacter) -> str:
    """The generated class name, or item for a non-fighter."""
    return character.character_class.value if character.character_class else "item"
