"""The English form of a name a game shows in kana, romanised by rule.

Hiragana is read as the katakana it matches. A run of kana becomes one
capitalised word, a long mark lengthens the vowel before it, and a long mark
that follows a letter or a digit is the hyphen the game drew with it. Spaces
and middle dots separate words; letters and digits are kept as they are.
"""

from typing import Final

SYLLABLES: Final = {
    **dict(zip("アイウエオ", ("a", "i", "u", "e", "o"), strict=True)),
    **dict(zip("カキクケコ", ("ka", "ki", "ku", "ke", "ko"), strict=True)),
    **dict(zip("ガギグゲゴ", ("ga", "gi", "gu", "ge", "go"), strict=True)),
    **dict(zip("サシスセソ", ("sa", "shi", "su", "se", "so"), strict=True)),
    **dict(zip("ザジズゼゾ", ("za", "ji", "zu", "ze", "zo"), strict=True)),
    **dict(zip("タチツテト", ("ta", "chi", "tsu", "te", "to"), strict=True)),
    **dict(zip("ダヂヅデド", ("da", "ji", "zu", "de", "do"), strict=True)),
    **dict(zip("ナニヌネノ", ("na", "ni", "nu", "ne", "no"), strict=True)),
    **dict(zip("ハヒフヘホ", ("ha", "hi", "fu", "he", "ho"), strict=True)),
    **dict(zip("バビブベボ", ("ba", "bi", "bu", "be", "bo"), strict=True)),
    **dict(zip("パピプペポ", ("pa", "pi", "pu", "pe", "po"), strict=True)),
    **dict(zip("マミムメモ", ("ma", "mi", "mu", "me", "mo"), strict=True)),
    **dict(zip("ヤユヨ", ("ya", "yu", "yo"), strict=True)),
    **dict(zip("ラリルレロ", ("ra", "ri", "ru", "re", "ro"), strict=True)),
    **dict(zip("ワヰヱヲン", ("wa", "i", "e", "o", "n"), strict=True)),
    **dict(zip("ヴヵヶヮ", ("vu", "ka", "ke", "wa"), strict=True)),
    **dict(zip("ヷヸヹヺ", ("va", "vi", "ve", "vo"), strict=True)),
}
SMALL_Y: Final = {"ャ": "a", "ュ": "u", "ョ": "o"}
SMALL_VOWELS: Final = {"ァ": "a", "ィ": "i", "ゥ": "u", "ェ": "e", "ォ": "o"}
Y_KEEPS: Final = ("sh", "ch", "j")
STEMS: Final = {"shi": "sh", "chi": "ch", "tsu": "ts", "fu": "f", "u": "w", "ji": "j", "vu": "v"}
LONG: Final = "ー"
HYPHEN: Final = "-"
DOUBLE: Final = "ッ"
VOWELS: Final = "aeiou"
FIRST_HIRAGANA: Final = "ぁ"
LAST_HIRAGANA: Final = "ゖ"
HIRAGANA_TO_KATAKANA: Final = ord("ァ") - ord("ぁ")
FIRST_KATAKANA: Final = "ァ"
LAST_KATAKANA: Final = "ヺ"
GAPS: Final = frozenset(
    " \u3000\u30fb\u3099\u309a\u309b\u309c\u309d\u309e\u309f\u30a0\u30fd\u30fe\u30ff"
)
KANA: Final = "kana"
GAP: Final = "gap"
OTHER: Final = "other"


def romanised(name: str) -> str:
    """The name in Latin letters, one word per run of kana."""
    runs: list[tuple[str, str]] = []
    for character in _as_katakana(name):
        kind = _kind(character, runs[-1][0] if runs else GAP)
        shown = HYPHEN if character == LONG and kind == OTHER else character
        if runs and runs[-1][0] == kind:
            runs = [*runs[:-1], (kind, runs[-1][1] + shown)]
        else:
            runs = [*runs, (kind, shown)]
    words = [_word(text) if kind == KANA else text for kind, text in runs if kind != GAP]
    return " ".join(word for word in words if word)


def _as_katakana(name: str) -> str:
    """The name with every hiragana letter turned into its katakana."""
    return "".join(
        chr(ord(character) + HIRAGANA_TO_KATAKANA)
        if FIRST_HIRAGANA <= character <= LAST_HIRAGANA
        else character
        for character in name
    )


def _kind(character: str, previous: str) -> str:
    """Whether a character is kana, a word break, or kept as it is."""
    if character in GAPS:
        return GAP
    if FIRST_KATAKANA <= character <= LAST_KATAKANA:
        return KANA
    if character == LONG:
        return OTHER if previous == OTHER else KANA
    return OTHER


def _word(kana: str) -> str:
    text = ""
    doubled = False
    for character in kana:
        text, doubled = _with(text, character, doubled=doubled)
    return text[:1].upper() + text[1:]


def _with(text: str, character: str, *, doubled: bool) -> tuple[str, bool]:
    if character == DOUBLE:
        return text, True
    if character == LONG:
        vowel = next((letter for letter in reversed(text) if letter in VOWELS), "")
        return text + vowel, False
    if character in SMALL_Y:
        return _small_y(text, SMALL_Y[character]), False
    if character in SMALL_VOWELS:
        return _small_vowel(text, SMALL_VOWELS[character]), False
    syllable = SYLLABLES.get(character, "")
    if doubled:
        syllable = ("t" if syllable.startswith("ch") else syllable[:1]) + syllable
    return text + syllable, False


def _small_y(text: str, vowel: str) -> str:
    stem = text[:-1]
    if stem.endswith(Y_KEEPS):
        return stem + vowel
    return stem + "y" + vowel


def _small_vowel(text: str, vowel: str) -> str:
    for syllable, stem in sorted(STEMS.items(), key=lambda pair: -len(pair[0])):
        if text.endswith(syllable):
            return text[: -len(syllable)] + stem + vowel
    if text and text[-1] in VOWELS:
        return text[:-1] + vowel
    return text + vowel
