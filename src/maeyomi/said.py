"""A message that says the same thing in English and in Japanese.

`Said` is the English text itself, so a terminal prints it and every test that
matches on English keeps working, and it carries its Japanese beside it for a
page shown in Japanese. A refusal raised with one keeps it through the raise.
"""

from collections.abc import Sequence
from typing import Final, Self

FIELDS: Final = {
    "hp": "たいりょく",
    "st": "こうげき",
    "df": "ぼうぎょ",
    "pp": "やくそう",
    "herbs": "やくそう",
    "mp": "まほう",
    "magic": "まほう",
    "speed": "スピード",
    "job": "しょくぎょう",
    "race": "しゅぞく",
    "class": "たたかいかた",
    "special": "のうりょく",
    "ability": "のうりょく",
    "back-read": "うしろから よむ",
    "level": "レベル",
    "character": "キャラクター",
}
"""Each field a refusal can name, as the page names it in Japanese."""


class Said(str):
    """English text that also knows how it reads in Japanese."""

    __slots__ = ("japanese",)
    japanese: str

    def __new__(cls, english: str, japanese: str) -> Self:
        """The English text, holding its Japanese."""
        said = super().__new__(cls, english)
        said.japanese = japanese
        return said


def said_of(error: BaseException) -> str:
    """The message an error was raised with, keeping any Japanese it carries."""
    first = error.args[0] if error.args else None
    return first if isinstance(first, str) else str(error)


def in_japanese(message: object) -> str | None:
    """A message's Japanese, or None when it was only written in English."""
    return message.japanese if isinstance(message, Said) else None


def field_in_japanese(field: str) -> str:
    """A field's Japanese name, or the field itself when the page has none for it."""
    return FIELDS.get(field, field)


def fields_in_japanese(fields: Sequence[str]) -> str:
    """Several fields named in Japanese, joined as a list."""
    return "・".join(field_in_japanese(field) for field in fields)


NO_MATCH: Final = Said(
    "no barcode satisfies every constraint at once",
    "ぜんぶの じょうけんを いっしょに みたす バーコードは ない",
)


def not_a_multiple(field: str, value: int, unit: int) -> Said:
    """A number the device cannot hold because it keeps only steps of `unit`."""
    return Said(
        f"{field} of {value} is not a multiple of {unit}",
        f"{field_in_japanese(field)} {value} は {unit} ずつに して",
    )


def above_ceiling(field: str, value: int, ceiling: int) -> Said:
    """A number above the most the device can hold."""
    return Said(
        f"{field} of {value} is above the ceiling of {ceiling}",
        f"{field_in_japanese(field)} {value} は さいだい {ceiling} より おおきい",
    )
