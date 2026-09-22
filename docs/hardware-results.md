# Hardware results

Sessions run against a physical Barcode Battler II, following
[`hardware-validation.md`](hardware-validation.md).

## Sessions

| Date | Device | Stage | Cards | First-swipe reads | Finding |
|---|---|---|---|---|---|
| 2026-09-22 | Barcode Battler II | 1, does the device read our ink | not recorded | not recorded | The device reads cards printed by this project. Reported by the project owner; the counts and the later stages were not recorded. |

## Open questions this file would close

Each of these is recorded in `src/barcode_battler/decoder/uncertainties.py` with
the evidence behind the choice this project made.

| Key | Question | Current answer |
|---|---|---|
| `front_read_speed_digit` | Which digit carries speed on a front read | index 9, from 100 published cards against the reference simulator's index 11 |
| `st_overflow_threshold` | Why the strength overflow test is 256 when the published ceiling is 199 | ported verbatim, never generated |
| `race_one_overflow_target` | Whether the defence correction reads from strength | ported verbatim, never generated |
| `upc_a_twelve_digits` | Whether a 12-digit code is left-padded | rejected, following the reference simulator |
| `shifted_back_read` | The shift semantics of a misaligned read | not implemented |
