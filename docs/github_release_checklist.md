# GitHub Release Checklist

- Confirm that no private or personal data is included in the repository snapshot.
- Confirm that no absolute local paths remain in user-facing docs or release notes.
- Confirm whether `artifacts/` should be cleaned or whether the current benchmark_lab result folders should be included on purpose.
- Confirm that `README.md` matches the current benchmark_lab status and current report wording.
- Confirm that `docs/report_appendix.md` placeholders for repository URL, commit hash, and release tag are filled.
- Confirm that the benchmark template in `data/benchmark_lab/benchmark_pairs_template.csv` is the intended release template.
- Run `python tools/create_report_bundle.py` and inspect the generated `report_bundle/` and `report_bundle.zip`.
- If git is being used, create the release tag after the final snapshot is checked.
- Upload the zip snapshot with the release if a bundled report appendix package is desired.# GitHub Release Checklist

- Confirm that the repository does not contain private data or personal files that should not be published.
- Confirm that no document or script still contains absolute local paths that should be removed before release.
- Confirm that generated `artifacts/` files are either intentionally included in the snapshot bundle or cleaned before a public release.
- Confirm that `README.md` reflects the current benchmark status and does not overclaim mathematical conclusions.
- Confirm that `docs/report_appendix.md` placeholders for GitHub URL, commit hash, and release tag are filled before submission.
- Confirm that the benchmark_lab commands in `docs/reproducibility.md` still run from the repository root.
- If a git repository is initialized, create and record the release tag.
- If desired, run `python tools/create_report_bundle.py` and upload `report_bundle.zip` as a release asset or report attachment.