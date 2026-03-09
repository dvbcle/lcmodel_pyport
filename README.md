# LCModel Fortran Porting Project

## Project Goal
Understand the LCModel CLI Fortran source code and produce porting-grade design specifications that enable a reliable implementation in a new language (target: Python).

## AI-Assisted Workflow
This repository uses an AI-assisted coding workflow to:

- investigate and explain the legacy Fortran codebase,
- generate and refine porting specifications,
- help implement and iterate on the Python port.

All generated specifications and code changes should be treated as draft engineering artifacts and validated with reproducible tests and domain review.

## Scope
- Source analyzed: `lcmodel_fortran/LCModel.f` plus local `lcmodel_fortran/*.inc` files.
- Focus: CLI behavior only.
- Out of scope: GUI chapters/features from the LCModel manual.

## What LCModel Does (Current Understanding)
LCModel performs voxel-wise spectroscopy quantification by fitting measured spectra as a combination of basis spectra, with correction and regularization steps (phase/shift handling, baseline/lineshape treatment, and constrained optimization), then outputs concentrations and diagnostics.

## Documentation
Start with these documents:

1. [Step 1: Source Baseline](docs/step1_source_baseline.md)
2. [Step 1: Routine Inventory (TSV)](docs/step1_routine_inventory.tsv)
3. [Step 2: Program Flow and Function Breakdown](docs/step2_program_flow_function_breakdown.md)
4. [Step 4: Execution Behavior and Golden Runs](docs/step4_execution_behavior.md)
5. [Step 5: CLI Manual Cross-Check](docs/step5_cli_manual_crosscheck.md)
6. [Step 6: Porting-Grade Functional Specifications](docs/step6_porting_functional_specs.md)
7. [Step 7: Verification Strategy and Test Harness Spec](docs/step7_test_harness_tdd_outline.md)
8. [Step 8: Python Architecture Proposal](docs/step8_python_architecture_proposal.md)
9. [Step 9: Full Scientific Port Completion Plan](docs/step9_scientific_port_completion_plan.md)
10. [Prompt Playbook (Session Record)](docs/prompt_playbook.md)
11. [PS Visual Inspection Guide](docs/ps_visual_inspection.md)

## Current Plan (Reordered)
1. Baseline source code
2. Recover program structure
3. Trace runtime flow
4. Build behavioral understanding from execution (golden/intermediate runs)
5. Cross-check against LCModel docs (CLI-relevant only)
6. Write porting-grade functional specs
7. Define verification strategy for the port
8. Propose Python architecture (last)

## Status
- Documentation: Steps 1-8 completed.
- Implementation (Python port):
  - Gate G1 complete (`config` + RAW/CORAW + schema validation + basic contracts).
  - Gate G2 complete (basis/preliminary checkpoint parsers + branch/behavior tests).
  - Gate G3 complete (Step 8 module-aligned numerical kernels, indexing helpers, and unit tests).
  - Gate G4 started (fullfit-stage reference checkpoint extraction + parity tests for full mode).
  - Gate G5 in progress (computed-mode output generation now emits `.table/.coord/.corraw/.print/.ps` without reference-output parsing for generation).
- G6 in progress: computed-mode orchestrator path added for case-level staged flow and DOFULL branch behavior checks.
- G7 started: stricter integer control enforcement and explicit missing-input error-path tests.
- Evidence run available: `VT-E2E-EVID-001` (`tests/test_evidence_external_dataset.py`) with JSON/JUnit output and no `not_implemented` stages.
- Evidence regression scope currently covers both external dataset branches (`case02_trace_full`, `case03_trace_prelim_only`).
- Evidence now includes explicit PS-input intermediate parity stage (`ps_input_parity_stage`) for visual-debug fallback.
- Python output-stage now emits inspectable `.ps` files for both external dataset branches.
- Computed-mode orchestration now runs prelim/fullfit checkpoints without reading reference `.print/.table` artifacts.
- Step 9 progress:
  - Gate 1 complete (computed prelim/fullfit checkpoints wired into computed orchestration, compare-only parity/evidence green).
  - Gate 2/3 started (data-derived prelim shift/FWHM behavior and numeric-progress tests added).
  - Gate 3/4 started (basis spectral payload parsing + solver-derived concentration amplitudes + computed fullfit-to-report wiring).
  - Gate 3/4 deepened (fullfit alpha now solved via regula-falsi target, and additional fullfit invariants validated under noise perturbation).
- Current test status:
  - Computed-mode/evidence tests are passing (`tests/test_gate_g5_output_stage_computed.py`, `tests/test_gate_g6_orchestrator_computed_mode.py`, `tests/test_evidence_external_dataset.py`).
  - Compare-only scientific parity tests are passing (`tests/test_scientific_parity_compare_only.py`) for both external branches.
  - New computed checkpoint tests are passing (`tests/test_gate_g4_computed_engines.py`, `tests/test_gate_g2_g3_numeric_progress.py`, `tests/test_gate_g3_basis_payloads.py`).
  - Full `pytest` run is intentionally red on 4 legacy reference-backed tests (`tests/test_gate_g5_output_stage.py`, `tests/test_gate_g6_orchestrator_reference_mode.py`) via strict `xfail` so reference-backed generation paths are explicitly treated as failing during migration.
- Rollback checkpoint tags:
  - `checkpoint/pre_g3_align_20260309`
  - `checkpoint/pre_g4_start_20260309`
  - `checkpoint/pre_g5_start_20260309`
  - `checkpoint/pre_autonomous_g5_complete_20260309`

## Implementation Guidance
Implementation is being driven by:
1. [Step 6: Porting-Grade Functional Specifications](docs/step6_porting_functional_specs.md) as normative behavior contracts.
2. [Step 7: Verification Strategy and Test Harness Spec](docs/step7_test_harness_tdd_outline.md) as executable parity/test definitions.
3. [Step 8: Python Architecture Proposal](docs/step8_python_architecture_proposal.md) as module/gate sequencing.

## Regression Target (Important)
- Ultimate acceptance is **not** byte-equality of `out.ps`.
- Primary regression target is checkpoint + contract + numeric parity:
  - strict structural/branch parity for `.table/.coord/.corraw/.print`,
  - tolerance-based numeric parity for concentrations/scalars/vectors,
  - `.ps` treated as a **weak contract** (gating and expected markers/layout intent, not byte-identical output).

## Repository Notes
- This repository currently contains source and analysis docs.
- Build scripts are not included; the codebase is source-only in its current form.

