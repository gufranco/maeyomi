"""Games where a barcode sets off one effect from a fixed list.

Lupin III, Donald Duck, Spider-Man and Alice no Paint Adventure read a code
through the Barcode Battler II Interface on their password screen and match it
against rules in their program. A code that matches a rule sets off that
rule's effect, such as a cheat or a jump to a later chapter; any other code
does nothing. Each game's module holds its rule and the effects it lists,
every one of them seen in the game running in MAME.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from maeyomi.datach.game_card import DatachCard, GameKind
from maeyomi.decoder.validation import validate_barcode
from maeyomi.models.device import Device

type Pair = tuple[str, str]

EAN_13: Final = 13
NO_EFFECT_IDENT: Final = -1


@dataclass(frozen=True, slots=True)
class Effect:
    """One thing a code can make the game do, and a code seen doing it in MAME.

    `screen` is 0 for the game's own screen, or 1 onwards for the further screens
    it lists, in their order.
    """

    ident: int
    name: Pair
    detail: Pair
    example: str
    screen: int = 0


@dataclass(frozen=True, slots=True)
class Screen:
    """One more place a game reads a code, and its rule from the digits to an effect."""

    name: Pair
    rule: Callable[[str], int | None]


@dataclass(frozen=True, slots=True)
class EffectGame:
    """A game's rule from thirteen digits to an effect, and the effects it lists.

    `rule` takes the digits as the game receives them, an EAN-8 led by five
    zeros, and returns the effect's ident or None. A code is read as the first
    screen whose rule sets something off: the game's own `screen` first, then
    `more` in order.
    """

    device: Device
    rule: Callable[[str], int | None]
    effects: tuple[Effect, ...]
    strongest: int
    screen: Pair
    more: tuple[Screen, ...] = ()


def decode_effect(code: str, game: EffectGame) -> DatachCard:
    """What a barcode sets off in the game, raising a typed error for a malformed one."""
    normalised = validate_barcode(code)
    digits = normalised.rjust(EAN_13, "0")
    rules = (game.rule, *(screen.rule for screen in game.more))
    ident = next((found for found in (rule(digits) for rule in rules) if found is not None), None)
    if ident is None:
        return DatachCard(normalised, game.device, GameKind.NO_EFFECT, NO_EFFECT_IDENT)
    return DatachCard(normalised, game.device, GameKind.EFFECT, ident)


def build_effect(ident: int, game: EffectGame) -> DatachCard | None:
    """A code that sets off the effect, or None when the game has no such effect."""
    effect = effect_of(ident, game)
    return None if effect is None else decode_effect(effect.example, game)


def strongest_effect(game: EffectGame) -> DatachCard:
    """The effect that helps the player most."""
    effect = effect_of(game.strongest, game)
    return decode_effect("" if effect is None else effect.example, game)


def screen_of(effect: Effect, game: EffectGame) -> Pair:
    """Where the game reads the code that sets off this effect."""
    return game.screen if effect.screen == 0 else game.more[effect.screen - 1].name


def effect_of(ident: int, game: EffectGame) -> Effect | None:
    """The listed effect with this ident, if the game has it."""
    return next((effect for effect in game.effects if effect.ident == ident), None)
