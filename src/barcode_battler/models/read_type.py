"""Whether a barcode is read from the front or from the back.

Source: barcodebattler.net/page02.htm, and `prepost_check` in
`src/BarcodeRead.as` of finalfighter/BarcodeBattler2-Simulator (MIT).
"""

from enum import Enum


class ReadType(Enum):
    """The reading mode the device selects for a barcode."""

    FRONT = "front"
    BACK = "back"
