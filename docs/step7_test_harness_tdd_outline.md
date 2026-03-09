# LCModel CLI Step 7: Reusable Test Harness Outline for Porting

## Purpose
Define a reusable test-driven development harness for the future Python port, using Step 4 run artifacts as golden references.

This is a design document only. No scaffolding or implementation is included here.

## Scope
- In scope:
  - harness architecture,
  - fixture strategy,
  - parity contracts,
  - tolerance policy,
  - test execution workflow.
- Out of scope:
  - production Python implementation,
  - test code generation in this step.

## Inputs and Golden Sources
- Primary fixture source:
  - `artifacts/step4_exec/case01`
  - `artifacts/step4_exec/case02_trace_full`
  - `artifacts/step4_exec/case03_trace_prelim_only`
- Supporting behavioral reference:
  - `docs/step4_execution_behavior.md`
- Code-truth anchors:
  - `lcmodel_fortran/LCModel.f`

## Core Harness Design

### 1) Fixture Registry
Maintain a manifest for each golden case containing:
- case id and description,
- input files (`control`, `basis`, `raw`),
- expected output files (`.table`, `.coord`, `.print`, `.corraw`, optional `.ps`),
- expected mode tags (`dofull=true|false`, `trace=true|false`),
- tolerance profile id.

Rationale:
- Keeps test definitions data-driven.
- Allows adding new coverage cases without changing test code shape.

### 2) Canonical Parsers
Define output parsers that convert LCModel text outputs into canonical JSON-like structures:
- `.table` parser:
  - sections: `$$CONC`, `$$MISC`, `$$DIAG`, `$$INPU`,
  - concentration rows as structured records.
- `.coord` parser:
  - section boundaries,
  - ppm axis vector,
  - phased-data vector,
  - fit vector,
  - background vector.
- `.print` parser:
  - branch markers (`DOFULL`, alpha-search markers, phase-pair markers),
  - key summary lines.
- `.corraw` parser:
  - header namelists,
  - complex row count and values.

Rationale:
- Makes comparisons stable and machine-readable.
- Reduces brittleness from text formatting differences.

### 3) Normalization Rules
Before comparing, normalize unstable fields:
- strip timestamps and build/version-only strings,
- trim trailing whitespace,
- normalize float formatting to numeric values,
- canonicalize metabolite labels where needed.

Do not normalize behavior-relevant values:
- `alphaB,S`,
- concentration values,
- ppm/fit/background vectors,
- section presence/order.

### 4) Assertion Layers
Use layered checks from strict structural parity to numeric parity:

1. Contract layer (strict):
- required files are produced,
- required sections exist,
- section ordering is valid,
- required branch markers exist or are absent by mode.

2. Semantic layer (mixed strict/tolerant):
- `DOFULL=F` excludes full-analysis markers,
- `DOFULL=T` includes alpha-search markers,
- expected concentration table cardinality regime (`full > prelim` for current fixture set),
- corrected-raw headers match expected shape.

3. Numeric layer (tolerance-based):
- misc metrics (`FWHM`, `S/N`, shift, phase, alpha),
- concentration values and percent SD,
- coordinate vectors (`ppm`, phased data, fit, background),
- optional correlations/diagnostics when available.

### 5) Tolerance Policy
Define explicit per-metric tolerances, not one global tolerance.

Suggested policy classes:
- `exact_string`: section headers and mode markers.
- `exact_int`: row counts and array lengths.
- `float_abs`: quantities near zero.
- `float_rel`: concentrations and scale-varying metrics.
- `vector_rmse`: waveform-like arrays (`fit`, `background`, phased data).

Each case references a tolerance profile so thresholds can evolve deliberately.

## Planned Test Suite Organization

### A) Fast Contract Suite (default local + CI)
- Runs on every change.
- Validates output existence, section structure, marker logic.
- Fails quickly when branch behavior breaks.

### B) Numeric Regression Suite (CI and release gating)
- Runs full fixture comparisons with tolerances.
- Produces comparison reports (per-case metric deltas).
- Used to approve algorithmic-equivalence changes.

### C) Diagnostic/Debug Suite (manual on demand)
- Dumps parsed intermediates and diff views.
- Helps investigate regressions during active porting.

## TDD Workflow for Porting

### Phase-by-phase red/green strategy
Port in small vertical slices and lock each with tests:

1. Input/control parsing parity.
2. Data ingest and preprocessing parity.
3. Preliminary-only flow parity (`DOFULL=F`).
4. Full-flow parity (`DOFULL=T`) with alpha-search markers.
5. Output serialization parity (`.table/.coord/.corraw`).

For each slice:
1. write or activate failing tests against golden expectations,
2. implement minimal code to pass,
3. refactor while keeping tests green.

## Regression Management
- Keep a `known_differences` registry for intentional, reviewed deviations.
- Require each entry to include:
  - case id,
  - metric(s),
  - quantitative delta,
  - justification,
  - owner/date.
- Disallow silent tolerance widening in CI.

## CI and Reproducibility Requirements
- Pin fixture files by checksum.
- Run harness in deterministic mode:
  - fixed locale,
  - fixed numeric formatting behavior,
  - deterministic ordering of rows/reports.
- Archive comparison artifacts on CI failure:
  - parsed outputs,
  - diff summaries,
  - metric delta tables.

## Practical Starting Point Once Porting Begins
Implement in this order:
1. fixture manifest format,
2. `.table` parser + contract tests,
3. `.coord` parser + vector checks,
4. `.print` parser for branch markers,
5. `.corraw` parser,
6. numeric tolerance engine and reporting.

This sequence yields useful test feedback early, before full solver parity exists.

## Exit Criteria for Harness Readiness
Harness is considered ready when:
1. all Step 4 cases run through contract and numeric suites,
2. failures produce actionable per-metric diffs,
3. tolerance profiles are versioned and reviewed,
4. CI gates merges on fast suite and at least one numeric case.
