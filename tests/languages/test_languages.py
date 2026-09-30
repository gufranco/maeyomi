"""Every game's cards say each thing in English on the English side and in Japanese on the other.

A name the game shows in kana has an English form, and a line of English words
is never also the Japanese line. Names the game itself writes in Latin letters,
such as a mobile suit's model number, are the same on both sides.
"""

import re
from collections.abc import Iterator

import pytest

from maeyomi.datach.game_types import CardText, DatachGame, GameOrder
from maeyomi.datach.games import GAMES
from maeyomi.models.constraint import Constraint
from maeyomi.models.device import Device

JAPANESE = re.compile(r"[぀-ヿ㐀-鿿ｦ-ﾟ]")
ENGLISH_WORD = re.compile(r"[a-z]{3,}")
ANY = Constraint.anything()
FIELDS = ("name", "detail", "heading", "power")


def texts(game: DatachGame) -> Iterator[CardText]:
    for entry in game.entries():
        card = game.build(GameOrder(entry.ident, (ANY, ANY, ANY)))
        if card is not None:
            yield game.describe(card)
    if game.strongest is not None:
        yield game.describe(game.strongest())


def pairs(game: DatachGame) -> Iterator[tuple[str, str]]:
    for entry in game.entries():
        yield entry.english, entry.japanese
    for text in texts(game):
        for field in FIELDS:
            yield getattr(text, field)


@pytest.mark.parametrize("device", list(GAMES), ids=str)
def test_no_english_line_carries_kana(device: Device) -> None:
    lines = [english for english, _ in pairs(GAMES[device])]

    mixed = [line for line in lines if JAPANESE.search(line)]

    assert mixed == []


@pytest.mark.parametrize("device", list(GAMES), ids=str)
def test_no_japanese_line_is_english_prose(device: Device) -> None:
    lines = list(pairs(GAMES[device]))

    untranslated = [
        japanese
        for english, japanese in lines
        if ENGLISH_WORD.search(english) and not JAPANESE.search(japanese)
    ]

    assert untranslated == []
