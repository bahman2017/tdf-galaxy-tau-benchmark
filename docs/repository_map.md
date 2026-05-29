# Repository map

High-level layout for external readers and Zenodo depositors.

## `configs/`

YAML configuration for:

- `sparc_subset.yaml` — initial six-galaxy controlled subset
- `subset_expansion.yaml` — expansion-12 / expansion-20 cohort protocol
- `models.yaml`, `reconstruction.yaml` — TDF knot models, NFW, MOND, fitting bounds
- `ml_priors.yaml` — optional M/L prior experiments (documented; not primary headline)

## `data/`

| Path | Contents |
| --- | --- |
| `data/raw/sparc/Rotmod_LTG/` | Per-galaxy SPARC `*_rotmod.dat` files |
| `data/raw/sparc/README.md` | Raw data provenance |
| `data/processed/sparc/` | `sparc_rotmod_standardized.csv`, `sparc_photometry_metadata.csv` |

Pipelines read processed CSVs; ingestion scripts rebuild them from raw Rotmod.

## `src/tdf_galaxy_tau/`

| Package | Role |
| --- | --- |
| `data/` | SPARC loaders, subset selection, expansion planning |
| `models/` | NFW, Burkert, MOND, TDF knot models, fitting |
| `reconstruction/` | Radial τ reconstruction, smoothing, regularization |
| `validation/` | Holdout validation, failure modes, robustness |
| `analysis/` | Audits, paper tables/figures, manuscript text, cleanup audit |
| `plotting/` | Rotation curves, τ profiles, diagnostics |
| `scripts/` | Shared pipeline helpers (`expansion_pipeline.py`, etc.) |

## `scripts/`

CLI wrappers (run from repository root). Headline chain for the paper:

1. `ingest_sparc_rotmod.py` — raw → processed rotmod
2. `plan_sparc_subset_expansion.py` — cohort plan CSV
3. `run_expansion20_pipeline.py` — expansion-20 fits + holdout tables
4. `analyze_expansion20_failure_modes.py` — failure diagnostics
5. `build_controlled_expansion_final_audit.py` — C20 claims + comparison summary
6. `export_paper_tables.py` / `build_paper_figures.py` / `compile_paper_pdf.py` — paper package

See [`reproducibility_commands.md`](reproducibility_commands.md) for exact invocations.

## `outputs/`

| Path | Role |
| --- | --- |
| `outputs/tables/` | Frozen CSV metrics (expansion12/20, controlled expansion, SPARC phase tables) |
| `outputs/reports/` | Markdown audit reports per phase |
| `outputs/figures/sparc_subset/` | PNG diagnostics used by paper figure composition |

**Do not treat** edits under `expansion20_*` or `controlled_expansion_*` as cosmetic — tests and the manuscript depend on them.

## `paper/`

| Path | Role |
| --- | --- |
| `manuscript.tex` / `manuscript.pdf` | Article source and compiled PDF |
| `references.bib` | Bibliography |
| `figures/` | Publication PNGs (fig1–fig7) |
| `tables/` | LaTeX tables exported from frozen benchmark CSVs |

## `docs/`

Methodology, assumptions, limitations, phase results, claim boundaries, reviewer objection
matrix (`reviewer_objection_matrix.md`), and pre-submission checklist.

## `tests/`

Pytest coverage for ingestion, models, holdout validation, expansion pipelines, paper
exports, and claim-boundary guards.

## `archive/`

Optional storage for superseded artifacts that are **unreferenced** (see
[`repository_cleanup_plan.md`](repository_cleanup_plan.md)). Empty by policy unless a
future audit moves files here.
