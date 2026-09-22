# Hardware validation

## Status

Printed cards have been read on a physical Barcode Battler II. The protocol
below is what a session works through, and each stage settles something the
other checks cannot reach.

| Claim | Evidence | Status |
|---|---|---|
| The decoder reproduces the published behaviour | 189 cards with published attributes, plus the six published attribute ceilings falling out of the arithmetic | done |
| A generated barcode decodes back to the request | Property tests over 1000 generated requests | done |
| The printed ink is a readable EAN symbol | Every sheet rasterised at 600 DPI and decoded | done |
| The device reads the printed card | Reported by the project owner; see `hardware-results.md` | done |

The stages below cover what a reading alone does not settle: which digit carries
speed, the two quarantined overflow branches, the twelve-digit case, and the
module width the scanner actually tolerates. Those remain open in
`src/barcode_battler/decoder/uncertainties.py` until a session records them.

## What a test session needs

- A Barcode Battler II.
- Sheets printed on matte white stock. Glossy stock reflects the scanner's
  light and is the first thing to rule out if a card will not read.
- A printer driven at 600 DPI or better with scaling turned off. A print dialog
  set to "fit to page" changes the module width, which is the whole point of
  drawing the symbol at a fixed one.
- A ruler or calipers, to confirm the printed module width before blaming the
  device.

## Before scanning anything

Measure one printed EAN-13 symbol edge to edge, including the blank margins the
generator leaves on each side. At the default geometry it must be 37.29 mm. A
different figure means the print pipeline scaled the page, and nothing measured
after that tells you anything about the device.

```bash
barcode-battler random --count 9 --seed 1 --output calibration.pdf
```

## The protocol

Work through the sheets in this order. Each stage answers a different question,
and a failure at one stage makes the later stages unreadable.

### 1. Does the device read our ink at all

Print a sheet at the default module width and scan every card. Record how many
read on the first swipe. A card that never reads is a geometry problem, not a
decoding problem.

### 2. Does it read what we say it reads

For each card that scanned, compare the attributes the device displays against
the attributes printed on the card. Any disagreement is a decoder defect and is
the most valuable result this protocol can produce.

### 3. Which digit carries speed

The device's initiative behaviour is the only thing that distinguishes digit 9
from digit 11. Generate two cards that are identical except for those digits and
observe which one goes first, repeatedly enough to see past the random element
in the hit calculation.

```bash
barcode-battler generate --hp 4000 --st 1200 --df 700 --race human --speed 9 --output fast.pdf
barcode-battler generate --hp 4000 --st 1200 --df 700 --race human --speed 0 --output slow.pdf
```

This settles `front_read_speed_digit`.

### 4. The two quarantined branches

The generator refuses to emit these, so the codes have to be entered by hand.
Both are front reads above 20000 HP with race 0 or race 1.

| Barcode | What this project's decoder says | What to record |
|---|---|---|
| `2099300045000` | HP 20900, ST 3800, DF 10000 | the ST the device shows |
| `2091093145004` | HP 20900, ST 11000, DF -14500 | the DF the device shows |

A device that shows ST 29300 on the first card means the overflow test is not
256 and `st_overflow_threshold` is resolved. A device that shows a DF unrelated
to ST on the second means `race_one_overflow_target` is a defect in the
reference simulator rather than hardware behaviour.

### 5. Twelve digit UPC-A

Print a 12-digit code and try it. This project rejects those, following the
reference simulator, while that simulator's own card list contains two of them.
Whichever way the device behaves, `upc_a_twelve_digits` is then resolved.

### 6. The module width floor

Repeat stage 1 at 0.264 mm, the smallest width the EAN specification permits,
then at 0.33 mm and 0.45 mm. Record the first-swipe read rate at each. The
result is the real floor for this device, which is the number the geometry
default should be set from.

```bash
barcode-battler random --count 9 --seed 1 --output narrow.pdf
```

## Recording a result

Add a row to `docs/hardware-results.md` for every session, including the ones
where everything worked. A protocol with only failures recorded cannot tell a
fixed defect from an untested one.

Any finding that contradicts `uncertainties.py` updates that file in the same
change, along with the test that pins the behaviour.
