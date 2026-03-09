# LCModel CLI Step 2: Program Flow and Function Breakdown

## Scope
This Step 2 document decomposes the runtime flow into function-level design specs suitable for porting to Python.

- Source of truth: `LCModel.f` + includes already baselined in Step 1.
- Full routine inventory remains in:
  - `docs/step1_routine_inventory.tsv`
- This document focuses on the core CLI pipeline and its direct support routines (the routines that define behavior, not every low-level FFT helper).

## End-to-End Runtime Flow (CLI)

### Global startup and control setup
1. `PROGRAM LCMODL`
2. `MYCONT`
3. If not `BASCAL`: `CHECK_ZERO_VOXELS`
4. If `IAVERG >= 1`: `AVERAGE`
5. Setup optional restart/CSV continuation state

### Per-voxel loop
1. `RESTORE_SETTINGS`
2. `OPEN_OUTPUT`
3. If voxel not skipped:
   - `LOADCH`
   - `INITIA`
4. If not `BASCAL`:
   - `DATAIN` (internally `MYDATA` when needed)
5. If skipped: continue to next voxel
6. `MYBASI(1)` -> `COMBIS` -> `STARTV(1)`
7. Optional reduced-prelim branch:
   - `CHECK_CHLESS`
   - if triggered: `MYBASI(1)` -> `COMBIS` -> `STARTV(2)`
8. If `DOFULL`:
   - `MYBASI(2)` -> `COMBIS` -> `TWOREG`
9. `FINOUT`
10. If multivoxel: `UPDATE_PRIORS`

### End of run
- Close/flush outputs and checkpoint files
- `STOP` (or fatal path via `ERRMES`/`EXITPS`)

## Function Design Specs by Phase

## Phase A: Control, Input Contracts, and Dataset Framing

### `PROGRAM LCMODL`
- Purpose:
  - Top-level orchestrator for global setup and voxel traversal.
- Main inputs:
  - Control namelist stream (`LCONTR`), basis/raw/h2o/output filenames and unit numbers (through shared state).
- Main outputs:
  - Runs complete analysis pipeline and emits outputs per enabled output channel.
  - Maintains checkpoint/resume counters for CSI save mode.
- Key side effects:
  - Controls multivoxel iteration order and skip logic.
  - Handles restart and CSV append behavior.

### `MYCONT`
- Purpose:
  - Read and finalize control variables (including `SPTYPE` presets and validation).
- Key behavior:
  - Reads namelist twice from scratch-copy of stdin:
    1. initial read for preliminary defaults
    2. reread to let explicit user inputs override preset mutations
  - Applies `SPTYPE` preset logic via:
    - `muscle-1.inc`
    - `liver-1.inc`
    - `lipid-1.inc`
  - Validates dimensions, unit/file combinations, option consistency.
  - Sets mode-dependent fields (`DOWS`, calibration modes, baseline/alpha scaling, etc.).
- Outputs:
  - Fully resolved run configuration in shared state.

### `CHECK_ZERO_VOXELS`
- Purpose:
  - Fast scan of RAW data to mark voxels that are identically zero.
- I/O contract:
  - Reads `/NMID/` then one complex record per voxel.
- Outputs:
  - `ZERO_VOXEL(IVOXEL)` mask populated for later skip logic.

### `AVERAGE`
- Purpose:
  - Aggregate multiple input voxel acquisitions into one effective signal depending on `IAVERG` mode.
- Key behavior:
  - Calls `MYDATA` repeatedly and combines signals with optional normalization/weighting.
  - Updates control/settings for following single-voxel analysis path.

### `RESTORE_SETTINGS`
- Purpose:
  - Reset mutable settings that were adapted by prior voxel analyses.
- Outputs:
  - Reinitializes selected priors/phase/shift ranges for next voxel pass.

### `OPEN_OUTPUT`
- Purpose:
  - Open output files for current voxel and emit headers/namelist summaries where applicable.
- Key behavior:
  - For multivoxel datasets, rewrites title/filenames with voxel identifiers.
  - Uses reduced output namelist (`LCMODeL`) for output serialization when configured.

### `LOADCH`
- Purpose:
  - Capture effective control changes text for later output tables.
- Output:
  - Fills `CHANGE(*)` lines used in report sections.

### `INITIA`
- Purpose:
  - Initialize derived grid/spectral quantities before fitting.
- Key outputs:
  - `NDATA`, `PPMINC`, analysis-window indices (`LDATST`, `LDATEN`), `NY`, `NYUSE`
  - `DELPPM`, compacted `PPM` axis (gaps removed)
  - constants/scales used downstream (`RADIAN`, `TOFWHM`, etc.)

### `DATAIN`
- Purpose:
  - Prepare per-voxel data stream for fitting.
- Key behavior:
  - Calls `MYDATA` (unless external averaging mode already loaded data).
  - Optional absolute-value transform path (zero-fill -> FFT -> abs -> inverse FFT).
  - Calls `FTDATA(0)` to build initial frequency-domain representation.
  - Contains legacy licensing checks (behavioral side effect on run continuation).

### `MYDATA`
- Purpose:
  - Read and scale raw time-domain data; optionally read H2O reference and apply correction paths.
- Inputs:
  - `/NMID/` for RAW and optionally H2O.
  - Optional `/seqpar/` probe.
- Key behavior:
  - Applies `TRAMP/VOLUME` scaling (`FCALIB` for RAW path).
  - Handles `SEQACQ` / `BRUKER` transforms.
  - Optional smoothing and ECC/water-reference handling.
  - Supports `UNSUPR` mode replacing `DATAT` by H2O signal.

## Phase B: Basis Construction and Model Composition

### `MYBASI(LSTAGE)`
- Purpose:
  - Load basis spectra, select metabolites/simulations, scale and transform to internal representation.
- Inputs:
  - `/BASIS1/`, repeated `/BASIS/`, basis spectral records.
  - Stage (`LSTAGE=1` preliminary subset, `LSTAGE=2` final/full model).
- Key behavior:
  - Builds `BASIST(*,jmetab)` (time-domain basis vectors used by solver).
  - Applies omission/selection logic (`CHOMIT`, `CHKEEP`, `CHUSE1`, `PPMMET`, etc.).
  - Configures priors for shifts and linewidth/RT2 deltas.
  - Parses/creates simulated components (`CHSIMU`) via `PARSE_CHSIMU`.
  - Optional water scaling (`WATER_SCALE`) under configured conditions.
- Outputs:
  - `NMETAB`, `NACOMB`, `BASIST`, prior vectors and flags needed by `SETUP/SOLVE`.

### `COMBIS`
- Purpose:
  - Construct concentration-combination structure.
- Outputs:
  - `NCONC`, `NCOMPO`, `LCOMPO`
  - Table ordering metadata (`TABLE_TOP`, `ICONC_LINE_TABLE`)

## Phase C: Preliminary Alignment and Starting Estimates

### `STARTV(ipass)`
- Purpose:
  - Obtain robust starting estimates for shift/phase/linewidth and lineshape grid size.
- Key behavior:
  - Cross-correlation based shift start from reference peaks.
  - Calls `FTDATA`/`SHIFTD` and `PHASTA` for initial phase estimates.
  - Runs coarse search with repeated `PLINLS(1)` evaluations.
  - Chooses best start and sets:
    - `FWHMST` (and `FWHMST_full`)
    - shift state (`ISHIFD` path)
    - phase state (`PHITOT`, `DEGZER`, `DEGPPM` updates through rephasing path)
    - `NSIDES` and `INCSID` (for lineshape convolution model).

### `FTDATA(ISHIFT)` and `SHIFTD(ISHIFT)`
- Purpose:
  - Build frequency-domain data from time-domain input and extract analysis window with selected shift.
- Outputs:
  - `DATAF` (rearranged spectrum), `CY` (current window), `RMSAMP`, `ISHIFD`, `ISTAGO`.

### `PHASTA`
- Purpose:
  - Estimate initial phase correction parameters before full nonlinear optimization.

### `CHECK_CHLESS`
- Purpose:
  - Heuristic branch to drop selected low-confidence metabolite groups and rerun preliminary stage.

## Phase D: Full Regularized Optimization

### `TWOREG`
- Purpose:
  - Main full-analysis driver with alpha regularization search and fallback fixed-DEGPPM series.
- Key behavior:
  - Starts with unconstrained/full pass via `TWORG2`.
  - If unstable/unusual conditions and configured (`IDGPPM>=0`), runs fixed-DEGPPM series and selects candidate by SSQ/baseline-distance rules.

### `TWORG2` / `TWORG3`
- Purpose:
  - Execute reference/full passes and alpha-search strategy.
- Key behavior:
  - Calls `SETUP(2)`, `PLINLS(2/3)`, `RFALSI`, `REPHAS`, `SAVBES`.
  - Manages rephase retries (`MREPHA`) and fixed-phase optional branch (`ENDPHA`).

### `RFALSI` and `SSRANG`
- Purpose:
  - Regula-falsi search in alpha space to satisfy probability/SSQ targets.
- Outputs:
  - Updated `ALPHAB`, `ALPHAS`, and selected best-solution slots in `SAVBES` buffers.

### `SETUP(LSTAGE)`
- Purpose:
  - Build per-stage optimization structure and initialize nonlinear parameters.
- Key behavior:
  - Computes baseline knot count and basis (`GBACKG`).
  - Eigendecomposes baseline regularizer and forms square-root regularizer matrix.
  - Initializes lineshape, phase, shift, and RT2-related nonlinear parameters.
  - Sets dimensions (`NLIN`, `NNONL`, `NSIDE2`, etc.) for solver.

### `SOLVE(LSTAGE, DONONL, PMQACT, ONLYFT, LERROR)`
- Purpose:
  - Core model assembly + constrained least squares solve + objective evaluation.
- Solver core:
  - Builds model matrix `DAMAT` and RHS from current nonlinear state.
  - Uses `PNNLS` for nonnegative linear subproblem.
  - Appends rows for:
    - concentration-ratio priors
    - shift/RT2/phase priors
    - baseline and lineshape regularizers (`ALPHAB`, `ALPHAS`)
    - Marquardt damping rows (`PMQACT`) in nonlinear update mode.
- Modes:
  - `ONLYFT=T`: compute fit components for plotting without overwriting covariance-forming matrix path.
  - `DONONL=F/T`: objective-only vs nonlinear-step context.

### `PLINLS(ISTAGE)`
- Purpose:
  - Nonlinear outer loop (Marquardt-like step control) around `SOLVE`.
- Key behavior:
  - Iterative step proposal/acceptance with objective reduction and cosine tests.
  - Uses `PASTEP` to enforce step bounds and nonnegativity constraints.
  - Convergence/stopping controlled by stage-specific thresholds (`MITER`, `RCONVR`, etc.).

### `REPHAS`
- Purpose:
  - Apply accumulated phase corrections to `CY` and reset phase parameters for continued optimization.

### `SAVBES(ILEVEL)`
- Purpose:
  - Central solution snapshot/restore mechanism for candidate tracking.
- Usage:
  - `1`: save current candidate
  - `2`: promote candidate to active best
  - `>=3` and negative levels: store/restore alternative scenarios (e.g., fixed-DEGPPM series)

## Phase E: Final Reporting and Output Products

### `FINOUT`
- Purpose:
  - Reconstruct best solution, compute fit products, covariance/error stats, and emit report outputs.
- Key behavior:
  - Optional final rephasing loop for plotting stability.
  - Replays best state from `SAVBES`.
  - Calls `SOLVE` twice:
    - nonlinear context to rebuild covariance-relevant structures
    - `ONLYFT` context to produce plot curves (`YREAL`, `YFITRE`, `BACKRE`)
  - Computes covariance/correlation and concentration uncertainty tables.
  - Writes outputs to enabled channels (`LPRINT`, `LCOORD`, `LTABLE`, `Lcsv`, `LCORAW`).

### `EXITPS`, `MAKEPS`, `ONEPAG`, `ERRTBL`
- Purpose:
  - Final diagnostics table assembly and PostScript/report generation.
- Key behavior:
  - `MAKEPS` produces one or more pages based on `ISTAGO` and available fit products.
  - `ONEPAG` draws axis/grid/curves/table regions.
  - `ERRTBL` compiles diagnostic summary lines.

### `UPDATE_PRIORS`
- Purpose:
  - Update multivoxel-adaptive priors (shift/phase dispersion windows) after each completed voxel analysis.

## Porting-Oriented Architecture Notes (Python)

## 1) Preserve stage semantics explicitly
- Keep explicit stage/mode enums for:
  - `LSTAGE` (1 prelim, 2 full)
  - `ISTAGE` in nonlinear solver (1/2/3)
  - `DONONL`, `ONLYFT` execution modes
- Avoid implicit branch coupling through global flags.

## 2) Replace `COMMON`-block coupling with typed state objects
- Suggested primary state containers:
  - `ControlConfig` (inputs and options from namelist + defaults)
  - `GridState` (ppm grid/window indices/gaps)
  - `DataState` (raw/H2O time data, frequency data, current window `CY`)
  - `BasisState` (loaded basis/simulated basis and metabolite metadata)
  - `FitState` (linear/nonlinear params, priors, alpha values, best-solution snapshots)
  - `OutputState` (tables, diagnostics, file routing)

## 3) Keep `SAVBES` behavior as first-class API
- Porting risk is high if candidate snapshot semantics are altered.
- Implement explicit snapshot store/restore with named slots (instead of numeric magic indices where possible), then keep numeric compatibility layer for verification.

## 4) Maintain two-pass control parse contract
- Required behavioral parity:
  - first pass for preset shaping
  - second pass for explicit user override

## 5) Preserve solver matrix assembly ordering
- `SOLVE` row/column block ordering drives covariance and diagnostics.
- Keep deterministic ordering identical during early parity phase.

## Step 2 Deliverable Status
- Program flow has been decomposed into phase-by-phase function specs.
- Core routines now have porting-oriented responsibility/contract definitions.
- This is sufficient to start Step 3 design outputs (module boundaries + testable port plan), while preserving traceability to original Fortran behavior.
