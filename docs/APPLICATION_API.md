# Application Service API

`src.services` is the explicit, frontend-neutral application API. Frontends
should import only names listed in `src.services.__all__`, rather than reaching
into mathematical evaluator modules or GUI adapters.

The supported surface covers:

- `list_evaluation_branches`, `get_evaluation_model`, and
  `get_evaluation_branch` for the current model catalog;
- parsing generator text and building validated catalog or custom braid input;
- evaluating a catalog example, arbitrary `BraidWord`, or `BraidInputState`;
- immutable application result DTOs, deterministic JSON serialization, and
  frontend-neutral text reports;
- structured `ApplicationServiceError` subclasses for input, unknown catalog,
  unknown branch, and unknown model failures.

The catalog is the sole frontend-neutral source for current mapping and status
facts. It records `sl2_fundamental` and `sl3_fundamental` as formal, and maps
the workbench model `sl2_3d_9x9` to internal branch `sl2_spin1`, which remains
candidate. Its notes describe existing program behavior only; they do not add
external mathematical claims or change conventions in
`docs/MATH_CONVENTIONS.md`.

Tkinter-specific colors, controls, and layouts remain in `src.gui`. Existing
GUI helper functions remain compatibility adapters over this API. Mathematical
builders, R-matrix construction, and normalization details are intentionally
not part of the application API.

The maintained `demo_launcher`, `braid_workbench_app`, and workbench runner use
the DTO/reporting surface rather than importing invariant result or formatter
implementations. The recovered `demo_launcher_legacy` remains a historical
compatibility entrypoint and intentionally retains its original internal
formatter dependencies; it is not the maintained frontend path.
