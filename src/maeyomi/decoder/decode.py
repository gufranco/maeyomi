"""The public entry point: one barcode in, one decoded character out.

Validation runs first, then read-type discrimination, then the matching reader.
The whole chain is deterministic: abilities 30, 31 and 32 make an item's sign a
runtime coin flip on the device, and that is reported as `sign_is_volatile`
rather than resolved here.
"""

from maeyomi.decoder.back_read import read_back
from maeyomi.decoder.front_read import read_front
from maeyomi.decoder.read_type import classify_read_type
from maeyomi.decoder.validation import validate_barcode
from maeyomi.models.character import BarcodeBattlerCharacter
from maeyomi.models.read_type import ReadType


def decode(code: str) -> BarcodeBattlerCharacter:
    """Decode a barcode, raising a typed error when the device would reject it."""
    normalised = validate_barcode(code)
    if classify_read_type(normalised) is ReadType.FRONT:
        return read_front(normalised)
    return read_back(normalised)
