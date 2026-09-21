# JSON Braid Input Schema

## Purpose

This document fixes the ordinary braid workbench JSON schema used by the JSON input tab. The goal is strict batch import for AI or program-generated braid data while keeping the downstream comparison and export flow identical to manual input.

## Fixed schema

```json
{
  "q_parameter": "q",
  "models": [
    "sl2_fundamental",
    "sl2_3d_9x9",
    "sl3_fundamental"
  ],
  "comparison_mode": "pairwise",
  "braids": [
    {
      "label": "A",
      "num_strands": 3,
      "generators": [1, 2, 1],
      "notes": "optional"
    },
    {
      "label": "B",
      "num_strands": 3,
      "generators": [2, 1, 2],
      "notes": "optional"
    }
  ]
}
```

## Field rules

### q_parameter

Allowed forms:

- q
- numeric strings such as 2 or 3
- numeric JSON values such as 2 or 3

Meaning:

- q means symbolic mode and is slower
- numeric values mean faster numeric screening

### models

Allowed values only:

- sl2_fundamental
- sl2_3d_9x9
- sl3_fundamental

Current meanings:

- sl2_fundamental -> Jones / sl2 fundamental -> formal Jones-compatible branch
- sl2_3d_9x9 -> sl2 的3维表示下的9x9矩阵 -> colored Jones candidate branch; compare against Knot Atlas n=2 because Knot Atlas uses J_n for the (n+1)-dimensional sl2 representation; current trefoil calibration is q^6 J_2(3_1; q^2); 5_2 is still under verification
- sl3_fundamental -> sl3 fundamental -> formal sl3 branch

### comparison_mode

Allowed values only:

- single
- pairwise
- all

Meaning:

- single: compute each braid independently and do not compare braids against each other
- pairwise: compare every unordered pair
- all: return the single-braid table, the pairwise table, and the summary table together

### braids

Each braid object must include:

- label
- num_strands
- generators

Optional:

- notes

### num_strands

Must be an integer and must be at least 2.

### generators

Must be an integer array. If num_strands = n, then only ±1 through ±(n-1) are allowed.

Examples:

- 1 means σ1
- -1 means σ1^-1
- 2 means σ2
- -2 means σ2^-1

## Validation behavior

Validation is strict and explicit.

If the JSON is invalid, the workbench reports a clear error instead of silently falling back or partially loading the batch.

Typical errors include:

- invalid JSON syntax
- invalid comparison_mode
- unknown model id
- missing required braid field
- generator out of range for the declared num_strands

## Equality of downstream behavior

This schema only changes the input frontend. After validation, JSON input is normalized into the same internal workbench spec used by manual input, so both modes share:

- the same evaluation runner
- the same pairwise comparison path
- the same result tables
- the same experiment log format
- the same CSV / JSON / markdown exports
