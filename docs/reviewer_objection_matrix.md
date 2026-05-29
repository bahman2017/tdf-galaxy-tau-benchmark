# Reviewer Objection Matrix (Phase 5F-E)

Honest responses for a controlled expansion_20 benchmark. This matrix does not expand claims beyond C20-A--C20-H.

| ID | Objection | Honest answer | Mitigation already done | Future work |
| --- | --- | --- | --- | --- |
| R01 | Why only 20 galaxies? | Full SPARC has 175 systems; we report a pre-registered controlled cohort, not a census. | Phase 5A frozen expansion plan; claims C20-A/E. | Full-catalog protocol amendment before scaling language. |
| R02 | Why not full SPARC? | Resource and claim-scope control; subset allows audited failure taxonomy. | Explicit “not full-SPARC validation” in abstract and limitations. | expansion beyond 20 only with new preregistration. |
| R03 | Why fixed baryons? | To isolate rotation-curve model comparison from M/L degeneracy. | Fixed SPARC rotmod decomposition; documented in assumptions. | Photometry-calibrated M/L priors (diagnostic grids exist in repo). |
| R04 | Why no M/L fitting? | M/L fitting would confound holdout comparison across models. | No M/L fit in primary gate; diagnostic M/L phases 4F–4G separate. | Fair M/L calibration study with new claim matrix. |
| R05 | Is tdf_5knot overfitting? | Higher knot count can reduce holdout error without primary success. | sensitivity_recovery class; tdf_5knot not counted as robust success. | Blocked holdout and stability tables per galaxy. |
| R06 | Why even/odd holdout? | Simple, reproducible radial split with train-only refit. | Frozen even/odd gate; additional splits diagnostic only. | Compare blocked thirds as co-primary in protocol v2. |
| R07 | Why not k-fold only? | k-fold requires sufficient points; used diagnostically when n≥15. | radial_kfold in pipeline tables; not primary claim gate. | Protocol amendment if k-fold made primary. |
| R08 | Why no lensing test? | No lensing data or forward model in this repository phase. | Claim C20-G: lensing not tested. | Lensing after frozen τ maps and protocol sign-off. |
| R09 | Does this disprove dark matter? | No. Halo baselines remain competitive; NGC7814 is NFW-favored on holdout. | Prohibited claim C20-F; NFW wins canonical failure case. | None (claim boundary is permanent). |
| R10 | Does this replace ΛCDM? | No. Rotation-curve subset benchmark only. | Prohibited cosmology language; MOND as empirical baseline only. | None. |
| R11 | Why not hierarchical Bayes? | Not implemented; goal was transparent frequentist pipeline audit. | Reproducible scripts and frozen CSV outputs. | Bayesian marginalization as separate study. |
| R12 | Why not MOND EFE? | External Field Effect not modeled; simple MOND interpolation baseline only. | Documented MOND scope; fair comparison at fixed baryons. | EFE-aware MOND extension if added to protocol. |
| R13 | Why not cluster tests? | Single-galaxy rotation curves only; no cluster lensing or kinematics. | Scope limits in limitations table. | Cluster-scale tests outside current benchmark. |
| R14 | Why claim no universal τ profile? | τ(r) shapes differ per galaxy; only reconstruction law is shared. | Equations in manuscript; claim C20-H not supported. | Meta-analysis across cohort if protocol allows. |
| R15 | Why is NGC7814 still a failure? | All TDF knot variants fail even/odd holdout vs NFW/MOND at canonical baryons. | Mandated label; Phase 4D–4G diagnostics without removing label. | Diagnostic M/L only; not “solved” language. |
| R16 | Why count sensitivity-recovery separately? | tdf_5knot improvements can be flexibility artifacts, not primary wins. | Three galaxies flagged; excluded from 15/20 robust count. | Radial maps (5B-R) document mechanism. |
| R17 | Why emphasize NFW over Burkert? | Burkert often boundary-limited under frozen bounds on this subset. | Burkert in pipeline but not primary gate; paragraph in manuscript. | Wider bounds study without changing frozen labels. |
| R18 | Are bootstrap intervals significance tests? | No. They are descriptive uncertainty brackets for cohort fractions. | Manuscript states non-significance framing. | Formal paired tests only if preregistered. |
| R19 | Why fixed K_τ? | Benchmark holds K_τ constant to reduce parameter proliferation. | K_τ sensitivity phases documented; not measured here. | Joint K_τ inference with calibration protocol. |
| R20 | Why compare to MOND with fitted a₀? | Empirical rotation-curve competitor widely used in SPARC studies. | mond_fit_a0_simple in holdout tables; not cosmological MOND claim. | Fixed-a₀-only sensitivity already in pipeline. |
| R21 | Is 15/20 statistically strong? | We report descriptive fractions with bootstrap intervals, not discovery claims. | paper_statistical_summary.csv; no p-value language. | Larger preregistered cohort. |
| R22 | Why UGC00128 mixed? | NFW marginally best; tdf_5knot worse than tdf_3knot on holdout. | mixed_result class; excluded from primary success. | Finer radial splits for near-tie cases. |
| R23 | Can TDF win in-sample but fail holdout? | Yes; NGC5055-style cases motivated sensitivity_recovery class. | Holdout-first primary gate; in-sample AIC not primary. | Publish in-sample vs holdout delta table in supplement. |
| R24 | Is the code reproducible? | Yes—frozen scripts and CSV lineage from ingestion to audit. | Reproducibility appendix; repository misc citation. | Zenodo DOI at release. |
