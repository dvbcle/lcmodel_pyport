# LCModel CLI Step 9: Full Scientific Port Completion Plan

## Purpose
Define the remaining implementation steps required to move from "computed-mode scaffolding" to a full scientific Python port, with compare-only parity tests against Fortran outputs.

## Compare-Only Rule
Fortran artifacts are used only as a validation oracle.
- Allowed: parse Fortran outputs/checkpoints and compare metrics.
- Not allowed: copy Fortran outputs into Python-generated results.
- Required: Python outputs must be generated from Python pipeline state (`control`, `raw`, `basis`, solver state).

## Remaining Steps to Full Scientific Port

1. Remove residual reference dependencies from computed mode
- Current state:
  - completed for computed orchestration path.
  - computed mode now derives prelim/fullfit checkpoints from Python engines.
- Target:
  - computed mode derives prelim/fullfit state from Python engines only.
- Exit tests:
  - `VT-I-004`, `VT-I-005`, `VT-I-006` pass using Python-emitted checkpoints only.

2. Complete preliminary-stage numerics (`DOFULL=F` and pre-fullfit path)
- Implement shift/phase/FWHM estimation behavior to match LCModel flow.
- Exit tests:
  - `VT-I-004`, `VT-S-001`, `VT-N-003`.

3. Complete fullfit-stage numerics (`DOFULL=T`)
- Implement solver loop, regularization search, and best-snapshot behavior.
- Current progress:
  - computed fullfit checkpoint now derives `S/N`, phase terms, and alpha terms from computed prelim/raw/basis state (no reference parse in generation path).
  - alpha-B solve now uses explicit regula-falsi root solve on computed target.
- Exit tests:
  - `VT-I-005`, `VT-N-001`, `VT-N-002`, `VT-U-N-008`, `VT-U-N-011`.

4. Generate final report state from computed fit state
- Replace placeholder concentration/misc generation with solver-derived values.
- Current progress:
  - report concentrations now come from nonnegative solve against parsed basis spectral payload templates.
  - misc/print fields in computed output now consume computed prelim/fullfit state.
- Exit tests:
  - `VT-I-006`, `VT-N-001`, `VT-N-002`.

5. Close output parity on `.table/.coord/.corraw/.print`
- Ensure numeric and structural parity by case branch.
- Exit tests:
  - `VT-C-002`, `VT-C-003`, `VT-C-004`, `VT-C-005`, `VT-N-001..VT-N-004`.

6. Close `.ps` parity workflow (weak contract + visual check)
- Keep `.ps` as weak automated contract, then perform manual visual parity.
- Fallback path:
  - if visual mismatch persists, inspect PS-input checkpoints first (`ppm_axis`, `phased_data`, `fit`, `background`).
- Exit tests:
  - `ps_input_parity_stage` pass + manual checklist from `docs/ps_visual_inspection.md`.

7. Tighten tolerances and remove known differences
- Start with existing tolerance profile, then tighten once parity is stable.
- Exit tests:
  - `VT-E2E-EVID-001` has `fail=0`, no temporary exceptions for active metrics.

8. Final acceptance gate
- One command produces evidence JSON with all stages passing.
- Acceptance:
  - both external branches (`case02_trace_full`, `case03_trace_prelim_only`) pass all contract, checkpoint, numeric, and compare-only scientific parity tests.

## Single-Run Evidence Target
- Primary run:
  - `python -m pytest tests/test_evidence_external_dataset.py -q`
- Required end-state assertions:
  - `output_numeric_regression_stage.status == "pass"`
  - all `cases[*].overall_case_ok == true`
  - summary: `fail == 0`, `not_implemented == 0`

## Current Status Snapshot (as of 2026-03-09)
- Compare-only parity infrastructure is in place.
- Computed-mode generation/orchestration tests pass for contracts.
- Evidence run is green (`fail=0`, `not_implemented=0`) for the external dataset fixture pair.
- Compare-only scientific parity tests are green for both branches.
- Gate 1 is complete; Gate 2/3 numerical deepening is in progress.
- Gate 3/4 implementation has started with basis payload parsing and solver-derived concentration wiring.
