# LCModel CLI Step 6: Porting-Grade Functional Specifications (Architecture-Driving)

## Purpose
Define a detailed functional specification that is precise enough to drive Step 8 architecture decisions without forcing a specific implementation style.

This document is the normative behavior contract for the Python CLI port.

## Scope
- In scope:
  - CLI behavior and stage flow,
  - explicit data contracts and interface contracts,
  - state lifecycle and mutation rules,
  - Fortran-to-Python indexing semantics,
  - explicit typing/schema constraints,
  - error-handling translation requirements,
  - output contract requirements,
  - parity acceptance criteria and traceability.
- Out of scope:
  - GUI behavior,
  - performance optimization strategy,
  - package/framework selection details (reserved for Step 8).

## Source of Truth
- Primary: `lcmodel_fortran/LCModel.f`
- Supporting:
  - `docs/step2_program_flow_function_breakdown.md`
  - `docs/step4_execution_behavior.md`
  - `docs/step5_cli_manual_crosscheck.md`

Tie-break rule: if comments/manual language and executable behavior differ, use code/runtime behavior.

## System Context
LCModel CLI performs spectroscopy quantification by:
1. Reading control, basis, and raw spectroscopy inputs.
2. Building stage-specific analysis models.
3. Running preliminary and (optionally) full regularized fitting.
4. Emitting concentration/diagnostic/report outputs across several file formats.

## Functional Requirement Set

### RQ-001: CLI Invocation and Control Input
- Support stdin-driven control input (`lcmodel < control.file` equivalent).
- Parse namelist `LCMODL` with default+override semantics.
- Repeated assignments resolve as "last assignment wins".

Anchors:
- `LCModel.f:70-72`, `731-742`, `862-867`
- `artifacts/step4_exec/case01/control.file:1`

### RQ-002: Control Parsing Compatibility
- Accept practical controls with `$LCMODL` in column 1.
- Preserve legacy-compatible handling of namelist formatting variants where feasible.
- Preserve ability to capture effective input changes for reporting.

Anchors:
- `LCModel.f:2107-2121`
- `docs/step5_cli_manual_crosscheck.md`

### RQ-003: RAW Input Contract
- Support optional `/seqpar/`, then `/NMID/`, then complex time-domain data.
- Honor `FMTDAT`.
- Preserve defaults `TRAMP=1`, `VOLUME=1` when omitted.
- Preserve RAW scaling by `FCALIB*TRAMP/VOLUME`.
- Preserve `SEQACQ` and `BRUKER` correction branches.

Anchors:
- `LCModel.f:2777-2814`, `2827-2856`

### RQ-004: Basis Input Contract
- Honor `BASIS1` and repeated `BASIS` entries.
- Preserve stage-specific basis behavior:
  - stage 1: preliminary,
  - stage 2: full.
- Preserve omit/keep/simulate and prior setup behavior.

Anchors:
- `LCModel.f:3216` (entry)
- `docs/step2_program_flow_function_breakdown.md` (`MYBASI`, `COMBIS`)

### RQ-005: Runtime Stage Flow
- Preserve the global and per-voxel flow ordering described in Step 2.
- Preserve skip-voxel behavior (suppression of normal outputs for skipped voxels).

Anchors:
- `LCModel.f:6`
- `LCModel.f:1805-1816`
- `docs/step2_program_flow_function_breakdown.md` (end-to-end flow)

### RQ-006: Preliminary Stage Behavior
- Preserve start-value and alignment behavior (shift/phase/FWHM-related state).
- Preserve optional reduced-prelim rerun path (`CHECK_CHLESS` branch).

Anchors:
- `LCModel.f:5441` (`STARTV`)

### RQ-007: `DOFULL` Branch Semantics
- `DOFULL` default is true.
- If `DOFULL=F`, skip full analysis and retain prelim-only output semantics.
- Preserve degraded diagnostic path (`CRUDE MODEL`) for prelim-only mode.

Anchors:
- `LCModel.f:541`, `352-356`, `5935-5941`, `11476-11483`
- `out_trace_prelim.print:159`, `out_trace_prelim.ps:420`

### RQ-008: Full Regularized Optimization Semantics
- Preserve alpha-search control flow and candidate handling semantics.
- Preserve availability of full-analysis markers in detailed output.

Anchors:
- `LCModel.f:7250-7252`, `7402`, `7430-7433`
- `out_trace_full.print:1280`, `out_trace_full.print:1591`

### RQ-009: Output Gating and File Control
- Preserve output gating by logical-unit enablement and filenames:
  - `.print`: `LPRINT/FILPRI`
  - `.coord`: `LCOORD/FILCOO`
  - `.table`: `LTABLE/FILTAB`
  - `.corraw`: `LCORAW/FILCOR`
  - `.ps`: `LPS` plus non-blank `FILPS`
- Preserve flexibility of positive logical unit values.

Anchors:
- `LCModel.f:1834-1872`, `10978-10985`

### RQ-010: `.TABLE` Contract
- Emit all four section headers:
  - `$$CONC`, `$$MISC`, `$$DIAG`, `$$INPU`
- Preserve concentration and misc semantics (including alpha/phase/shift/linewidth lines).

Anchors:
- `LCModel.f:10423-10427`, `10692-10735`, `10804-10808`
- `out_trace_full.table:4`, `42`, `50`, `53`

### RQ-011: `.COORD` Contract
- Preserve presence and ordering of:
  - table/misc text,
  - ppm-axis block,
  - phased data,
  - fit,
  - background (when applicable).

Anchors:
- `LCModel.f:10768-10787`

### RQ-012: `.CORAW` Contract
- Preserve corrected RAW output with `SEQPAR` and `NMID` headers and corrected payload.
- Preserve phase and shift correction semantics applied before emission.

Anchors:
- `LCModel.f:10810-10833`

### RQ-013: `.PS` Contract
- Preserve `.ps` generation control flow and plotting-stage semantics.
- Byte-identical parity is not required; structural/report parity is required.

Anchors:
- `LCModel.f:10942-11041`
- `docs/step4_execution_behavior.md` (reproducibility notes)

### RQ-014: Diagnostics/Error Semantics
- Preserve diagnostic section behavior and failure signaling conditions.
- Maintain fail-fast behavior for unrecoverable errors.

Anchors:
- `LCModel.f` (`ERRMES`, `ERRTBL`, `FINOUT` paths)

### RQ-015: Indexing Semantics (Fortran 1-based -> Python 0-based)
- All loop and slice ports shall explicitly account for Fortran 1-based indexing.
- Any translated loop shall preserve original inclusive/exclusive bounds behavior.
- Any window extraction logic (`LDATST`, `LDATEN`, `NY`, `NYUSE`, metabolite indices) shall be verified with explicit index-conversion tests.
- Off-by-one-sensitive calculations must be annotated with original Fortran bounds in code comments or metadata.

Anchors:
- `LCModel.f` loop-heavy stage flow and output sections, including `10775-10787` and fitting loops.

### RQ-016: Explicit Typing and Schema Enforcement
- Python implementation shall not rely on inferred/implicit typing for ported computational state.
- Each major contract model (`ControlConfig`, `RawDataset`, `BasisStageData`, `VoxelRunState`, `ReportState`) shall use explicit typed fields.
- Integer-valued loop/state controls from Fortran (especially I-N naming family) must be explicitly typed and validated.
- Parse layers shall validate schema before execution stages run.

Anchors:
- Fortran implicit typing model and control-variable-heavy paths throughout `LCModel.f`.

### RQ-017: Error-Handling Translation (Fortran Control Flow -> Python Exceptions)
- Fortran error signaling behavior (`ERRMES`, fatal/continue paths, branch-specific diagnostics) shall be mapped to explicit Python exception and diagnostic-event semantics.
- Stage interfaces shall declare recoverable vs fatal failures.
- Python code shall preserve legacy intent:
  - recoverable warnings continue with diagnostics,
  - fatal conditions terminate run with explicit error context.
- Exception messages should include enough context to map back to ported stage and requirement ID.

Anchors:
- `LCModel.f` error pathways (`ERRMES`, `ERRTBL`, open/read/write error branches)

## Architecture-Driving Decomposition (Functional Components)

The architecture step should map to these components, each with clear ownership.

### FC-1 `control_layer`
Responsibilities:
- Parse and normalize control input.
- Apply default+override behavior.
- Record effective input changes (for `$$INPU`/reporting).

Key interfaces:
- `parse_control(stdin_text) -> ControlConfig`
- `extract_effective_changes(raw_control_text, config) -> ChangeLog`

Mapped requirements:
- RQ-001, RQ-002

### FC-2 `io_raw_layer`
Responsibilities:
- Parse `/seqpar/` and `/NMID/`.
- Load raw complex time-domain data.
- Apply RAW/H2O scaling and format-specific corrections (`SEQACQ`, `BRUKER`).

Key interfaces:
- `read_raw_dataset(path, cfg) -> RawDataset`
- `read_h2o_dataset(path, cfg) -> Optional[RawDataset]`

Mapped requirements:
- RQ-003

### FC-3 `io_basis_layer`
Responsibilities:
- Parse basis control/data records.
- Build stage-dependent basis matrices and prior metadata.

Key interfaces:
- `read_basis(path, cfg, stage) -> BasisStageData`

Mapped requirements:
- RQ-004

### FC-4 `pipeline_orchestrator`
Responsibilities:
- Execute global/per-voxel stage ordering.
- Manage skip masks, voxel loop, and per-voxel reset/restore semantics.

Key interfaces:
- `run_pipeline(cfg, data_handles) -> RunResult`

Mapped requirements:
- RQ-005, RQ-007

### FC-5 `prelim_engine`
Responsibilities:
- Preliminary start estimates and associated optional reduced-prelim branch.

Key interfaces:
- `run_preliminary(state, basis_stage1) -> PrelimState`

Mapped requirements:
- RQ-006

### FC-6 `fullfit_engine`
Responsibilities:
- Full regularized analysis (`DOFULL=T` path), alpha-search family behavior, candidate tracking.

Key interfaces:
- `run_fullfit(state, basis_stage2) -> FullFitState`

Mapped requirements:
- RQ-008

### FC-7 `reporting_layer`
Responsibilities:
- Assemble tables, diagnostics, misc metrics, and per-format outputs.
- Enforce section ordering and marker semantics.

Key interfaces:
- `emit_table(report_state, out_path)`
- `emit_coord(report_state, out_path)`
- `emit_corraw(report_state, out_path)`
- `emit_print(report_state, out_path)`
- `emit_ps(report_state, out_path)`

Mapped requirements:
- RQ-009 to RQ-014

## Data Contract Specifications

These schemas are functional contracts; exact class/struct form is architecture-dependent.

All data contracts in this section are required to be explicitly typed and validated at stage boundaries.

### DC-1 `ControlConfig`
Required fields (minimum):
- scalar controls: `nunfil`, `deltat`, `hzpppm`, `dofull`, `iaverg`, `bascal`, `idgppm`
- file controls: `filraw`, `filbas`, `filh2o`, `filpri`, `filcoo`, `filtab`, `filcor`, `filps`
- logical units: `lprint`, `lcoord`, `ltable`, `lcoraw`, `lps`
- arrays/sets needed by stage logic (selection/omit/ratio/simulation flags)

Invariants:
- defaults applied before overrides,
- repeated assignments resolved by final occurrence.

### DC-2 `RawDataset`
Required fields:
- `seqpar` metadata (`hzpppm`, optional `echot`, optional `seq`)
- `nmid` metadata (`fmtdat`, `tramp`, `volume`, `seqacq`, `bruker`, `id`)
- `datat`: complex vector length `nunfil` per voxel

Invariants:
- correction/scaling order preserved,
- parser handles optional `seqpar`.

### DC-3 `BasisStageData`
Required fields:
- stage id,
- selected metabolite list,
- basis vectors in internal representation,
- prior vectors/limits needed by solver stage.

Invariants:
- stage 1 and stage 2 behavior can diverge by design.

### DC-4 `VoxelRunState`
Required fields:
- voxel identifiers and skip flags,
- spectral grids and window indices (`ny`, `nyuse`, etc.),
- shift/phase/linewidth parameters,
- concentrations/errors/covariances,
- best-solution snapshots.

Invariants:
- explicit separation of:
  - persistent run-wide state,
  - per-voxel mutable state,
  - derived transient buffers.

### DC-5 `ReportState`
Required fields:
- concentration table rows,
- misc metrics rows,
- diagnostics rows,
- input-change rows,
- vectors for coord/plot export (ppm, data, fit, background).

Invariants:
- section ordering fixed for `.table` and `.coord`.

## Interface Contract Specifications

Each stage entrypoint must declare:
1. Inputs consumed.
2. State mutated.
3. Outputs produced.
4. Recoverable vs fatal failure modes.

Required stage interfaces:
- `control_stage`
- `raw_stage`
- `basis_stage(stage_id)`
- `prelim_stage(pass_id)`
- `fullfit_stage`
- `finalize_stage`
- `output_stage`

Each interface should be pure-by-default when possible; mutable shared state must be explicit.

Each interface must also document:
- index expectations (original Fortran bounds and translated Python bounds),
- explicit type assumptions for inputs/outputs,
- exception classes that may be raised.

## State Lifecycle Rules

### Global state (run lifetime)
- Control config and fixed constants.
- Caches safe to reuse across voxels.

### Per-voxel state
- Raw/basis-derived working buffers,
- shift/phase/fit intermediate states,
- candidate/best-solution snapshots.

### Reset requirements
- On entering each voxel, reset all mutable per-voxel fields that are not explicitly persisted by algorithm rules.
- Preserve designated adaptive priors only where legacy flow does so.

### Skip behavior
- Skip voxels must bypass normal fitting stages and suppress designated outputs (matching legacy behavior).

## Numerical Kernel Constraints (Functional, Not Implementation)

### NK-1 FFT and spectrum conventions
- Preserve zero-fill and rearranged-frequency conventions used by legacy flow.
- Preserve sign conventions in phase/shift application paths.

### NK-2 Objective/solver behavior
- Preserve nonlinear outer-loop semantics and regularized linear subproblem behavior.
- Preserve branch-level behavior even if solver internals are modernized later.

### NK-3 Determinism requirements
- For identical inputs and fixed tolerances, output sections and ordering must be deterministic.
- Numeric tolerances apply to floating outputs; structural markers must be exact.

### NK-4 Index Integrity Requirements
- Numerical kernels shall include explicit checks for index-domain validity before array operations.
- Any index remapping between Fortran and Python domains must be centralized and test-covered.

## Error and Diagnostic Model

### Severity model
- `fatal`: terminate current run with explicit error state.
- `warning`: continue and record diagnostic message.
- `info`: optional informational diagnostics.

### Required behavior
- Keep diagnostic visibility equivalent to current outputs.
- Preserve key branch markers used in Step 4/7 parity checks.
- Preserve mapping from stage-local failures to clear exception categories and diagnostic severity.

## Output Contract Details

### `.table`
Must include:
- `$$CONC`, `$$MISC`, `$$DIAG`, `$$INPU`
with semantics preserved.

### `.coord`
Must include ordered blocks:
1. concentration/misc text
2. ppm axis
3. phased data
4. fit
5. background (when available)

### `.corraw`
Must include:
- `SEQPAR`,
- `NMID`,
- corrected complex payload.

### `.print`
Must include sufficient branch/trace markers for debugging parity.

### `.ps`
Must honor gating semantics (`FILPS` requirement); strict byte-level equality is not required.

## Requirement-to-Component Traceability

| Requirement | Primary Components |
|---|---|
| RQ-001, RQ-002 | FC-1, FC-4 |
| RQ-003 | FC-2 |
| RQ-004 | FC-3 |
| RQ-005 | FC-4 |
| RQ-006 | FC-5 |
| RQ-007, RQ-008 | FC-4, FC-6 |
| RQ-009 to RQ-014 | FC-7 (+ FC-4 orchestration) |
| RQ-015 | FC-4, FC-5, FC-6, FC-7 |
| RQ-016 | FC-1, FC-2, FC-3, FC-4, FC-7 |
| RQ-017 | FC-4, FC-7 |

This traceability is the handoff boundary for Step 8 architecture mapping.

## Requirement-to-Test Traceability (Step 7 Handoff)

| Requirement Group | Test Focus |
|---|---|
| Control/Parsing | parser compatibility, override semantics, change-log extraction |
| Branch behavior | `DOFULL` full vs prelim markers, stage omission checks |
| Output structure | section headers/order for `.table` and `.coord` |
| Numeric parity | misc metrics, concentration values, vector tolerances |
| Corrected raw | header presence and payload shape |
| Index integrity | explicit 1-based to 0-based conversion checks at stage boundaries |
| Typing/schema | strict model validation before stage execution |
| Error translation | exception/diagnostic mapping parity for recoverable/fatal flows |

## Parity Acceptance Criteria (Execution-Level)

Baseline fixtures:
- `case02_trace_full`
- `case03_trace_prelim_only`

Mandatory assertions:
1. `.table` contains all four expected sections.
2. `DOFULL` marker and full-analysis marker behavior matches expected branch.
3. `.coord` section ordering is preserved.
4. `.corraw` contains expected headers and payload structure.
5. Full case produces richer concentration output regime than prelim-only case.

Tolerance policy:
- Structural assertions: exact.
- Scalar metrics: per-metric absolute/relative tolerance.
- Vectors: RMSE/max-abs tolerance by profile.

## Architecture Guidance Notes for Step 8

1. Use component boundaries FC-1..FC-7 as candidate module boundaries.
2. Define explicit typed models for DC-1..DC-5 before implementing algorithms.
3. Make state transitions explicit at stage boundaries; avoid hidden global mutation where possible.
4. Keep reporting layer decoupled from solver internals so regression checks remain stable.
5. Centralize index conversion helpers and require test coverage before enabling solver stages.
6. Standardize exception classes and severity mapping early so parity diagnostics remain consistent.

## Exit Criteria
- Requirements are explicit, testable, and mapped to components.
- Data/interface/state contracts are detailed enough to drive architecture design directly.
- Traceability to Step 7 tests and Step 8 components is defined.
- Indexing, typing, and error-handling translation requirements are explicit and test-mapped.
