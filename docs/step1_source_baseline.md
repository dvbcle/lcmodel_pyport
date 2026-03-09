# LCModel CLI Source Baseline (Step 1)

## Scope
This document captures the Step 1 baseline for the source-only codebase:
- file inventory (`.f`, `.inc`)
- entrypoint and top-level execution flow
- include dependency map
- shared-state structure
- logical compile/build units (without build scripts)
- CLI input/output conventions and control parsing routines

All findings are from local source in `lcmodel_fortran/`.

## Source Inventory

| File | Kind | Role |
|---|---|---|
| `lcmodel_fortran/LCModel.f` | Fortran fixed-form source | Main program + all subroutines/functions |
| `lcmodel_fortran/lcmodel.inc` | include | Global dimensions, `COMMON` blocks, shared arrays/state |
| `lcmodel_fortran/nml_lcmodl.inc` | include | Full control namelist definition (`/LCMODL/`) |
| `lcmodel_fortran/nml_lcmodel.inc` | include | Reduced-output namelist definition (`/LCMODeL/`) |
| `lcmodel_fortran/muscle-1.inc` | include | `SPTYPE` preset overrides for muscle analyses |
| `lcmodel_fortran/liver-1.inc` | include | `SPTYPE` preset overrides for liver/breast/lipid families |
| `lcmodel_fortran/lipid-1.inc` | include | Additional `SPTYPE` preset overrides for lipid/breast variants |

Observed but commented/inactive include references in `lcmodel_fortran/LCModel.f`:
- `frahm.inc`
- `devx.inc`
- `devx_linux.inc`

There are no nested `INCLUDE` statements inside any `.inc` file.

## Entrypoint and Top-Level Flow

- Program entrypoint: `PROGRAM LCMODL` (`lcmodel_fortran/LCModel.f:6`).
- Main control setup: `CALL MYCONT()` (`lcmodel_fortran/LCModel.f:160`).
- Main execution loops over voxel positions (single-voxel and CSI/multivoxel supported).
- Per-voxel high-level sequence in `PROGRAM LCMODL`:
  1. `restore_settings`
  2. `open_output`
  3. `LOADCH`
  4. `INITIA`
  5. `DATAIN` (loads raw/H2O data path unless `BASCAL`)
  6. `MYBASI(1)` (basis prep)
  7. `COMBIS`
  8. `STARTV(1)` (+ optional reduced-metabolite rerun via `check_chless`)
  9. If `DOFULL`: `MYBASI(2)` -> `COMBIS` -> `TWOREG`
  10. `FINOUT`
  11. Optional `update_priors` for multivoxel continuation

Top-level does restart handling for CSI save-state files and CSV append mode before voxel loops.

## Include Dependency Map

Effective include graph (active):

- `lcmodel_fortran/LCModel.f`
  - `lcmodel_fortran/lcmodel.inc` in most computational/output routines (global shared state)
  - `lcmodel_fortran/nml_lcmodl.inc` + `lcmodel_fortran/nml_lcmodel.inc` in:
    - `MYCONT` (control namelist read path)
    - `open_output` (namelist echo/write path)
  - `lcmodel_fortran/muscle-1.inc`, `lcmodel_fortran/liver-1.inc`, `lcmodel_fortran/lipid-1.inc` inside `MYCONT` (`SPTYPE`-specific default/preset mutation logic)

No additional include chains exist below these files.

## Shared-State Structure (`lcmodel_fortran/lcmodel.inc`)

`lcmodel_fortran/lcmodel.inc` is the central state contract for the executable:

- Dimension/size parameters (`PARAMETER`) for arrays and model limits
  - examples: `MMETAB`, `MUNFIL`, `MDATA`, `MY`, `MBACKG`, `MSIDES`, etc.
- Major `COMMON` blocks:
  - `/BLCHAR/`: names, filenames, labels, textual controls
  - `/BLCPLX/`: complex spectral arrays (`DATAT`, `DATAF`, `BASIST`, etc.)
  - `/BLDP/`: double-precision work arrays and solver matrices
  - `/BLINT/`: unit numbers, dimensions, counters, loop indices, control integers
  - `/BLLOG/`: logical control flags (`DOECC`, `DOFULL`, `BASCAL`, etc.)
  - `/BLREAL/`: core real-valued model and tuning parameters

Porting implication: nearly all routine coupling occurs through these shared blocks, not explicit argument lists.

## Logical Compile/Build Units (No Build Scripts Present)

Given source layout, the effective logical build model is:

1. Single translation unit:
   - compile `lcmodel_fortran/LCModel.f` (fixed-form Fortran) with include search path containing `lcmodel_fortran/`.
2. Required include files at compile time:
   - `lcmodel_fortran/lcmodel.inc`
   - `lcmodel_fortran/nml_lcmodl.inc`
   - `lcmodel_fortran/nml_lcmodel.inc`
   - `lcmodel_fortran/muscle-1.inc`
   - `lcmodel_fortran/liver-1.inc`
   - `lcmodel_fortran/lipid-1.inc`
3. Optional/commented historical includes are not needed for this source state.

Program-unit inventory extracted from `lcmodel_fortran/LCModel.f`:
- 149 program units total
- 1 `PROGRAM`
- 23 `FUNCTION`s
- remaining are `SUBROUTINE`s (plus `BLOCK DATA`)

## CLI Input and Output Conventions

### Control input

- Source: `LCONTR` (must be standard input per program header comments; default unit is set to 5 in `BLOCK DATA`).
- Parsed in `MYCONT`:
  - copies stdin to `LCONTR_SCRATCH` (scratch unit) to allow rewind/reread
  - reads `/LCMODL/` once for preliminary default shaping
  - applies `SPTYPE` preset includes (`muscle/liver/lipid`)
  - rereads `/LCMODL/` to let explicit user values override preset/default mutations

Namelist sources:
- full control: `lcmodel_fortran/nml_lcmodl.inc` (`/LCMODL/`)
- reduced-print echo: `lcmodel_fortran/nml_lcmodel.inc` (`/LCMODeL/`)

### Raw data input (`FILRAW`)

Routines:
- `check_zero_voxels`: initial voxel zero-detection pass
- `MYDATA`: actual per-voxel raw load and optional H2O load
- `DATAIN`: wrapper around `MYDATA` plus preprocessing/licensing path

Format from code:
- NAMELIST `/NMID/`: `ID, FMTDAT, TRAMP, VOLUME, SEQACQ, BRUKER`
- followed by `NUNFIL` complex points read using format string `FMTDAT`
- optional `/seqpar/` is probed from the same source for `hzpppm, echot, seq`

Optional non-water-suppressed input:
- file `FILH2O` on unit `LH2O`
- same `/NMID/` + complex data structure as raw file

### Basis input (`FILBAS`)

Routine: `MYBASI`

Read order:
1. optional `/seqpar/` probe (`fwhmba, hzpppm, echot, seq`)
2. NAMELIST `/BASIS1/`: `IDBASI, FMTBAS, BADELT, NDATAB`
3. repeated loop:
   - NAMELIST `/BASIS/`: `ID, METABO, CONC, TRAMP, VOLUME, ISHIFT`
   - spectrum record via `FMTBAS`, `NDATAB` complex values

### Outputs

Opened in `open_output` / `MAKEPS` depending on flags and filename variables:
- `FILPRI` (`LPRINT`) detailed print output
- `FILCOO` (`LCOORD`) coordinate/output stream
- `FILCOR` (`LCORAW`) corrected raw output
- `FILTAB` (`LTABLE`) table summary
- `FILPS` (`LPS`) PostScript output
- `FILcsv` (`Lcsv`) CSV summary/append handling in main program

For multivoxel, filenames/titles are rewritten to include voxel coordinates.

### Restart/checkpoint auxiliary files

If `lcsi_sav_1==12` and `lcsi_sav_2==13`, the main program reads/writes progress and adaptive prior data across runs using units 12/13 and filenames `filcsi_sav_1` / `filcsi_sav_2`.

## Step 1 Outcomes

Step 1 requested baseline is complete:
- inventory of all source files
- confirmed entrypoint and top-level CLI execution path
- include dependency map and inactive include references
- shared-state (common-block) structure identified
- logical compile unit reconstructed for source-only repository
- input/output and control parsing conventions documented with routine anchors

## Comment Cross-Check (Requested Verification)

The following Step 1 claims were rechecked against explicit source comments:

- Program-header I/O contract:
  - `LCONTR` standard input (`lcmodel_fortran/LCModel.f:70`)
  - basis input on `LBASIS`/`FILBAS` (`lcmodel_fortran/LCModel.f:73`)
  - raw input on `LRAW`/`FILRAW` (`lcmodel_fortran/LCModel.f:79`)
  - optional H2O input on `LH2O`/`FILH2O` when `DOECC`/`DOWS`/`UNSUPR` (`lcmodel_fortran/LCModel.f:83`)
  - outputs on `LPRINT/LCOORD/LCORAW/LPS/LTABLE` with `FILPRI/FILCOO/FILCOr/FILPS/FILTAB` (`lcmodel_fortran/LCModel.f:91`, `lcmodel_fortran/LCModel.f:94`, `lcmodel_fortran/LCModel.f:97`, `lcmodel_fortran/LCModel.f:101`, `lcmodel_fortran/LCModel.f:104`)
- `MYCONT` behavior comments and includes:
  - purpose: control-variable input (`lcmodel_fortran/LCModel.f:707`)
  - scratch-copy and reread behavior (`lcmodel_fortran/LCModel.f:731`, `lcmodel_fortran/LCModel.f:862`)
  - namelist include sources (`lcmodel_fortran/LCModel.f:722`, `lcmodel_fortran/LCModel.f:723`)
- `MYDATA` comments for raw/H2O data and ECC path (`lcmodel_fortran/LCModel.f:2760`, `lcmodel_fortran/LCModel.f:2762`, `lcmodel_fortran/LCModel.f:2763`)
- `MYBASI` comments for basis read structure and basis namelists (`lcmodel_fortran/LCModel.f:3224`, `lcmodel_fortran/LCModel.f:3254`, `lcmodel_fortran/LCModel.f:3255`, `lcmodel_fortran/LCModel.f:3660`)

No contradictions were found between Step 1 documentation and the in-source comments.


