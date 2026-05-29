# Archive directory

Historical or superseded artifacts may be moved here when they are **not** referenced by
tests, scripts, documentation, or the paper package, and when a newer frozen output
supersedes them.

**Release policy (controlled expansion-20):** Frozen `outputs/tables/expansion*` and
`controlled_expansion_*` CSVs were not moved. LaTeX build debris is deleted (not archived)
because `python3 scripts/compile_paper_pdf.py` regenerates it.

## Archived in Zenodo prep (unreferenced scaffold / duplicate)

| Original path | Reason |
| --- | --- |
| `outputs/figures/Galaxy_A_rotation.png` | Phase 0 mock scaffold figure |
| `outputs/figures/Galaxy_A_tau.png` | Phase 0 mock scaffold figure |
| `outputs/figures/Galaxy_B_rotation.png` | Phase 0 mock scaffold figure |
| `outputs/figures/Galaxy_B_tau.png` | Phase 0 mock scaffold figure |
| `docs/TDF_Radial_Reconstruction_on_a_Preregistered_Controlled_SPARC_Subset.pdf` | Duplicate of `paper/manuscript.pdf` |

To archive a file safely:

1. Confirm zero references via `outputs/tables/repository_cleanup_candidates.csv`.
2. Move the file under `archive/` preserving relative path (e.g. `archive/outputs/reports/...`).
3. Re-run `python3 scripts/build_repository_cleanup_audit.py --apply-cleanup`.
