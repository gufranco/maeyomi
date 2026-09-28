"""Random sheets for any device, each card the device's own reading of its barcode.

The Barcode Battler II keeps its generator, which samples values and inverts
them. Every other device is handled the way the machines were played: a
barcode is drawn at random, read the way that device reads it, and kept when
it is a fighter whose numbers sit inside the requested ranges. Nothing is
adjusted after the read, so a printed card always shows what the device will.

A Datach code is kept only when every Datach reader reads it at any swipe
speed, per `maeyomi.datach.dbz_reader`, and a game's numbers are held to the
three ranges in the order the game prints them.
"""

import random
from dataclasses import dataclass
from typing import Final

from maeyomi.bb1.card import FirstBattlerCard
from maeyomi.datach.dbz import DbzCard, DbzKind
from maeyomi.datach.dbz_reader import Readability, readability
from maeyomi.datach.dbz_solve import unread_fields
from maeyomi.datach.game_card import DatachCard, GameKind
from maeyomi.datach.game_reader import printable
from maeyomi.datach.games import GAMES, game_for
from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.double.card import DoubleCard
from maeyomi.generator.random_cards import ATTEMPTS_PER_CARD, generate_random
from maeyomi.models.card_request import CardRequest
from maeyomi.models.device import Device
from maeyomi.models.generated_card import AnyCard, CardResult
from maeyomi.registry import GAME_NOT_READ, NOT_READ, printable_as
from maeyomi.rendering.face import face_of

BODY_DIGITS: Final = 12
REQUEST_FIELDS: Final = ("hp", "st", "df")
FIELD_OF_TILE: Final = {
    "HP": "hp",
    "ST": "st",
    "BP": "st",
    "DF": "df",
    "DP": "df",
    **{
        key: field
        for game in GAMES.values()
        for key, field in zip(game.stat_keys, REQUEST_FIELDS, strict=True)
    },
}
FIGHTING_KINDS: Final = frozenset({GameKind.FIGHTER, GameKind.UNIT, GameKind.PLAYER})


@dataclass(frozen=True, slots=True)
class DeviceBatch:
    """The cards one random run produced, and why it fell short if it did."""

    cards: tuple[AnyCard, ...] = ()
    requested: int = 0
    reason: str = ""

    @property
    def shortfall(self) -> int:
        """How many fewer cards were produced than were asked for."""
        return self.requested - len(self.cards)


def random_for(
    device: Device,
    count: int,
    *,
    template: CardRequest,
    seed: int | None = None,
    attempts_per_card: int = ATTEMPTS_PER_CARD,
) -> DeviceBatch:
    """Up to `count` distinct random fighters for the device, inside the template's ranges."""
    if device is Device.BB2:
        second = generate_random(
            count, template=template, seed=seed, attempts_per_card=attempts_per_card
        )
        return DeviceBatch(cards=second.cards, requested=count, reason=second.reason)
    unread = unread_fields(template, back_read=False) if device.is_game else ()
    if unread:
        refusal = NOT_READ if device is Device.DATACH_DBZ else GAME_NOT_READ
        reason = refusal.format(game=device.english, fields=", ".join(unread))
        return DeviceBatch(requested=count, reason=reason)
    return _draw_batch(device, count, template, random.Random(seed), count * attempts_per_card)


def _draw_batch(
    device: Device, count: int, template: CardRequest, rng: random.Random, budget: int
) -> DeviceBatch:
    """Draw barcodes until the batch is full or the budget is spent."""
    cards: list[AnyCard] = []
    seen: set[str] = set()
    for _ in range(budget):
        if len(cards) == count:
            break
        code = _random_code(rng)
        if code in seen or not _reads_everywhere(device, code):
            continue
        if not _admits(template, printable_as(device, code, "").character):
            continue
        seen.add(code)
        cards.append(_named(device, code, len(cards)))
    return DeviceBatch(
        cards=tuple(cards), requested=count, reason=_reason(len(cards), count, budget)
    )


def _random_code(rng: random.Random) -> str:
    """A valid EAN-13 with random digits."""
    body = "".join(str(rng.randrange(10)) for _ in range(BODY_DIGITS))
    return body + str(expected_check_digit(body))


def _reads_everywhere(device: Device, code: str) -> bool:
    """Whether the device reads the code at any swipe speed."""
    if game_for(device) is not None:
        return printable(code)
    return device is not Device.DATACH_DBZ or readability(code) is Readability.READS


def _admits(template: CardRequest, card: CardResult) -> bool:
    """Whether a read card is a fighter of the asked race with numbers inside the ranges."""
    if not _is_fighter(card) or not _race_matches(template, card):
        return False
    return all(
        getattr(template, FIELD_OF_TILE[tile.key]).admits(tile.value)
        for tile in face_of(card).tiles
    )


def _is_fighter(card: CardResult) -> bool:
    """A fighter or an enemy to fight, never an item."""
    if isinstance(card, DbzCard):
        return card.kind is not DbzKind.ITEM
    if isinstance(card, DatachCard):
        return card.kind in FIGHTING_KINDS
    if isinstance(card, (FirstBattlerCard, DoubleCard)) and card.race is None:
        return True
    return card.race is not None and card.race.is_fighter


def _race_matches(template: CardRequest, card: CardResult) -> bool:
    """Whether the card is of the race asked for, when one was asked for."""
    if template.race is None:
        return True
    return not isinstance(card, DbzCard | DatachCard) and card.race is template.race


def _named(device: Device, code: str, index: int) -> AnyCard:
    """The card again, named after the kind the device reads it as."""
    kind = face_of(printable_as(device, code, "").character).kind.english
    return printable_as(device, code, f"{kind} {index + 1:02d}")


def _reason(produced: int, requested: int, budget: int) -> str:
    """Explain a batch that could not be filled."""
    if produced >= requested:
        return ""
    return (
        f"produced {produced} of {requested} distinct cards after {budget} barcodes; "
        "the requested ranges admit too few of them"
    )
