"""Random sheets for any device, each card the device's own reading of its barcode.

The Barcode Battler II keeps its generator, which samples values and inverts
them. Every other device is handled the way the machines were played: a
barcode is drawn at random, read the way that device reads it, and kept when
it is a fighter whose numbers sit inside the requested ranges. Nothing is
adjusted after the read, so a printed card always shows what the device will.

A Datach code is kept only when every Datach reader reads it at any swipe
speed, per `maeyomi.datach.dbz_reader`, and a game's numbers are held to the
three ranges in the order the game prints them. A game whose reader takes no
product barcode reads only the cards in its own list, so its sheet is drawn
from that list, and so is Battle Rush's, since no random code reads as one of
its robot units.
"""

import random
from dataclasses import dataclass
from functools import cache
from typing import Final

from maeyomi.barcode.geometry import Symbology, symbology_of
from maeyomi.bb1.card import FirstBattlerCard
from maeyomi.datach.dbz import DbzCard, DbzKind
from maeyomi.datach.dbz_reader import Readability, readability
from maeyomi.datach.dbz_solve import unread_fields
from maeyomi.datach.game_card import DatachCard
from maeyomi.datach.game_reader import printable
from maeyomi.datach.game_types import GameEntry, GameOrder
from maeyomi.datach.games import GAMES, game_for
from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.double.card import DoubleCard
from maeyomi.generator.random_cards import ATTEMPTS_PER_CARD, generate_random
from maeyomi.models.card_request import CardRequest
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device
from maeyomi.models.generated_card import AnyCard, CardResult, GeneratedCard
from maeyomi.registry import not_read, printable_as
from maeyomi.rendering.face import face_of
from maeyomi.said import Said

BODY_DIGITS: Final = 12
LISTED_GAMES: Final = frozenset({Device.DATACH_BATTLE_RUSH})
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
        for key, field in zip(game.stat_keys, REQUEST_FIELDS, strict=False)
    },
}


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
        return DeviceBatch(requested=count, reason=not_read(device, unread))
    if _listed_only(device):
        return _draw_listed(device, count, random.Random(seed))
    return _draw_batch(device, count, template, random.Random(seed), count * attempts_per_card)


@cache
def holds_ranges(device: Device) -> bool:
    """Whether a sheet for the device can be held to the three number ranges."""
    if _listed_only(device):
        return False
    game = game_for(device)
    if game is None:
        return True
    if game.strongest is None:
        return False
    return any(tile.key in FIELD_OF_TILE for tile in face_of(game.strongest()).tiles)


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


def _listed_only(device: Device) -> bool:
    """Whether the device reads only the cards in its own list."""
    return device in LISTED_GAMES or symbology_of(device) is not Symbology.EAN


def _draw_listed(device: Device, count: int, rng: random.Random) -> DeviceBatch:
    """Distinct cards drawn from the game's own list, each named after the card it is."""
    game = GAMES[device]
    entries = [entry for entry in game.entries() if entry.kind in game.drawable]
    chosen = rng.sample(entries, min(count, len(entries)))
    cards = tuple(
        GeneratedCard(name=entry.english, barcode=card.barcode, character=card)
        for entry in chosen
        if (card := game.build(_order_for(entry))) is not None
    )
    reason = "" if len(cards) >= count else _listed_reason(len(cards))
    return DeviceBatch(cards=cards, requested=count, reason=reason)


def _order_for(entry: GameEntry) -> GameOrder:
    """An order for one listed card, with no number held to a range."""
    anything = Constraint.anything()
    return GameOrder(entry.ident, (anything, anything, anything))


def _listed_reason(available: int) -> str:
    """Explain a sheet larger than the game's list."""
    return Said(
        f"the game reads only {available} cards, so a sheet holds at most {available}",
        f"この ゲームが よむ カードは {available}まい だけ",
    )


def _random_code(rng: random.Random) -> str:
    """A valid EAN-13 with random digits."""
    body = "".join(str(rng.randrange(10)) for _ in range(BODY_DIGITS))
    return body + str(expected_check_digit(body))


def _reads_everywhere(device: Device, code: str) -> bool:
    """Whether the device reads the code at any swipe speed."""
    game = game_for(device)
    if game is not None:
        return printable(code) or not game.datach_reader
    return device is not Device.DATACH_DBZ or readability(code) is Readability.READS


def _admits(template: CardRequest, card: CardResult) -> bool:
    """Whether a read card is a fighter of the asked race with numbers inside the ranges."""
    if not _is_fighter(card) or not _race_matches(template, card):
        return False
    return all(
        getattr(template, FIELD_OF_TILE[tile.key]).admits(tile.value)
        for tile in face_of(card).tiles
        if tile.key in FIELD_OF_TILE
    )


def _is_fighter(card: CardResult) -> bool:
    """A fighter or an enemy to fight, or whatever else the game draws, never a plain item."""
    if isinstance(card, DbzCard):
        return card.kind is not DbzKind.ITEM
    if isinstance(card, DatachCard):
        return card.kind in GAMES[card.game].drawable
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
    return Said(
        f"produced {produced} of {requested} distinct cards after {budget} barcodes; "
        "the requested ranges admit too few of them",
        f"{requested} まいの うち {produced} まいしか つくれなかった。"
        "すうじの はんいを ひろげて みて",
    )
