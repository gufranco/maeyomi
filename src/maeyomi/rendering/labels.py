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

from maeyomi.models.character import BarcodeBattlerCharacter
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
UNKNOWN_KIND: Final = Bilingual("Enemy, kind unknown", "てき・しゅるい ふめい")
DBZ_FIGHTER: Final = Bilingual("Fighter", "せんし")
DBZ_MOVES: Final = Bilingual("Special moves", "ひっさつわざ")
UNREADABLE: Final = Bilingual(
    "The game's reader cannot read this barcode", "ゲームの リーダーでは よめない バーコード"
)
UNREADABLE_KIND: Final = Bilingual("Cannot be read", "よめない")
SPEED_DEPENDENT: Final = Bilingual(
    "Reads only at some swipe speeds", "とおす はやさに よっては よめない"
)
DBZ_EFFECT: Final = Bilingual("Effect", "こうか")
UNKNOWN_FIGHTER: Final = Bilingual("Fighter, kind unknown", "キャラクター・しゅるい ふめい")
PRIEST: Final = Bilingual("Priest", "そうりょ")
HOLY_WARRIOR: Final = Bilingual("Holy warrior", "せいせんし")
DOUBLE_PRIEST_JOB: Final = 4
DOUBLE_HOLY_WARRIOR_JOB: Final = 6
DOUBLE_LOWEST_MAGICIAN_JOB: Final = 7

STAT_LABELS: Final[dict[str, Bilingual]] = {
    "HP": Bilingual("HP", "たいりょく"),
    "ST": Bilingual("ST", "こうげき"),
    "DF": Bilingual("DF", "ぼうぎょ"),
    "PP": Bilingual("Herbs", "やくそう"),
    "MP": Bilingual("Magic", "まほう"),
    "BP": Bilingual("BP", "せんとうりょく"),
    "DP": Bilingual("DP", "ぼうぎょりょく"),
    "PW": Bilingual("PW", "PW"),
    "UST": Bilingual("ST", "ST"),
    "USP": Bilingual("SP", "SP"),
    "GHP": Bilingual("HP", "HP"),
    "AP": Bilingual("AP", "AP"),
    "GDP": Bilingual("DP", "DP"),
    "CP": Bilingual("CP", "CP"),
    "YHP": Bilingual("HP", "HP"),
    "YSP": Bilingual("SP", "SP"),
    "WHP": Bilingual("HP", "たいりょく"),
    "WST": Bilingual("ST", "こうげきりょく"),
    "WDF": Bilingual("DF", "しゅびりょく"),
    "WMP": Bilingual("MP", "まほうの かず"),
    "WPP": Bilingual("PP", "やくそうの かず"),
    "BMP": Bilingual("MP", "MP"),
    "KPW": Bilingual("Power, PS", "パワー PS"),
    "KWT": Bilingual("Weight, kg", "おもさ kg"),
    "FHR": Bilingual("Home runs", "本塁打"),
    "FSP": Bilingual("Speed", "走力"),
    "FKM": Bilingual("Pitch speed, km/h", "球速 km/h"),
    "FST": Bilingual("Stamina", "スタミナ"),
    "HSP": Bilingual("Speed", "スピード"),
    "HST": Bilingual("Stamina", "スタミナ"),
    "HGT": Bilingual("Guts", "ガッツ"),
    "HJP": Bilingual("Jump", "ジャンプ"),
    "HTB": Bilingual("Turbo", "ターボ"),
    "HTP": Bilingual("Type", "タイプ"),
    "DPW": Bilingual("Power", "ちから"),
    "DSM": Bilingual("Smarts", "あたま"),
    "DTG": Bilingual("Toughness", "じょうぶ"),
    "DSD": Bilingual("Speed", "はやさ"),
    "DHP": Bilingual("HP", "HP"),
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


def double_class_label(job: int) -> Bilingual:
    """How a Double fighter fights: the Double adds a priest and a holy warrior."""
    if job == DOUBLE_PRIEST_JOB:
        return PRIEST
    if job == DOUBLE_HOLY_WARRIOR_JOB:
        return HOLY_WARRIOR
    if job >= DOUBLE_LOWEST_MAGICIAN_JOB:
        return _CLASSES[CharacterClass.MAGICIAN]
    return _CLASSES[CharacterClass.WARRIOR]


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


def panel_text(character: BarcodeBattlerCharacter) -> Bilingual:
    """The ability panel's words, led by any strength the display hides.

    The hidden value goes first so a narrow panel trims the ability text rather
    than the one number the printed stat tiles cannot show.
    """
    text = ability_text(character.special)
    notes = _battle_notes(character)
    if not notes:
        return text
    english = "; ".join(note.english for note in [*notes, text])
    japanese = " ".join(note.japanese for note in [*notes, text])
    return Bilingual(english, japanese)


def _battle_notes(character: BarcodeBattlerCharacter) -> list[Bilingual]:
    """One sentence per stat a fight uses at a value the display does not show."""
    notes: list[Bilingual] = []
    if character.battle_st is not None:
        notes.append(
            Bilingual(
                f"Fights with ST {character.battle_st}",
                f"たたかうと こうげき {character.battle_st}。",
            )
        )
    if character.battle_df is not None:
        notes.append(
            Bilingual(
                f"Fights with DF {character.battle_df}",
                f"たたかうと ぼうぎょ {character.battle_df}。",
            )
        )
    return notes


def dbz_level_text(level: int | None) -> Bilingual:
    """A Datach Dragon Ball Z fighter's special move level, from 0, or that it shows none."""
    if level is None:
        return Bilingual("No special move level", "ひっさつわざ レベル なし")
    return Bilingual(f"Special move level {level}", f"ひっさつわざ レベル{level}")
