# Assumptions

- The reconstruction law is universal, but each galaxy has its own reconstructed tau profile/map.
- `K_tau` is a run-level normalization/calibration parameter, not a measured universal constant.
- Negative residual handling is explicit and policy-driven (`allow_signed`, `clip_to_zero`, `mask_negative`).
- `dtaudr_reconstructed` is a reconstruction quantity derived from rotation-curve residuals.
- No universal closed-form tau profile is introduced.
