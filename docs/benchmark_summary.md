# Benchmark Summary

## What is a separation profile

The benchmark_lab compares each braid pair under three fixed branches:

`(sl2_fundamental, sl2_3d_9x9, sl3_fundamental)`

It records `same` as `0` and `different` as `1`.

So a profile like `(0,1,1)` means:

- the `sl2_fundamental` branch does not separate the pair,
- the `sl2_3d_9x9` branch does separate the pair,
- the `sl3_fundamental` branch does separate the pair.

## Current core benchmark pairs

- `P01 = 5_1 vs 5_1_stabilized`
- `P02 = 5_1 vs 10_22`
- `P03 = 10_22 vs 10_35`
- `P04 = 5_1 vs 10_132`
- `P05 = K11n34 vs K11n42` placeholder

## Why P03 matters

`P03` is the cleanest current positive benchmark pair in this repository. In the stored numeric runs for `q=2`, `q=3`, and `q=5`, the observed profile is `(0,1,1)`. This means the pair is not separated by the current Jones-compatible line, but it is separated by the current two 9x9-based lines.

This makes `P03` the main benchmark result for the current report-ready snapshot.

## Why P01 and P04 are not final conclusions

`P01` is a stabilization audit case. It is useful because it tells us whether the current branch conventions behave as expected on a control pair.

`P04` is a literature/convention reconciliation case. It is useful because it shows that some braid-side outputs still need careful interpretation before any stronger statement should be made.

These two pairs should therefore stay visible in the repository and in the report, but they should not be presented as final benchmark wins.

## Why P05 is skipped

`P05` is intentionally marked as a placeholder case with `needs_audit`. The benchmark_lab is designed to warn and skip such pairs instead of inventing a profile.

## Practical reading guide

If you want one result that best represents the current benchmark story, read `P03` first. If you want to understand the current limitations and open interpretation issues, read `P01` and `P04` next.# Benchmark Summary

## What Is A Separation Profile

The benchmark_lab uses a fixed three-branch comparison order:

`(sl2_fundamental, sl2_3d_9x9, sl3_fundamental)`

For each pair of braids or knot representatives:

- `same` is encoded as `0`
- `different` is encoded as `1`

So the profile `(0,1,1)` means that the first branch does not separate the pair, while the second and third branches do.

## Current Core Benchmark Pairs

- `P01 = 5_1 vs 5_1_stabilized`
- `P02 = 5_1 vs 10_22`
- `P03 = 10_22 vs 10_35`
- `P04 = 5_1 vs 10_132`
- `P05 = K11n34 vs K11n42` placeholder pair

## Why P03 Matters

`P03` is the current main benchmark pair because it repeatedly shows the same qualitative pattern in the stored experiments:

- `sl2_fundamental`: same
- `sl2_3d_9x9`: different
- `sl3_fundamental`: different
- observed profile: `(0,1,1)`

This makes `P03` a useful report example for branch comparison. It is stronger than a trivial all-different control, because one branch agrees while two others separate.

## Why P01 And P04 Are Not Final Conclusions

`P01` is a stabilization audit case. It is useful because it exposes whether the current branch implementation behaves consistently on a control pair that should be read with care.

`P04` is a literature or convention reconciliation case. It is useful because it highlights where interpretation still depends on braid choice, normalization, or comparison convention.

For that reason:

- `P01` should not be advertised as a final positive benchmark result.
- `P04` should not be advertised as a final positive benchmark result.
- mismatches between expected and observed profiles should remain visible in the exported files.

## Current Interpretation

At the present stage, the clean report-facing statement is:

- `P03` is the main benchmark result.
- `P01` and `P04` are audit cases.
- `P05` remains a skipped placeholder until a reliable braid source is supplied.