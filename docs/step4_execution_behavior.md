# LCModel CLI Step 4: Execution Behavior and Golden Runs

## Scope
This document captures runtime-observed LCModel CLI behavior from executable runs and turns it into parity checks for a Python port.

- Source of truth for behavior: executable outputs plus `lcmodel_fortran/LCModel.f`.
- Tie-break rule: if comments and behavior diverge, use executable code paths.
- Focus: CLI only (no GUI/manual GUI chapters).

## Execution Inputs Used
- Upstream test data: `.tmp_upstream_lcmodel/test_lcm/`
- Upstream Windows binary: `.tmp_upstream_lcmodel/binaries/win/win10/LCModel.exe.zip`
- Local run workspace: `artifacts/step4_exec/`

## Reproduction Cases

### Case 01: Baseline upstream control
- Directory: `artifacts/step4_exec/case01`
- Control: `control.file`
- Command: `LCModel.exe < control.file`
- Output checked: `out.ps`

### Case 02: Full-trace run (`DOFULL=T`)
- Directory: `artifacts/step4_exec/case02_trace_full`
- Control: `control_trace_full.file`
- Key overrides:
  - `filpri/filcoo/filtab/filcor/filps` explicit file targets
  - `lprint=11, lcoord=12, ltable=13, lcoraw=14, lps=8`
  - `ldump(1..3)=.true.`
- Output checked:
  - `out_trace_full.print`
  - `out_trace_full.coord`
  - `out_trace_full.table`
  - `out_trace_full.corraw`
  - `out_trace_full.ps`

### Case 03: Preliminary-only trace (`DOFULL=F`)
- Directory: `artifacts/step4_exec/case03_trace_prelim_only`
- Control: `control_trace_prelim.file` (same as Case 02 plus `dofull=.false.`)
- Output checked:
  - `out_trace_prelim.print`
  - `out_trace_prelim.coord`
  - `out_trace_prelim.table`
  - `out_trace_prelim.corraw`
  - `out_trace_prelim.ps`

## Observed Branch Behavior

### Full vs prelim branch markers in `.print`
- Full run (`out_trace_full.print`):
  - `DOFULL=T` (line 159)
  - preliminary basis block present (line 409)
  - final basis block present (line 1238)
  - `Preliminary full analysis with alphaB ... alphaS ...` (line 1280)
  - `Reference Solution for rephased data` present (lines 1315, 1518)
  - `Phase Pair ... Decrease ... of alphaB/alphaS` present (line 1591)
  - final misc includes non-zero `alphaB,S = 1.7E-01, 3.7E-01` (line 1836)
- Prelim-only run (`out_trace_prelim.print`):
  - `DOFULL=F` (line 159)
  - preliminary basis block present (line 410)
  - no final-analysis alpha search markers
  - final misc includes `alphaB,S = 0.0E+00, 0.0E+00` (line 1253)

### Quantitative differences in `.table`
- Full run: `$$CONC 36 lines`, `$$MISC 6 lines`, `$$DIAG 0 lines`, `$$INPU 18 lines`
- Prelim-only run: `$$CONC 6 lines`, `$$MISC 5 lines`, `$$DIAG 0 lines`, `$$INPU 19 lines`
- Full run misc values:
  - `FWHM = 0.084 ppm`, `S/N = 21`
  - `alphaB,S = 1.7E-01, 3.7E-01`
  - `2 inflections. 1 extrema`
- Prelim-only misc values:
  - `FWHM = 0.110 ppm`, `S/N = 15`
  - `alphaB,S = 0.0E+00, 0.0E+00`
  - no inflection/extrema line

### Coordinate output contract in `.coord`
Both traced runs contain:
- concentration table
- misc table
- `NY` ppm axis block
- `NY phased data points follow`
- `NY points of the fit to the data follow`
- `NY background values follow`

Observed counts:
- Full run: `498 points on ppm-axis = NY`
- Prelim-only run: `498 points on ppm-axis = NY`

### Corrected RAW output contract in `.corraw`
Both traced runs:
- start with `&SEQPAR` then `&NMID` headers
- include corrected complex time-domain rows in `FMTDAT="(2e15.6)"`
- contain 1035 lines total for this dataset/control set

## Source-Code Anchors (Code Truth)

### Top-level flow and `DOFULL` branch
- Main flow around preliminary/final stages in [`lcmodel_fortran/LCModel.f`](../lcmodel_fortran/LCModel.f):331-362
- `IF (.not.DOFULL)` handling after `STARTV` in [`lcmodel_fortran/LCModel.f`](../lcmodel_fortran/LCModel.f):5935-5941

### Full-analysis alpha search signaling
- `Preliminary full analysis with alphaB ... alphaS` format in [`lcmodel_fortran/LCModel.f`](../lcmodel_fortran/LCModel.f):7250-7252
- `Phase Pair ... Decrease ... alphaB/alphaS` format in [`lcmodel_fortran/LCModel.f`](../lcmodel_fortran/LCModel.f):7430-7433

### Output table and misc serialization
- `$$CONC`/concentration table write in [`lcmodel_fortran/LCModel.f`](../lcmodel_fortran/LCModel.f):10419-10427
- `ETCOUT` generation (`FWHM`, `Data shift`, `Ph`, `alphaB,S`) in [`lcmodel_fortran/LCModel.f`](../lcmodel_fortran/LCModel.f):10692-10735
- inflection/extrema lines in [`lcmodel_fortran/LCModel.f`](../lcmodel_fortran/LCModel.f):10736-10748
- `.coord` NY/data/fit/background emission in [`lcmodel_fortran/LCModel.f`](../lcmodel_fortran/LCModel.f):10775-10787

### `.ps` behavior and degraded-mode output
- PostScript generation entry in [`lcmodel_fortran/LCModel.f`](../lcmodel_fortran/LCModel.f):10942-11041
- one-page table/diagnostics rendering, including `.NOT.DOFULL` "CRUDE MODEL" branch in [`lcmodel_fortran/LCModel.f`](../lcmodel_fortran/LCModel.f):11441-11483

## Reproducibility Notes for Porting
- `out.ps` from Case 01 and upstream `out_ref_build.ps` have same line count (855) but differ in hash/content.
- Stable differences include:
  - version/build string (`6.3-1R` vs `6.3-1N`)
  - timestamp line
  - binary-like encoded plot payload differences
- Porting implication:
  - treat `.ps` as a weak regression target (presence/structure checks), not strict byte-level parity.
  - prefer `.table`, `.coord`, `.corraw` for algorithmic parity checks.

## Step 4 Porting Acceptance Checks
For the same control/data pair, a Python port should satisfy:

1. Case 03 (`DOFULL=F`) omits final-analysis markers and reports `alphaB,S = 0`.
2. Case 02 (`DOFULL=T`) includes final-analysis markers and reports non-zero `alphaB,S`.
3. Case 02 has materially richer concentration table than Case 03 (`NCONC` increase).
4. `.coord` contains the same section ordering (`ppm`, phased data, fit, background).
5. `.table` contains all four section headers: `$$CONC`, `$$MISC`, `$$DIAG`, `$$INPU`.
6. `.corraw` includes `&SEQPAR` and `&NMID` headers and `NUNFIL`-length complex data payload.

These checks become baseline regression tests before algorithm refactoring.
