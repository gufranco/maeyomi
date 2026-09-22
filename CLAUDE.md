# Barcode Battler II card maker

Print-ready cards for a 1992 Epoch handheld. A barcode is the whole card: the
device reads thirteen digits and derives the kind, the three numbers and the
special power from them. Nothing on a card is decoration that the code does not
already imply.

## The rule that outranks every other rule here

**Never invent a formula.** Every arithmetic step in `decoder/` is a port of
`src/BarcodeRead.as` from the MIT-licensed `finalfighter/BarcodeBattler2-Simulator`,
cross-checked against `barcodebattler.net`. When a source is silent or two
sources disagree, the question goes in `decoder/uncertainties.py` with what each
source says and what was decided, and the generator refuses to produce codes
that reach the uncertain branch. A plausible guess that passes the tests is the
failure this project exists to avoid, because it produces cards that are wrong
on real hardware and correct everywhere else.

The two known divergences from the simulator are recorded at the top of
`decoder/front_read.py`. Do not quietly widen that list.

## What the output has to be

| Obligation | What it means here |
|---|---|
| Two languages, always | Every card carries English and Japanese together, whatever language the page is in. Not a toggle, not a variant: both on the same card |
| A child who cannot read must still understand | Every kind, every stat and every special power has a pictogram beside the words |
| Portrait, at the original size | 63.5 by 88.9 mm. No landscape variant. The size is not up for revisiting |
| The barcode is a measurement, not a picture | Vectors at the specified module width and full bar height. A shortened bar removes the reader's whole alignment tolerance |
| It survives a grey printer | Nothing is carried by colour alone. Every distinction has a second channel |
| It survives colour blindness | The palette is held to numbers in tests, under protanopia, deuteranopia and tritanopia. Never chosen by eye |
| It survives the print shop | Bleed, gutter, corner crop marks, a calibration ruler, a one-card-per-page shop file |
| It survives a screen reader | The page and the PDFs both. See the accessibility section below |
| Everything on the page exists in the CLI | A feature added to one is added to the other in the same change |

## Accessibility is a gate, not a pass

The page: axe-core reports zero violations on every tab, in both colour
schemes, against WCAG 2.2 A and AA plus best-practice. Keyboard alone reaches
everything. A change to markup, styles or the component tree is unverified
until a real browser has drawn it and the computed result was read back off the
focused element. The stylesheet is not evidence.

The PDFs: the document names itself so a reader speaks the card's name rather
than the filename, declares its language, and every word is real extractable
text. **The drawing order is the reading order**, because ReportLab emits no
tag tree, so drawing the barcode before the name makes every card open with
thirteen digits. `tests/rendering/test_reading_order.py` locks that in.

These are not PDF/UA files and the README says so. Do not let that sentence
drift into a compliance claim.

## Verification

- 100% coverage, statements and branches, enforced in CI. A new module arrives
  with its tests.
- A barcode claim is verified by rasterising the rendered page and decoding the
  symbol back out. A test on the digits proves nothing about what a scanner
  sees.
- A layout claim names the viewport it holds at.
- The device was tested with real hardware. Record what was actually observed;
  never invent a count to make the record look fuller.

## House style

- **English only**, in every file, commit, comment and reply, whatever language
  the conversation is in.
- **No comments in source.** The ban is absolute and covers test files. Only
  tool directives such as `# noqa` survive. When code needs explaining, rename
  something or extract a function.
- No em dashes, no emoji, no parentheses in prose, no ASCII diagrams.
- Nothing in any artifact may reveal how the work was produced: no phase
  numbers, no plan paths, no verification narration.
- `uv` for everything. `ruff` with `select = ["ALL"]`, `pyright` strict, both
  clean before a commit.
- Files under 500 lines, functions under 30, no magic numbers, immutable by
  default, explicit types at every boundary.

## Working style

- When a list of improvements is presented, the answer is all of them. Do not
  ask which subset.
- Run a plan to the end. Status between phases is welcome; asking permission to
  continue is not.
- A problem found while a change is open is fixed in that change, whoever
  introduced it and whenever. Never filed, never deferred.
- Ambiguity that would change the work is one question, asked once, with a
  recommendation attached.

## Data that is not ours

`products/japan.json` is a subset of Open Food Facts under ODbL, and the
official card barcodes come from collector wikis. Both are credited in
`NOTICE.md`. Every number on a card is read from the barcode by this project's
decoder and is never copied from either source, so a wrong name spoils a joke
and nothing else.
