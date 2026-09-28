"""Every piece of text a card this program makes can print, and the page shows.

The Chinese catalogues are written against this set and a test holds them to
it. It gathers the fixed labels, the face of every official card, every
device's cheat card, the names in every game's own list, and the faces of a
fixed spread of barcodes on every device, which reaches each decoder's kinds,
abilities and effects.
"""

import random
from typing import Final, cast

from maeyomi.datach.games import GAMES
from maeyomi.decoder.check_digit import expected_check_digit
from maeyomi.models.device import Device
from maeyomi.official.catalogue import official_cards
from maeyomi.registry import cheat_as, readable_as
from maeyomi.rendering import labels
from maeyomi.rendering.face import CardFace, face_of
from maeyomi.rendering.labels import Bilingual

SEED: Final = 1992
CODES_PER_DEVICE: Final = 2000
BODY_DIGITS: Final = 12


def printed_texts() -> frozenset[Bilingual]:
    """The fixed labels and the words on every card face in the sample."""
    faces = [*_official_faces(), *_cheat_faces(), *_sampled_faces()]
    return frozenset(
        {
            *_fixed_labels(),
            *_race_descriptions(),
            *_game_names(),
            *(text for face in faces for text in _texts_of(face)),
        }
    )


def _race_descriptions() -> list[Bilingual]:
    """What each kind of card does, as the page's card maker explains it."""
    return [
        Bilingual(labels.RACE_DESCRIPTIONS[race], labels.RACE_DESCRIPTIONS_JA[race])
        for race in labels.RACE_DESCRIPTIONS
    ]


def _fixed_labels() -> list[Bilingual]:
    """Every label the label module declares, alone or in a table."""
    found: list[Bilingual] = []
    for value in vars(labels).values():
        if isinstance(value, Bilingual):
            found.append(value)
        elif isinstance(value, dict):
            table = cast("dict[object, object]", value)
            found.extend(item for item in table.values() if isinstance(item, Bilingual))
    return found


def _game_names() -> list[Bilingual]:
    """Every card name a game's own list gives."""
    return [
        Bilingual(entry.english, entry.japanese)
        for game in GAMES.values()
        for entry in game.entries()
    ]


def _official_faces() -> list[CardFace]:
    """The face of every official card that prints."""
    return [face_of(card.character) for card in official_cards()]


def _cheat_faces() -> list[CardFace]:
    """The face of every device's cheat card, where the device has one."""
    faces: list[CardFace] = []
    for device in Device:
        try:
            faces.append(face_of(cheat_as(device, None).character))
        except ValueError:
            continue
    return faces


def _sampled_faces() -> list[CardFace]:
    """The faces of a fixed spread of barcodes on every device."""
    rng = random.Random(SEED)  # noqa: S311
    faces: list[CardFace] = []
    for device in Device:
        for _ in range(CODES_PER_DEVICE):
            body = "".join(str(rng.randrange(10)) for _ in range(BODY_DIGITS))
            result = readable_as(device, body + str(expected_check_digit(body)))
            if result is not None:
                faces.append(face_of(result))
    return faces


def _texts_of(face: CardFace) -> list[Bilingual]:
    """The words a face carries."""
    heading = [] if face.power_heading is None else [face.power_heading]
    return [face.kind, face.detail, face.power_text, *heading]
