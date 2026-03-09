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
5. [Step 7: Reusable Test Harness Outline](docs/step7_test_harness_tdd_outline.md)

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
- Completed: Steps 1-4
- In progress: Step 5 (CLI-manual cross-check)
- Pending: Steps 6, 7, 8

## Repository Notes
- This repository currently contains source and analysis docs.
- Build scripts are not included; the codebase is source-only in its current form.

