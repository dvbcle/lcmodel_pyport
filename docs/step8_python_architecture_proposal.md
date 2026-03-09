# LCModel CLI Step 8: Python Architecture Proposal

## Purpose
Propose a Python architecture that directly implements the Step 6 functional contracts and is verifiable through Step 7 test definitions.

## Design Drivers
1. Behavioral parity first.
2. Strong contract boundaries between parsing, pipeline, solver, and reporting.
3. Deterministic outputs for reproducible regression testing.
4. Incremental implementation path aligned with fixture-based TDD.

## Proposed Repository Layout

```text
src/lcmodel_pyport/
  __init__.py
  cli.py
  config/
    control_parser.py
    defaults.py
    change_log.py
    models.py
  io/
    raw_reader.py
    basis_reader.py
    h2o_reader.py
    namelist_utils.py
  core/
    orchestrator.py
    state.py
    voxel_loop.py
  preprocess/
    fft_ops.py
    shift_phase.py
    averaging.py
    ecc.py
  basis/
    stage_builder.py
    selection_rules.py
    combination_builder.py
  fit/
    prelim_engine.py
    fullfit_engine.py
    solver_linear.py
    solver_nonlinear.py
    regularization.py
    snapshots.py
  report/
    table_writer.py
    coord_writer.py
    corraw_writer.py
    print_writer.py
    ps_writer.py
    diagnostics.py
  verify/
    parsers_table.py
    parsers_coord.py
    parsers_print.py
    parsers_corraw.py
    compare.py
    tolerances.py
```

## Component Mapping from Step 6

| Step 6 Component | Python Module Group |
|---|---|
| FC-1 `control_layer` | `config/*` |
| FC-2 `io_raw_layer` | `io/raw_reader.py`, `io/h2o_reader.py` |
| FC-3 `io_basis_layer` | `io/basis_reader.py`, `basis/*` |
| FC-4 `pipeline_orchestrator` | `core/orchestrator.py`, `core/voxel_loop.py` |
| FC-5 `prelim_engine` | `fit/prelim_engine.py` |
| FC-6 `fullfit_engine` | `fit/fullfit_engine.py`, `fit/regularization.py`, `fit/snapshots.py` |
| FC-7 `reporting_layer` | `report/*` |

## Core Data Model Strategy

Use typed dataclasses for internal state and immutable config objects where possible.

### Primary models
1. `ControlConfig`
2. `RawDataset`
3. `BasisStageData`
4. `VoxelRunState`
5. `ReportState`

### Storage conventions
1. Numerical arrays in `numpy.ndarray`.
2. Complex time/frequency data in complex dtype arrays.
3. Output row models as structured records before formatting.
4. Explicit conversion functions from internal models to file-format text.

## Stage Interfaces

### Orchestrator contract
`run_pipeline(config: ControlConfig) -> RunSummary`

### Per-voxel contract
`run_voxel(state: VoxelRunState, config: ControlConfig) -> VoxelRunState`

### Stage entrypoints
1. `control_stage`
2. `raw_stage`
3. `basis_stage(stage_id)`
4. `prelim_stage(pass_id)`
5. `fullfit_stage`
6. `finalize_stage`
7. `output_stage`

Each stage returns updated state plus diagnostics events for reporting.

## Numerical Engine Plan

### FFT and transforms
1. Centralize FFT/sign/rearrangement in `preprocess/fft_ops.py`.
2. Keep all shift/phase conventions in one module (`preprocess/shift_phase.py`).

### Solvers
1. Separate linear constrained solve and nonlinear iteration:
   - `solver_linear.py`
   - `solver_nonlinear.py`
2. Keep regularization and alpha search isolated in `regularization.py`.
3. Preserve best-solution snapshot semantics in `snapshots.py`.

### Determinism controls
1. Stable ordering for table/report rows.
2. Fixed floating formatting rules in writers.
3. Explicit random-free execution path.

## Reporting Architecture

### Writer layering
1. Build canonical `ReportState`.
2. Pass `ReportState` into format-specific writers.
3. Keep text formatting and numeric computation separate.

### Output gating
1. Gate file generation by logical-unit and filename semantics from `ControlConfig`.
2. Enforce `.ps` writer gating on non-blank `filps`.

## Verification Integration by Design

### Built-in comparability
1. Keep report generation deterministic and parse-friendly.
2. Reuse `verify/*` canonical parsers as both test helpers and debug tools.
3. Emit optional structured run metadata for CI diff reports.

### Test harness alignment
1. Map Stage 7 test IDs to module-level tests.
2. Keep fixture manifest-driven runs independent from implementation internals.

## Module-to-Test Traceability Matrix

The following matrix maps implementation modules to the specific Step 7 test IDs they must satisfy.

| Module / Layer | Primary Test IDs | Gate Intent |
|---|---|---|
| `config/control_parser.py` | VT-I-001, VT-S-003, VT-C-005 | control parsing correctness and branch-flag integrity |
| `config/change_log.py` | VT-S-003, VT-I-001 | input-change extraction and reporting parity |
| `io/raw_reader.py` | VT-I-002, VT-C-004, VT-N-004, VT-U-N-006 | RAW parsing/scaling and corrected RAW contracts |
| `io/h2o_reader.py` | VT-I-002, VT-C-004 | H2O side-path parsing and header contract integrity |
| `io/basis_reader.py` | VT-I-003, VT-S-002 | basis read/selection parity |
| `basis/stage_builder.py` | VT-I-003, VT-S-002, VT-N-002 | stage-specific basis composition behavior |
| `basis/selection_rules.py` | VT-I-003, VT-S-002 | omit/keep/simulate rule parity |
| `basis/combination_builder.py` | VT-N-002, VT-I-006 | concentration combination row semantics |
| `preprocess/fft_ops.py` | VT-U-N-001, VT-U-N-002, VT-U-N-003 | FFT convention and index mapping parity |
| `preprocess/shift_phase.py` | VT-U-N-003, VT-U-N-004, VT-U-N-005 | shift/phase numerical correctness |
| `preprocess/averaging.py` | VT-I-002, VT-C-005 | averaging path consistency and mode behavior |
| `preprocess/ecc.py` | VT-I-002, VT-N-004 | ECC/correction path consistency |
| `fit/prelim_engine.py` | VT-I-004, VT-S-001, VT-C-005 | prelim branch and degraded-mode semantics |
| `fit/fullfit_engine.py` | VT-I-005, VT-N-001, VT-C-005 | full-analysis markers and misc metric parity |
| `fit/regularization.py` | VT-U-N-008, VT-U-N-009, VT-N-001 | alpha-search and regularizer behavior |
| `fit/solver_linear.py` | VT-U-N-007, VT-N-002 | constrained linear solve correctness |
| `fit/solver_nonlinear.py` | VT-N-001, VT-N-003 | nonlinear update stability and fit metrics |
| `fit/snapshots.py` | VT-U-N-011, VT-I-005 | best-state save/restore correctness |
| `core/orchestrator.py` | VT-I-001..VT-I-007, VT-C-001, VT-C-005 | stage ordering, branch execution, artifact completeness |
| `core/voxel_loop.py` | VT-C-001, VT-I-007 | voxel iteration/skip semantics |
| `report/table_writer.py` | VT-C-002, VT-N-001, VT-N-002 | table section contract and scalar/conc outputs |
| `report/coord_writer.py` | VT-C-003, VT-N-003 | coord ordering and vector output parity |
| `report/corraw_writer.py` | VT-C-004, VT-N-004 | corrected RAW header/payload contract |
| `report/print_writer.py` | VT-C-005, VT-S-001, VT-I-007 | branch markers and diagnostics text parity |
| `report/ps_writer.py` | VT-C-001, VT-D-001 | PS gating and diagnostic structure parity |
| `report/diagnostics.py` | VT-S-001, VT-D-001, VT-U-N-012 | diagnostics consistency and uncertainty sanity |
| `verify/parsers_*` | VT-D-002, VT-C-002, VT-C-003, VT-C-004 | canonical parse reliability |
| `verify/compare.py` | VT-N-001, VT-N-002, VT-N-003, VT-N-004 | comparator correctness across metric classes |
| `verify/tolerances.py` | VT-N-001..VT-N-004, VT-U-N-* | tolerance profile enforcement |

## Module Implementation Gates

Each module group should be considered "ready" only when its mapped critical tests pass.

### Gate G1: Config and RAW I/O
Required passing tests:
- VT-I-001, VT-I-002, VT-S-003, VT-U-N-006, VT-C-004

### Gate G2: Basis and Preliminary Flow
Required passing tests:
- VT-I-003, VT-I-004, VT-S-001, VT-S-002, VT-C-005

### Gate G3: Numerical Kernels
Required passing tests:
- VT-U-N-001 through VT-U-N-012

### Gate G4: Full Fit and Snapshot Behavior
Required passing tests:
- VT-I-005, VT-N-001, VT-U-N-008, VT-U-N-011

### Gate G5: Reporting Outputs
Required passing tests:
- VT-C-002, VT-C-003, VT-C-004, VT-N-002, VT-N-003, VT-N-004

### Gate G6: End-to-End Orchestration
Required passing tests:
- VT-I-001..VT-I-007, VT-C-001..VT-C-005, representative VT-N-* set

## Dependency Strategy

### Required
1. `numpy` for array math.
2. `scipy` for numerical methods where needed.
3. `pyyaml` for fixture manifests and tolerance profiles.

### Optional
1. `matplotlib` for local plot diagnostics only.
2. `rich` for improved CLI diagnostics formatting.

Keep runtime dependencies minimal for deterministic CI.

## Error Model

### Exception classes
1. `ControlParseError`
2. `InputFormatError`
3. `NumericalConvergenceError`
4. `OutputContractError`

### Diagnostics events
1. `info`
2. `warning`
3. `fatal`

Each stage emits structured events that writers can convert to legacy-like diagnostics text.

## Incremental Delivery Plan

### Phase A (I/O and contracts)
1. Implement `config` and `io` layers.
2. Pass Gate G1.
3. Pass contract tests for `.table/.coord/.corraw` structure with placeholders.

### Phase B (preliminary path)
1. Implement `prelim_engine`.
2. Pass Gate G2.
3. Pass `DOFULL=F` fixture branch tests.

### Phase C (full path)
1. Implement `fullfit_engine` and regularization search.
2. Pass Gate G3 and Gate G4.
3. Pass `DOFULL=T` fixture branch and numeric tests.

### Phase D (hardening)
1. Implement reporting writers to pass Gate G5.
2. Pass Gate G6 (orchestration-wide).
3. Tighten tolerances.
4. Resolve known differences.
5. Stabilize CI gate profiles.

## Risks and Mitigations

### Risk 1: Hidden coupling from legacy globals
Mitigation:
1. Use explicit state objects with stage-local mutation.
2. Enforce stage interface contracts in tests.

### Risk 2: Numeric drift in solver behavior
Mitigation:
1. Use per-metric tolerances.
2. Introduce staged numeric assertions before tightening.

### Risk 3: Output-format regressions
Mitigation:
1. Centralize writers.
2. Keep canonical parser-based regression tests mandatory in CI.

## Architecture Exit Criteria
1. Module boundaries trace directly to Step 6 components.
2. All Step 6 requirements map to concrete modules and stage interfaces.
3. Step 7 test IDs can be attached to architecture components without ambiguity.
4. Implementation can proceed incrementally while preserving parity visibility.
