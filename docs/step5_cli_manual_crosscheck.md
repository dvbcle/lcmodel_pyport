# LCModel CLI Step 5: Manual Cross-Check (CLI-Relevant)

## Scope
This document cross-checks CLI-relevant statements from the LCModel manual against:

- executable behavior from Step 4 artifacts, and
- `lcmodel_fortran/LCModel.f`.

Tie-break rule for porting: when manual text and executable behavior diverge, code/runtime behavior is authoritative.

## Sources Used
- Manual:
  - https://www.s-provencher.com/pub/LCModel/manual/manual.pdf
  - Focused sections: Ch. 5 (`.RAW` / `.CONTROL`), Ch. 9/11/12 (output files, diagnostics, detailed output, hidden controls).
- Code:
  - `lcmodel_fortran/LCModel.f`
- Runtime artifacts:
  - `artifacts/step4_exec/case01`
  - `artifacts/step4_exec/case02_trace_full`
  - `artifacts/step4_exec/case03_trace_prelim_only`

## Cross-Check Matrix

| Topic | Manual (CLI-relevant) | Code/Runtime Observation | Porting Guidance |
|---|---|---|---|
| Launch path | Manual shows direct CLI invocation (`lcmodel < my.control`). | `LCMODL` reads control namelist from stdin (`LCONTR`), matching CLI redirection model. | Preserve stdin-driven control parsing in early port parity mode. |
| `.CONTROL` structure | `.CONTROL` consists of namelist `LCMODL`; only provided variables change from defaults. | Code reads `LCMODL`; defaults are in block data and overwritten by namelist input. | Keep default+override semantics identical. |
| Repeated control variable semantics | Manual: order mostly irrelevant; repeated variables take value nearest end of namelist; Input Changes table reflects bottom-up view. | `MYCONT` does two-pass read over scratch copy; later values remain effective. `LOADCH` captures changes for output tables; Step 4 `.table` contains `$$INPU`. | Preserve effective "last assignment wins" behavior and expose effective input changes in outputs. |
| Namelist formatting rule (column position) | Manual text states first column ignored and `$` in column 2. | Runtime contradicts strict column-2 requirement: Step 4 controls begin with `$LCMODL` in column 1 and parse successfully. `LOADCH` searches `$` at any position (`INDEX`). | Treat manual's strict column-position statement as legacy/compiler-specific. Port parser should accept `$` at column 1. |
| `.RAW` header structure | Manual: optional `SEQPAR`, then `NMID`, then complex data; `FMTDAT` required; `TRAMP/VOLUME` default to 1; `BRUKER`/`SEQACQ` control corrections. | `MYDATA` optionally reads `/seqpar/`, reads `/NMID/` with `FMTDAT` required, scales by `FCALIB*TRAMP/VOLUME`, applies `SEQACQ` and `BRUKER` transforms. | Preserve this parsing and correction order exactly for parity. |
| `.TABLE` archive output | Manual: `.TABLE` contains One-Page table information in text form and is enabled by `LTABLE>0`/`FILTAB`. | Code emits `$$CONC`, `$$MISC`, `$$DIAG`, `$$INPU` sections on `LTABLE`; Step 4 outputs confirm all four sections. | Use `.table` as primary regression target for concentration/misc/diagnostics/input-change parity. |
| `.COORD` output | Manual: `.COORD` contains curve coordinates for plotting; enabled with `LCOORD>0`/`FILCOO`. | Code writes concentration/misc text, ppm axis, phased data, fit, and background blocks; Step 4 `.coord` confirms ordering and section presence. | Preserve section ordering and numeric arrays; this is a high-value parity artifact. |
| `.CORAW` output | Manual: `FILCOR`/`LCORAW` emits corrected `.CORAW`. | Code writes corrected RAW after scaling, ECC/format corrections, and phase/shift correction path; Step 4 `.corraw` has `SEQPAR`+`NMID` headers and payload. | Preserve corrected RAW transformation semantics for testability/debug. |
| Detailed output (`.PRINT`) | Manual: `FILPRI`/`LPRINT` enable detailed ASCII output and default dump flow. | Code opens `FILPRI` when `LPRINT>0`, writes run header + namelist + detailed diagnostics; Step 4 `.print` includes branch markers and full analysis traces. | Keep `.print` richness and branch marker text stable for debugging parity. |
| Logical unit numbers | Manual examples use conventional alternate units (`LPRINT=6`, `LTABLE=7`, `LCOORD=9`, `LCORAW=10`). | Code only gates on `>0`; Step 4 uses non-manual values (`11/12/13/14`) successfully. | Treat unit values as configurable positive integers; do not hardcode manual examples. |
| `.PS` output behavior | Manual (Ch. 5 wording) says `.PS` output is automatic. | `MAKEPS` only opens/writes when `FILPS` is non-blank. `LPS` defaults to 8, but blank `FILPS` suppresses file open. | Preserve actual condition: require an output path (`FILPS`) for reliable `.ps` file emission. |
| Full vs preliminary model control | Manual diagnostics define `CRUDE MODEL` as preliminary-only path when full model is suppressed by control parameters. | Code has explicit `DOFULL` branch (`.TRUE.` default), final stage skipped when false; Step 4 `DOFULL=F` run shows `CRUDE MODEL` and no full alpha-search markers. | Preserve stage branching (`DOFULL`) and associated diagnostics/outputs. |
| Hidden controls | Manual notes hidden control parameters are undocumented and should generally not be changed. | Code contains many controls and stage flags not prominently documented in normal usage paths (including `DOFULL` behavior). | For porting, implement hidden controls for behavioral parity; defer UX simplification until after regression parity. |

## Key Code and Runtime Anchors

### Code anchors (`LCModel.f`)
- CLI input/output contract comments:
  - `LCMODL`/`NMID`/output units: `lcmodel_fortran/LCModel.f:70-106`
- Two-pass control read and scratch-copy behavior:
  - `MYCONT`: `lcmodel_fortran/LCModel.f:731-742`, `lcmodel_fortran/LCModel.f:862-867`
- Optional `SEQPAR`, required `NMID`, scaling/corrections:
  - `MYDATA`: `lcmodel_fortran/LCModel.f:2777-2814`, `lcmodel_fortran/LCModel.f:2827-2856`
- Output file opening and gating:
  - `OPEN_OUTPUT`: `lcmodel_fortran/LCModel.f:1834-1872`
- `.TABLE` / `.COORD` section emission:
  - `FINOUT`: `lcmodel_fortran/LCModel.f:10423-10427`, `lcmodel_fortran/LCModel.f:10768-10809`
- `.CORAW` corrected output path:
  - `FINOUT`: `lcmodel_fortran/LCModel.f:10810-10833`
- `.PS` file open condition:
  - `MAKEPS`: `lcmodel_fortran/LCModel.f:10978-10985`
- `DOFULL` default and branch-sensitive `CRUDE MODEL` diagnostic:
  - default: `lcmodel_fortran/LCModel.f:541`
  - rendering: `lcmodel_fortran/LCModel.f:11476-11483`
- `$LCMODL` detection in `LOADCH` (not column-2 strict):
  - `lcmodel_fortran/LCModel.f:2107-2121`

### Runtime anchors (Step 4 artifacts)
- Column-1 `$LCMODL` in working control file:
  - `artifacts/step4_exec/case01/control.file:1`
- `.TABLE` four sections:
  - `artifacts/step4_exec/case02_trace_full/out_trace_full.table:4`
  - `artifacts/step4_exec/case02_trace_full/out_trace_full.table:42`
  - `artifacts/step4_exec/case02_trace_full/out_trace_full.table:50`
  - `artifacts/step4_exec/case02_trace_full/out_trace_full.table:53`
- `DOFULL` branch markers:
  - `artifacts/step4_exec/case02_trace_full/out_trace_full.print:159`
  - `artifacts/step4_exec/case03_trace_prelim_only/out_trace_prelim.print:159`
- Full analysis markers present only when `DOFULL=T`:
  - `artifacts/step4_exec/case02_trace_full/out_trace_full.print:1280`
  - `artifacts/step4_exec/case02_trace_full/out_trace_full.print:1591`
- `CRUDE MODEL` shown in prelim-only path:
  - `artifacts/step4_exec/case03_trace_prelim_only/out_trace_prelim.ps:420`

## Noted Manual/Code Divergences (Important)

1. Namelist column-position strictness
- Manual text describes strict first-column/column-2 `$` placement.
- Current CLI executable accepts Step 4 control files with `$LCMODL` at column 1.
- Decision for port: accept both forms; do not enforce strict column-2 `$`.

2. `.PS` "automatic" wording vs actual output condition
- Manual wording in Ch. 5 suggests automatic `.PS` output.
- Code requires a non-blank `FILPS` path in `MAKEPS` before opening output.
- Decision for port: mirror code condition exactly (`FILPS` path required).

3. Fixed logical-unit examples vs actual flexibility
- Manual shows specific alternate units.
- Code accepts any positive unit integer; Step 4 used 11/12/13/14 successfully.
- Decision for port: preserve flexible positive-unit behavior.

## CLI-Relevant Manual Areas Intentionally Excluded
- GUI-specific workflows and screenshots (LCMgui operations) not represented in this source-only CLI codebase.
- Non-CLI utilities except where needed to interpret shared control/output semantics.

## Porting Implications from Step 5

1. Keep namelist parsing permissive enough for real-world controls used today.
2. Preserve output contracts (`.table/.coord/.print/.corraw`) exactly before algorithmic refactoring.
3. Preserve branch semantics and diagnostics language for `DOFULL` and related stage behavior.
4. Use code/runtime behavior as final authority where the manual appears legacy or generalized.

## Step 5 Exit Criteria Check
- CLI invocation model cross-checked.
- `.RAW` and `.CONTROL` semantics cross-checked.
- Output file controls and payload semantics cross-checked.
- At least one behavior-level mismatch documented with code-truth resolution.
- Porting directives captured for next-step functional specifications.
