# Braid Preview Status

## Current drawing rules

The ordinary braid preview now treats the lane positions as fixed braid lanes. The renderer keeps a current_order list, initialized as [1, 2, ..., n], and for each generator only swaps the two adjacent lane occupants involved in that step.

Each generator row is drawn explicitly instead of relying on one broad smooth interpolation across the whole picture:

- Unchanged strands stay in their current lanes for that row.
- The over strand is drawn as one continuous sampled curve.
- The under strand is drawn as two sampled curve segments with a deliberate center gap.
- The bottom labels show the final lane ordering after all swaps.
- The header now includes the final permutation so the visual output can be checked against the combinatorics.

## Over/under convention

The renderer follows the standard Artin-generator convention on adjacent lanes i and i+1:

- sigma_i: the strand currently in lane i crosses over the strand currently in lane i+1.
- sigma_i^-1: the strand currently in lane i+1 crosses over the strand currently in lane i.

This is implemented by keeping lane_x fixed, swapping only current_order after each generator, and choosing the over/under sampled curves according to the generator sign.

## Active preview synchronization

The ordinary GUI now keeps the preview synchronized not only after evaluation, but also during pending input states:

- Switching the catalog example updates the pending preview immediately.
- Editing the custom braid updates the pending preview whenever the current text parses successfully.
- Load into custom now updates the custom editor and the pending preview together.
- Cards and report output remain marked as not yet evaluated until Evaluate example or Apply custom braid is pressed.

## Validated examples

The current regression coverage includes:

- identity on 1 and 3 strands
- [1]
- [2]
- [1, 2]
- [1, 2, 1]
- [2, 1, 2]
- [1, -1]
- [1, 1, 1]
- [-1, 2, -1, 2]
- long 5- and 6-strand smoke examples

The automated checks currently verify:

- endpoint counts
- over/under segment counts
- under-strand center gap existence
- final permutation for key relations such as [1, 2, 1] ~ [2, 1, 2]
- ordinary GUI pending-preview synchronization for catalog and load-into-custom flows

## Manual debug export

Use the debug exporter to write SVG previews for the standard inspection set:

```powershell
C:/Users/dongqiyu/anaconda3/python.exe examples/debug_braid_preview.py
```

By default it writes SVG files to artifacts/braid_preview_debug/ and prints the strand count, generators, and final permutation for each case.

## Known limitations

The preview is still a diagrammatic debugging aid, not a theorem prover.

- It does not try to detect isotopy-equivalent layouts beyond the generator-by-generator combinatorics.
- Very long braid words will become vertically tall rather than folding into a compact layout.
- The renderer validates final lane order, not full planar isotopy simplification.
