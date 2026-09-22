"""Every word printed on a card, in English and in Japanese.

A card is printed in both languages whatever language the page was used in, so
a child who reads either can use it, and the pictograms carry the meaning for a
child who reads neither.

Two kinds of text live here and they have different sources. The special
ability effects are the published wording: English from this project's reading
of barcodebattler.net/page05.htm, Japanese copied from the same page. Everything
else, the race and class names, the stat names and the captions, is this
project's own translation, written in the hiragana and katakana a young reader
learns first rather than in kanji.
"""

from dataclasses import dataclass
from typing import Final

from maeyomi.models.character_class import CharacterClass
from maeyomi.models.race import Race
from maeyomi.models.special_ability import UNDOCUMENTED, SpecialAbility


@dataclass(frozen=True, slots=True)
class Bilingual:
    """One piece of text in both languages a card is printed in."""

    english: str
    japanese: str


_RACES: Final[dict[Race, Bilingual]] = {
    Race.MECHANICAL: Bilingual("Robot", "ロボット"),
    Race.ANIMAL: Bilingual("Animal", "どうぶつ"),
    Race.AQUATIC: Bilingual("Sea creature", "うみの いきもの"),
    Race.BIRD: Bilingual("Bird", "とり"),
    Race.HUMAN: Bilingual("Human", "にんげん"),
    Race.SINGLE_USE_WEAPON: Bilingual("Weapon, one use", "ぶき (1かい)"),
    Race.WEAPON: Bilingual("Weapon", "ぶき"),
    Race.SINGLE_USE_ARMOUR: Bilingual("Armour, one use", "ぼうぐ (1かい)"),
    Race.ARMOUR: Bilingual("Armour", "ぼうぐ"),
    Race.SUPPORT_ITEM: Bilingual("Helper item", "おたすけ アイテム"),
}

_CLASSES: Final[dict[CharacterClass, Bilingual]] = {
    CharacterClass.WARRIOR: Bilingual("Warrior", "せんし"),
    CharacterClass.MAGICIAN: Bilingual("Magician", "まほうつかい"),
}

ITEM_CARD: Final = Bilingual("Item card", "アイテム カード")

STAT_LABELS: Final[dict[str, Bilingual]] = {
    "HP": Bilingual("HP", "たいりょく"),
    "ST": Bilingual("ST", "こうげき"),
    "DF": Bilingual("DF", "ぼうぎょ"),
}

RACE_DESCRIPTIONS: Final[dict[Race, str]] = {
    Race.MECHANICAL: "Machines. Gain attack when very healthy.",
    Race.ANIMAL: "Beasts. Gain defence when very healthy.",
    Race.AQUATIC: "Sea creatures. Gain both when very healthy.",
    Race.BIRD: "Fliers. No bonus, so every number is reachable.",
    Race.HUMAN: "People. No bonus, so every number is reachable.",
    Race.SINGLE_USE_WEAPON: "An attack boost that breaks after one battle.",
    Race.WEAPON: "An attack boost that lasts.",
    Race.SINGLE_USE_ARMOUR: "A defence boost that breaks after one battle.",
    Race.ARMOUR: "A defence boost that lasts.",
    Race.SUPPORT_ITEM: "Health, herbs or magic points.",
}

RACE_DESCRIPTIONS_JA: Final[dict[Race, str]] = {
    Race.MECHANICAL: "きかい。たいりょくが とても おおいと こうげきが ふえる。",
    Race.ANIMAL: "けもの。たいりょくが とても おおいと ぼうぎょが ふえる。",
    Race.AQUATIC: "うみの いきもの。たいりょくが とても おおいと りょうほう ふえる。",
    Race.BIRD: "そらを とぶ。ボーナスは ないので どの すうじでも つくれる。",
    Race.HUMAN: "ひと。ボーナスは ないので どの すうじでも つくれる。",
    Race.SINGLE_USE_WEAPON: "こうげきが ふえる。1かいの たたかいで こわれる。",
    Race.WEAPON: "こうげきが ずっと ふえる。",
    Race.SINGLE_USE_ARMOUR: "ぼうぎょが ふえる。1かいの たたかいで こわれる。",
    Race.ARMOUR: "ぼうぎょが ずっと ふえる。",
    Race.SUPPORT_ITEM: "たいりょく、やくそう、まほうの ポイント。",
}

"""What each kind of card does, for a player who has not read the manual."""


SPECIAL_POWER: Final = Bilingual("Special power", "とくしゅ のうりょく")
SWIPE: Final = Bilingual("Swipe this end", "ここを とおしてね")
NO_POWER: Final = Bilingual("No special power", "のうりょく なし")
UNKNOWN_POWER: Final = Bilingual("Unknown power", "なぞの のうりょく")

NO_ABILITY_CODE: Final = 0


def race_label(race: Race) -> Bilingual:
    """What kind of card this is."""
    return _RACES[race]


def class_label(character_class: CharacterClass | None) -> Bilingual:
    """How a fighter fights, or that the card is an item."""
    if character_class is None:
        return ITEM_CARD
    return _CLASSES[character_class]


def ability_text(special: SpecialAbility) -> Bilingual:
    """The special power in words, with the two placeholders put plainly.

    Every documented effect is printed as published, because a card that
    paraphrases the rules is a card that gets them wrong.
    """
    if special.code == NO_ABILITY_CODE:
        return NO_POWER
    if special.description == UNDOCUMENTED:
        return UNKNOWN_POWER
    return Bilingual(special.description, special.japanese)
