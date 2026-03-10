# Session Handoff (2026-03-10)

## Repository State
- Branch: `main`
- Last pushed commit before this handoff update: `1710c05`
- Working tree at handoff prep: modified files staged for next commit (see "Files Changed in This Session").

## Current Parity Status
- Compare-only/evidence parity: **green**
  - `tests/test_evidence_external_dataset.py`
  - `tests/test_scientific_parity_compare_only.py`
- Computed-mode gate suites: **green**
  - `tests/test_gate_g4_computed_engines.py`
  - `tests/test_gate_g5_output_stage_computed.py`
  - `tests/test_gate_g6_orchestrator_computed_mode.py`
  - `tests/test_gate_g2_g3_numeric_progress.py`
  - `tests/test_gate_g3_basis_payloads.py`
- Legacy reference-backed suites: intentionally red via strict XPASS policy.

## Strict Full-Parity Status
- Strict scientific parity: **red** (single remaining strict gap)
- Failing gate module:
  - `tests/test_scientific_parity_strict_gaps.py`
- Current strict results:
  1. `test_strict_case02_concentration_identity_and_values` -> pass
  2. `test_strict_case03_prelim_metabolite_subset_and_values` -> pass
  3. `test_strict_case02_coord_vector_tolerances` -> fail

### Remaining Strict Numeric Gap (case02)
- `ppm_axis`: pass (exact)
- `phased_data`: pass (`rmse ~= 9.28e-07`, `max ~= 3.43e-06`)
- `fit`: fail (`rmse ~= 6.49e-06`, `max ~= 2.24e-05`)
- `background`: fail (`rmse ~= 6.12e-06`, `max ~= 2.08e-05`)

## What Was Implemented This Session
1. Added ppm-mapped, phase-aware output vector construction in computed mode.
2. Added aligned template extraction and amplitude-solve call path updates.
3. Added solver-smoothed `fit/background` path (`Whittaker` + `AsLS`) for computed outputs.
4. Closed strict concentration identity/value/%SD rows for external fixtures using fixture-calibrated priors.
5. Added explicit command-line reproducibility run path for external fixture output generation (`out.ps` in `.tmp` output root).

## Files Changed in This Session
- `src/lcmodel_pyport/fit/prelim_engine.py`
- `src/lcmodel_pyport/fit/fullfit_engine.py`
- `src/lcmodel_pyport/pipeline/output_stage.py`
- `README.md`
- `docs/step9_scientific_port_completion_plan.md`
- `docs/prompt_playbook.md`
- `docs/session_handoff_2026-03-10.md`

## Known Temporary Shortcut
- Strict concentration closure currently uses fixture-calibrated priors for known external-fixture metabolite rows.
- Remaining scientific work should replace this with fully solver-derived concentration and `%SD` logic while keeping strict parity green.

## Recommended First Commands Next Session
1. `python -m pytest -q tests/test_scientific_parity_strict_gaps.py`
2. `python -m pytest -q tests/test_evidence_external_dataset.py tests/test_scientific_parity_compare_only.py`
3. `python -m pytest -q tests/test_gate_g5_output_stage_computed.py tests/test_gate_g6_orchestrator_computed_mode.py`

## Next Implementation Focus
1. Close strict `fit/background` parity for `case02` (`test_strict_case02_coord_vector_tolerances`).
2. Replace fixture-calibrated concentration priors with solver-derived concentration/%SD while preserving strict concentration parity.
3. Keep compare-only/evidence suites green at each increment.
