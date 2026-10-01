"""The cheat cards every machine and game offers, one kind or several.

The page and the command line both read this one list. The first kind is the
default. A machine offers its strongest fighter and its items at their top; a
game offers the kinds `game_cheats` builds from the game's own tables. A card
with no name typed is named after its kind, the default kind keeping the cheat
name, so a sheet of every kind never repeats one name on all its cards.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from maeyomi.bb1.cheat import strongest_first_card, strongest_first_items
from maeyomi.datach.dbz_cheat import strongest_dbz_card, strongest_dbz_items
from maeyomi.double.cheat import strongest_double_card, strongest_double_items
from maeyomi.game_cheats import GameCheat, game_cheats
from maeyomi.generator.cheat import DEFAULT_CHEAT_NAME, strongest_card
from maeyomi.generator.cheat_items import strongest_items
from maeyomi.models.character import HIGHEST_WARRIOR_JOB
from maeyomi.models.device import Device
from maeyomi.models.generated_card import AnyCard, GeneratedCard
from maeyomi.said import Said


@dataclass(frozen=True, slots=True)
class CheatKind:
    """One kind of cheat card: its key, its name in both languages, and its cards."""

    key: str
    english: str
    japanese: str
    cards: Callable[[str], tuple[AnyCard, ...]]


ALL: Final = "all"
"""The key that asks for every kind at once."""
FIGHTER: Final = ("fighter", "Strongest fighter", "いちばん つよい キャラクター")
ITEMS: Final = ("items", "Every item at its top", "アイテム ぜんぶ さいだい")
WARRIOR: Final = ("warrior", "Strongest warrior, who can hold every item", "いちばん つよい せんし")

MACHINES: Final[dict[Device, tuple[CheatKind, ...]]] = {
    Device.BB2: (
        CheatKind(*FIGHTER, lambda name: (strongest_card(name),)),
        CheatKind(*WARRIOR, lambda name: (strongest_card(name, job=HIGHEST_WARRIOR_JOB),)),
        CheatKind(*ITEMS, lambda _: strongest_items()),
    ),
    Device.BB1: (
        CheatKind(*FIGHTER, lambda name: (strongest_first_card(name),)),
        CheatKind(*ITEMS, lambda _: strongest_first_items()),
    ),
    Device.DOUBLE: (
        CheatKind(*FIGHTER, lambda name: (strongest_double_card(name),)),
        CheatKind(*ITEMS, lambda _: strongest_double_items()),
    ),
    Device.DATACH_DBZ: (
        CheatKind(*FIGHTER, lambda name: (strongest_dbz_card(name),)),
        CheatKind(*ITEMS, lambda _: strongest_dbz_items()),
    ),
}


def cheat_kinds(device: Device) -> tuple[CheatKind, ...]:
    """Every cheat kind the device offers, the default first."""
    machine = MACHINES.get(device)
    if machine is not None:
        return machine
    return tuple(_from_game(cheat) for cheat in game_cheats(device))


def _from_game(cheat: GameCheat) -> CheatKind:
    """A game's cheat kind, its cards printed under the name asked for."""
    return CheatKind(
        cheat.key,
        cheat.english,
        cheat.japanese,
        lambda name: tuple(
            GeneratedCard(name=name, barcode=card.barcode, character=card) for card in cheat.cards()
        ),
    )


def cheat_kind(device: Device, key: str | None) -> CheatKind:
    """The kind asked for by key, the default when none is, or a ValueError naming the kinds."""
    kinds = cheat_kinds(device)
    if not kinds:
        message = Said(
            f"{device.english} cards carry no numbers, so none is stronger than another",
            f"{device.japanese} の カードには すうじが ないので、いちばん つよい カードは ない",
        )
        raise ValueError(message)
    wanted = (key or "").strip().lower()
    chosen = kinds[0] if not wanted else next((k for k in kinds if k.key == wanted), None)
    if chosen is not None:
        return chosen
    listed = ", ".join(kind.key for kind in kinds)
    message = Said(
        f"{device.english} has no cheat card {key!r}; its kinds are {listed}",
        f"{device.japanese} に {key!r} という チートカードは ない。えらべるのは {listed}",
    )
    raise ValueError(message)


def kind_name(device: Device, kind: CheatKind) -> str:
    """The name a kind's cards carry when none is typed: the cheat name, or the kind's own."""
    return DEFAULT_CHEAT_NAME if kind.key == cheat_kind(device, None).key else kind.english


def cheat_cards(device: Device, key: str | None, name: str | None) -> tuple[AnyCard, ...]:
    """The cards of one kind, or of every kind once each, each under its own name, for `all`."""
    if (key or "").strip().lower() != ALL:
        chosen = cheat_kind(device, key)
        return chosen.cards(name or kind_name(device, chosen))
    if name:
        message = Said(
            "a name is printed on one kind of cheat card; "
            "every kind together is named kind by kind",
            "なまえは 1しゅるいの チートカードに つけられる。"
            "ぜんぶ いっしょの ときは しゅるいの なまえに なる",
        )
        raise ValueError(message)
    kinds = cheat_kinds(device) or (cheat_kind(device, None),)
    every = [card for kind in kinds for card in kind.cards(kind_name(device, kind))]
    return tuple(
        card for place, card in enumerate(every) if card.barcode not in _barcodes(every[:place])
    )


def _barcodes(cards: list[AnyCard]) -> frozenset[str]:
    """The barcodes of the cards already chosen."""
    return frozenset(card.barcode for card in cards)
