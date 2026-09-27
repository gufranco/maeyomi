"""Render what was asked for beside what was produced.

A custom card is never accepted silently when it differs from the request, so
the three columns are printed whether or not anything differs.
"""

from collections.abc import Sequence

from maeyomi.bb1.card import FirstBattlerCard
from maeyomi.double.card import DoubleCard
from maeyomi.generator.equip import ALL_JOBS, equipping_jobs
from maeyomi.models.card_request import CardRequest
from maeyomi.models.character import BarcodeBattlerCharacter
from maeyomi.models.generated_card import AnyCard

DISCLAIMER = (
    "These cards were verified against this project's own decoder and read on a "
    "physical Barcode Battler II."
)
DISCLAIMER_JA = (
    "これらのカードは このプログラムの デコーダーで けんしょうし、"
    "バーコードバトラーII の 実機で よみとり かくにん しています。"
)
FIRST_DEVICE_DISCLAIMER = (
    "Cards for the first Barcode Battler were verified against this project's own "
    "decoder, which reproduces the published card lists, and were never read on a "
    "physical first Barcode Battler."
)
FIRST_DEVICE_DISCLAIMER_JA = (
    "初代バーコードバトラー用の カードは このプログラムの デコーダーで けんしょうしました。"
    "デコーダーは こうかいされた カードリストを さいげんしますが、"
    "初代の 実機では まだ よみとって いません。"
)
DOUBLE_DISCLAIMER = (
    "Cards for the Barcode Battler II Double were verified against this project's "
    "own decoder, which reproduces the 正伝3 list bundled with it, and were never read "
    "on a physical Double."
)
DOUBLE_DISCLAIMER_JA = (
    "バーコードバトラーII² 用の カードは このプログラムの デコーダーで けんしょうしました。"
    "デコーダーは どうこんの 正伝3 の カードリストを さいげんしますが、"
    "II² の 実機では まだ よみとって いません。"
)
UNCONSTRAINED = ("any", "-")


def disclaimers(cards: Sequence[AnyCard]) -> list[str]:
    """What was verified, one line per device the cards were made for, in a fixed order."""
    kinds = {type(card.character) for card in cards}
    lines = [
        (BarcodeBattlerCharacter, DISCLAIMER),
        (FirstBattlerCard, FIRST_DEVICE_DISCLAIMER),
        (DoubleCard, DOUBLE_DISCLAIMER),
    ]
    return [line for kind, line in lines if kind in kinds]


def comparison_lines(request: CardRequest, character: BarcodeBattlerCharacter) -> list[str]:
    """Return one line per attribute showing requested, generated and difference."""
    rows = [
        ("HP", str(request.hp), str(character.hp)),
        ("ST", str(request.st), str(character.st)),
        ("DF", str(request.df), str(character.df)),
        ("PP", str(request.pp), str(character.pp)),
        ("MP", str(request.mp), str(character.mp)),
        ("Race", _race_name(request), character.race.name.lower()),
        ("Job", _optional(request.job), str(character.job)),
        ("Class", _optional(_requested_class(request)), _generated_class(character)),
        ("Speed", _optional(request.speed), _optional(character.speed)),
        ("Ability", _optional(request.special), f"{character.special.code:02d}"),
    ]
    return comparison_table(rows)


def comparison_table(rows: Sequence[tuple[str, str, str]]) -> list[str]:
    """Lay out field, requested and generated rows under one header."""
    header = f"{'Field':<9}{'Requested':<16}{'Generated':<16}Difference"
    return [header, "-" * len(header), *[_row(*row) for row in rows]]


def fit_line(fighter_job: int, item: BarcodeBattlerCharacter) -> str:
    """Which jobs can use an item, and whether the fighter it came with is one of them."""
    jobs = equipping_jobs(item)
    fits = "fits this fighter" if fighter_job in jobs else "not this fighter"
    return f"{job_span(jobs)}, {fits}"


def job_span(jobs: Sequence[int]) -> str:
    """Name a set of jobs the short way: every job, a run, or a list."""
    if tuple(jobs) == ALL_JOBS:
        return "every job"
    if list(jobs) == list(range(jobs[0], jobs[-1] + 1)):
        return f"jobs {jobs[0]} to {jobs[-1]}"
    return "jobs " + " and ".join(str(job) for job in jobs)


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
