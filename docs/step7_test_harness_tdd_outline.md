# LCModel CLI Step 7: Verification Strategy and Reusable Test Harness Specification

## Purpose
Define a concrete, reusable verification specification for the Python port.

This document is intentionally implementation-ready (test IDs, schemas, gates), but it does not add code scaffolding.

## Scope
- In scope:
  - golden fixture governance,
  - parser/normalization contracts,
  - test case definitions and IDs,
  - tolerance policies,
  - CI gating and regression handling.
- Out of scope:
  - production solver implementation,
  - architecture/package choices (Step 8),
  - generated test code in this step.

## Normative Inputs
- Functional requirements:
  - `docs/step6_porting_functional_specs.md`
- Runtime behavior baseline:
  - `docs/step4_execution_behavior.md`
  - `artifacts/step4_exec/case01`
  - `artifacts/step4_exec/case02_trace_full`
  - `artifacts/step4_exec/case03_trace_prelim_only`
- Code truth:
  - `lcmodel_fortran/LCModel.f`

## Verification Principles
1. Structural parity is strict.
2. Behavioral branch parity is strict.
3. Numeric parity is tolerance-based and metric-specific.
4. Known deltas must be explicit, versioned, and reviewed.
5. No silent broadening of tolerances in CI.

## Fixture Package Specification

### FXS-001 Directory Layout
Recommended fixture root:
- `tests/fixtures/lcmodel/`
  - `case01_baseline/`
  - `case02_full_trace/`
  - `case03_prelim_only/`
  - `manifest.yaml`
  - `checksums.sha256`

### FXS-002 Manifest Schema
Required manifest fields per case:
- `id`: stable identifier
- `description`
- `inputs`:
  - `control`
  - `raw`
  - `basis`
  - optional `h2o`
- `expected_outputs`:
  - required: `table`, `coord`
  - optional: `print`, `corraw`, `ps`
- `mode_tags`:
  - `dofull`: `true|false`
  - `trace`: `true|false`
- `tolerance_profile`
- `required_tests`: list of test IDs

### FXS-003 Integrity Rules
- Each fixture file is checksum-pinned.
- Any fixture update requires:
  - checksum update,
  - changelog note,
  - impact summary on test baselines.

## Canonical Parse Model Specification

All comparator logic uses parsed canonical objects, not raw text diffs.

### CPM-001 Parsed `.table` Model
Required keys:
- `sections.conc.header`
- `sections.conc.rows[]`
- `sections.misc.header`
- `sections.misc.rows[]`
- `sections.diag.header`
- `sections.diag.rows[]`
- `sections.inpu.header`
- `sections.inpu.rows[]`

### CPM-002 Parsed `.coord` Model
Required keys:
- `conc_rows[]`
- `misc_rows[]`
- `ppm_axis[]`
- `phased_data[]`
- `fit[]`
- `background[]` (optional when absent by mode)

### CPM-003 Parsed `.print` Model
Required keys:
- `flags.dofull`
- `markers[]`
  - e.g. full-analysis markers, phase-pair markers
- `misc_summary`

### CPM-004 Parsed `.corraw` Model
Required keys:
- `seqpar`
- `nmid`
- `data_complex[]`

### CPM-005 Parsed `.ps` Model (weak contract)
Required keys:
- `has_expected_sections`
- `diagnostic_markers[]`
- `line_count`

No byte-equality assertions for `.ps`.

## Intermediate Source-of-Truth Checkpoints

This section defines where intermediate data is checked after specific Python stages.

## Checkpoint Artifact Specification

### ICS-001 Checkpoint Storage
Recommended location:
- `tests/fixtures/lcmodel/checkpoints/<case_id>/<checkpoint_id>.json`

Each checkpoint artifact should contain:
- `checkpoint_id`
- `stage_name`
- `case_id`
- `source` (`fortran_reference` or `python_run`)
- `scalars` (key metrics)
- `vectors` (or sampled vector summaries)
- `hashes` (optional digest of long arrays)
- `metadata` (version, timestamp, generator)

### ICS-002 Checkpoint Source Generation
- Primary source: parseable intermediate markers from Fortran detailed output (`.print`) using trace controls (`ldump`, `idump`) where available.
- Secondary source: derived checkpoints from final artifacts (`.table`, `.coord`, `.corraw`) when direct internal dumps are unavailable.
- Python must emit equivalent stage checkpoints during verification runs.

## Stage-to-Checkpoint Map

| Checkpoint ID | Python Stage | Source-of-Truth Data | Minimum Assertions |
|---|---|---|---|
| `CP-CTRL-001` | `control_stage` | control file + input-change extraction | normalized control values, "last assignment wins", required defaults |
| `CP-RAW-001` | `raw_stage` | RAW/NMID parsing + scaling path | `nunfil` length, `FMTDAT` parse validity, scale factors, `SEQACQ/BRUKER` branch flags |
| `CP-BASIS-001` | `basis_stage(1)` | stage-1 basis selection | metabolite count, selected IDs, stage-1 dimensions |
| `CP-PRELIM-001` | `prelim_stage(pass1)` | preliminary branch trace | shift/phase/FWHM start metrics, objective monotonicity sanity |
| `CP-PRELIM-002` | `prelim_stage(pass2)` optional | `CHECK_CHLESS` branch behavior | reduced basis behavior only when trigger conditions are met |
| `CP-FULL-001` | `fullfit_stage` (`DOFULL=T`) | full-analysis trace markers | alpha-search markers, nonzero alpha regime, best-snapshot transitions |
| `CP-FINAL-001` | `finalize_stage` | pre-output report state | concentration row count regime, misc metrics presence, diagnostics state |
| `CP-OUT-001` | `output_stage` | `.table/.coord/.corraw/.print` parsers | section ordering, required headers, vector lengths |

## Intermediate Checkpoint Tests

### VT-I-001 Control Checkpoint Parity
- Compare `CP-CTRL-001` python checkpoint against reference checkpoint.

### VT-I-002 Raw Stage Checkpoint Parity
- Compare `CP-RAW-001` for parsing/scaling/correction branch flags.

### VT-I-003 Basis Stage Checkpoint Parity
- Compare `CP-BASIS-001` dimensions and selected metabolite identities.

### VT-I-004 Preliminary Stage Checkpoint Parity
- Compare `CP-PRELIM-001` (and `CP-PRELIM-002` when active).

### VT-I-005 Full Stage Checkpoint Parity
- Compare `CP-FULL-001` for full-case fixtures only.

### VT-I-006 Finalization Checkpoint Parity
- Compare `CP-FINAL-001` prior to text formatting.

### VT-I-007 Output Checkpoint Parity
- Compare `CP-OUT-001` with canonical output parse models.

## Normalization Specification

### NRM-001 Strip Unstable Fields
- timestamps,
- build-only identifiers when not behavior-relevant,
- trailing whitespace.

### NRM-002 Preserve Behavior-Critical Values
Never normalize away:
- branch markers (`DOFULL`, phase-pair/full-analysis markers),
- section headers/order,
- concentrations and misc metrics,
- coordinate vectors.

## Test Suite Definition

## Suite A: Contract Tests (fast)

### VT-C-001 Required Output Presence
- Assert required output files exist per fixture manifest.

### VT-C-002 Table Section Contract
- Assert `.table` contains `$$CONC`, `$$MISC`, `$$DIAG`, `$$INPU` in canonical order.

### VT-C-003 Coord Section Contract
- Assert `.coord` contains ppm, phased data, fit, background sections in order.

### VT-C-004 Corraw Header Contract
- Assert `.corraw` contains `SEQPAR` and `NMID` header blocks.

### VT-C-005 Branch Marker Contract
- `DOFULL=T` fixtures include full-analysis markers.
- `DOFULL=F` fixtures exclude full-analysis markers.

## Suite B: Semantic Parity Tests (medium)

### VT-S-001 Mode-Specific Behavior
- For prelim-only fixture, assert degraded-model marker path is present.

### VT-S-002 Concentration Regime Check
- For shared dataset controls, full mode has richer concentration output regime than prelim-only.

### VT-S-003 Input Change Log Consistency
- Assert normalized input-change rows reflect control overrides used in fixture.

## Suite C: Numeric Regression Tests (slower)

### VT-N-001 Misc Scalar Metrics
- Compare:
  - `FWHM`,
  - `S/N`,
  - `Data shift`,
  - phase terms,
  - `alphaB,S`.

### VT-N-002 Concentration Rows
- Compare concentration rows by metabolite key with tolerance profile.

### VT-N-003 Vector Comparisons
- Compare `ppm_axis`, `phased_data`, `fit`, `background` with vector tolerances.

### VT-N-004 Corraw Payload Shape
- Compare complex payload length and sampled value deltas.

### VT-N-005 External Dataset Scientific Parity Gate (compare-only)
- Run Python computed mode on external fixtures and compare generated outputs to Fortran artifacts.
- Pass criteria:
  - case-level `overall_case_ok=true` for both `DOFULL=T` and `DOFULL=F` branches.
- Guardrail:
  - Fortran outputs are oracle-only; they must not be used as generation inputs.

### VT-N-006 Compare-Only Scalar/Concentration Detail Gate
- For each external case, compare:
  - misc scalar deltas within configured tolerance profile,
  - concentration rows keyed by metabolite.
- Emit per-case metric deltas in machine-readable report.

## Suite D: Diagnostic Tests (manual/debug)

### VT-D-001 Artifact Diff Report
- Emit machine-readable diff report per failed fixture/metric.

### VT-D-002 Parsed Snapshot Dump
- Emit canonical parsed JSON objects for failed tests.

## Suite E: Numerical Unit Tests (module-level)

These tests validate numerical kernels independently of full fixture runs.

### VT-U-N-001 FFT Round-Trip
- `ifft(fft(x)) ~= x` for deterministic complex vectors across representative lengths.

### VT-U-N-002 Frequency Reindex Convention
- Validate rearranged-frequency index mapping used by legacy flow.

### VT-U-N-003 Integer Shift Consistency
- Validate that time/frequency shift implementations match expected phase-ramp equivalence.

### VT-U-N-004 Zero-Order Phase Rotation
- Apply known phase rotation to synthetic data and assert exact expected transform within tolerance.

### VT-U-N-005 First-Order Phase Ramp
- Validate ppm-dependent phase term behavior around reference center.

### VT-U-N-006 RAW Scaling Rule
- Verify `FCALIB*TRAMP/VOLUME` scaling against controlled synthetic inputs.

### VT-U-N-007 Nonnegative Linear Solver Validity
- On synthetic constrained systems, assert nonnegativity and KKT-residual bounds.

### VT-U-N-008 Regula-Falsi Search Behavior
- Validate convergence on monotonic test functions and boundary/fallback behavior.

### VT-U-N-009 Regularization Matrix Construction
- Assert matrix dimensions, symmetry expectations, and stability for representative settings.

### VT-U-N-010 Inflection/Extrema Counters
- Validate counter functions on synthetic lineshapes with known inflection/extrema counts.

### VT-U-N-011 Snapshot Save/Restore Idempotence
- Assert save/restore paths preserve state exactly for representative solver states.

### VT-U-N-012 Covariance/Uncertainty Sanity
- Validate covariance symmetry and nonnegative uncertainty extraction on controlled cases.

### VT-U-N-013 Window Index Mapping Integrity
- Validate `LDATST/LDATEN/NY/NYUSE`-style window conversions from 1-based to 0-based indexing on synthetic fixtures.

## Suite F: Index/Type/Error Unit Tests (module-level)

### VT-U-I-001 Loop Bound Equivalence
- Assert translated Python loops visit the same logical element set as original Fortran bounds.

### VT-U-I-002 Slice Boundary Equivalence
- Assert slice conversions preserve inclusive Fortran endpoints where intended.

### VT-U-T-001 Typed Schema Validation
- Validate required data models reject missing/ill-typed fields before stage execution.

### VT-U-T-002 Integer Control Field Enforcement
- Ensure integer control variables are explicitly typed and reject float/string coercion without explicit conversion rules.

### VT-U-E-001 Recoverable Error Mapping
- Assert recoverable legacy conditions map to warning diagnostics without crashing the run.

### VT-U-E-002 Fatal Error Mapping
- Assert fatal legacy conditions raise explicit fatal exceptions with stage and context details.

### VT-U-E-003 I/O Error Context Propagation
- Assert file read/write failures include file path, stage name, and case ID in error payload.

## Requirement-to-Test Traceability

| Step 6 Requirement | Primary Test IDs |
|---|---|
| RQ-001, RQ-002 | VT-I-001, VT-C-005, VT-S-003 |
| RQ-003 | VT-I-002, VT-C-004, VT-N-004, VT-U-N-006 |
| RQ-004 | VT-I-003, VT-S-002, VT-N-002 |
| RQ-005 | VT-I-001..VT-I-007, VT-C-001, VT-C-005 |
| RQ-006 | VT-I-004, VT-C-005, VT-S-001 |
| RQ-007 | VT-I-004, VT-I-005, VT-C-005, VT-S-001 |
| RQ-008 | VT-I-005, VT-C-005, VT-N-001, VT-N-005, VT-U-N-008, VT-U-N-011 |
| RQ-009 | VT-C-001, VT-I-007 |
| RQ-010 | VT-C-002, VT-N-001, VT-N-002, VT-N-006, VT-I-006 |
| RQ-011 | VT-C-003, VT-N-003, VT-N-005, VT-I-007 |
| RQ-012 | VT-C-004, VT-N-004, VT-I-007 |
| RQ-013 | VT-C-001, VT-D-001 |
| RQ-014 | VT-S-001, VT-D-001, VT-U-N-012 |
| RQ-015 | VT-U-N-013, VT-U-I-001, VT-U-I-002, VT-I-007 |
| RQ-016 | VT-U-T-001, VT-U-T-002, VT-I-001 |
| RQ-017 | VT-U-E-001, VT-U-E-002, VT-U-E-003, VT-D-001 |

## Tolerance Policy Specification

Each case points to a tolerance profile ID in `manifest.yaml`.

### TOL-Base (initial default)
- `exact_string`: strict equality.
- `exact_int`: strict equality.
- `float_abs_default`: `1e-8`
- `float_rel_default`: `1e-4`
- `vector_rmse_default`: `1e-5`
- `vector_max_abs_default`: `1e-4`

### TOL-PrelimOnly
- Same as `TOL-Base`, but allow expected absence of full-analysis markers.

### TOL-FullTrace
- Same as `TOL-Base`, but require presence of full-analysis markers.

### TOL-UnitNumerics
- `float_abs_default`: `1e-10`
- `float_rel_default`: `1e-7`
- `vector_rmse_default`: `1e-8`
- For solver tests, allow dedicated residual thresholds per test ID.

### TOL-IndexTypeError
- Index tests: exact index-set equality.
- Type tests: exact pass/fail behavior by schema rule.
- Error tests: exact exception class + required context fields.

Tolerance values are initial placeholders and must be tuned from empirical runs, then version-locked.

## Regression Exception Governance

### EXC-001 Known Differences Registry
Keep `tests/known_differences.yaml` entries with:
- `id`,
- `case_id`,
- `test_id`,
- `metric`,
- `expected_delta`,
- `justification`,
- `date`,
- `owner`.

### EXC-002 Change Control
Any new exception requires:
- linked issue reference,
- review approval,
- explicit expiration/removal condition when applicable.

## CI Gate Policy

### CI-PR (required on every PR)
- Run Suite A + selected Suite B + critical unit tests:
  - numeric: `VT-U-N-001`, `003`, `006`, `007`
  - index/type/error: `VT-U-I-001`, `VT-U-T-001`, `VT-U-E-002`
- Fail build on any contract failure.

### CI-Main (required on merge to main)
- Run Suite A + B + representative Suite C + full Suite E and Suite F.

### CI-Nightly (full regression)
- Run full Suite A/B/C + full intermediate checkpoint suite + Suite E + Suite F.
- Publish diff reports and parsed snapshots on failure.

## Reporting Specification

### REP-001 Machine-Readable Result
Per test run, emit JSON with:
- `case_id`,
- `test_id`,
- `status`,
- `metric_results[]`,
- `tolerance_profile`,
- `artifact_links` (if failed).

### REP-002 Human Summary
Emit concise summary table:
- passed/failed counts by suite,
- top failing metrics,
- links to detailed reports.

## Recommended Build-Out Sequence (Once Coding Starts)
1. Implement fixture manifest reader and checksum verifier.
2. Implement `.table` parser and Suite A tests.
3. Implement `.coord` parser and vector comparator.
4. Implement `.print` parser for branch markers.
5. Implement `.corraw` parser and payload checks.
6. Add intermediate checkpoint emitters and `VT-I-*` tests.
7. Add numerical unit tests (`VT-U-N-*`) and dedicated tolerance profile.
8. Add index/type/error unit tests (`VT-U-I-*`, `VT-U-T-*`, `VT-U-E-*`).
9. Add numeric tolerance engine and Suite C.
10. Add CI reporting and known-difference enforcement.

## Step 7 Completion Criteria
Step 7 is complete when:
1. Every Step 6 requirement maps to at least one executable test ID.
2. Fixture manifest and tolerance profiles are versioned and checksum-guarded.
3. CI gate rules are defined for PR/main/nightly.
4. Regression exception process is documented and enforceable.
5. Intermediate stage checkpoints are defined and testable for both `DOFULL=T` and `DOFULL=F` paths.
6. Numerical kernels have explicit unit-test coverage independent of end-to-end fixtures.
7. Index conversion, typed schema validation, and error translation all have explicit unit-test coverage.
