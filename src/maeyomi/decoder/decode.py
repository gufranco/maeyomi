"""The public entry point: one barcode in, one decoded character out.

Validation runs first, then read-type discrimination, then the matching reader.
The whole chain is deterministic: abilities 30, 31 and 32 make an item's sign a
runtime coin flip on the device, and that is reported as `sign_is_volatile`
rather than resolved here.

The barcodes on Epoch's own boxes are the exception. barcodebattler.co.uk,
Barcode Battler II technical info, lists the device reading the Barcode Battler
and Barcode Battler II boxes as fixed heroes, each the same as an ordinary code
it gives, so those two are read as that code. It lists three more boxes, the
dedicated card software, as still needing testing, so those are refused.
"""

import dataclasses
from typing import Final

from maeyomi.decoder.back_read import read_back
from maeyomi.decoder.errors import UnsupportedBarcodeError
from maeyomi.decoder.front_read import read_front
from maeyomi.decoder.read_type import classify_read_type
from maeyomi.decoder.validation import validate_barcode
from maeyomi.models.character import BarcodeBattlerCharacter
from maeyomi.models.read_type import ReadType
from maeyomi.said import Said

BOX_EQUIVALENTS: Final[dict[str, str]] = {
    "4905040352507": "0521501106508",
    "4905040352521": "0521501187507",
}
UNRECORDED_BOXES: Final = frozenset({"4905040352606", "4905040352705", "4905040352804"})
UNRECORDED_BOX_REASON: Final = Said(
    "an Epoch box whose reading nobody has recorded",
    "だれも よみかたを きろくして いない エポックしゃの はこ",
)


def decode(code: str) -> BarcodeBattlerCharacter:
    """Decode a barcode, raising a typed error when the device would reject it."""
    normalised = validate_barcode(code)
    if normalised in UNRECORDED_BOXES:
        raise UnsupportedBarcodeError(normalised, UNRECORDED_BOX_REASON)
    equivalent = BOX_EQUIVALENTS.get(normalised)
    if equivalent is not None:
        return dataclasses.replace(_read(equivalent), barcode=normalised)
    return _read(normalised)


def _read(code: str) -> BarcodeBattlerCharacter:
    """Read an ordinary code the way its read type calls for."""
    if classify_read_type(code) is ReadType.FRONT:
        return read_front(code)
    return read_back(code)
