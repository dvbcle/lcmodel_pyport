# PS Visual Inspection Guide

## Purpose
Provide a repeatable way to visually compare Python-generated `.ps` output with Fortran reference `.ps` output for the external dataset fixtures.

## Generate Python PS Outputs
Run:

```powershell
python -m pytest tests/test_evidence_external_dataset.py -q
```

This updates/generated files under:
- `tests/.tmp/generated_external_cases/case02_trace_full/out_trace_full.ps`
- `tests/.tmp/generated_external_cases/case03_trace_prelim_only/out_trace_prelim.ps`

## Reference Fortran PS Outputs
- `artifacts/step4_exec/case02_trace_full/out_trace_full.ps`
- `artifacts/step4_exec/case03_trace_prelim_only/out_trace_prelim.ps`

## What To Compare Visually
1. Overall page layout and plotted trace shape trends.
2. Presence/absence of branch marker:
   - prelim-only (`DOFULL=F`) should show `CRUDE MODEL`.
   - full mode (`DOFULL=T`) should not show `CRUDE MODEL`.
3. Relative scaling/position of traces (data/fit/background) and axis framing.

## Machine-Checked Companion Evidence
The evidence run also records PS branch-marker parity in:
- `tests/.tmp/evidence_external_dataset.json`
- stage: `output_numeric_regression_stage`
- key: `ps_crude_marker_match` (for both case02 and case03)
