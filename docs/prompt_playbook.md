# Prompt Playbook: LCModel PyPort Session Record

## Purpose
Capture the prompt patterns, decisions, and outcomes from this chat so future sessions can resume work quickly and consistently.

## Session Outcome Summary
- Completed documentation pipeline through Steps 1-8.
- Established code-as-truth rule when manual/comments conflict.
- Built execution-backed understanding using LCModel Windows binary and test fixtures.
- Produced architecture-driving functional and verification specifications.
- Added module-to-test traceability and numerical unit-test strategy.
- Incorporated third-party review feedback into specs:
  - explicit index conversion safeguards,
  - explicit typing/schema constraints,
  - Pythonic error-handling translation requirements.

## High-Value Prompt Patterns Used

1. Stage progression prompts
- Example: "Proceed to step X."
- Effect: kept work scoped, auditable, and checkpointed by document.

2. Truth-priority prompts
- Example: "Where comments and code inferred mismatch occurs, use the code as the truth."
- Effect: avoided manual/comment drift and anchored specs to executable behavior.

3. Verification-depth prompts
- Example: "Can the verification spec map intermediate source of truth data... add specific unit tests."
- Effect: upgraded verification from output-only checks to stage checkpoints + numeric kernel unit tests.

4. Architecture handoff prompts
- Example: "Can functional specs be more detailed to guide architecture?"
- Effect: converted requirements into component/data/interface/state contracts and direct module mapping.

5. Repo hygiene prompts
- Example: "Commit and push all changes."
- Effect: preserved clear milestone history and synchronized remote state.

6. External review integration prompts
- Example: "Use this 3rd-party feedback to update relevant step documents."
- Effect: transformed high-level concerns into concrete requirements and test IDs.

7. Autonomous execution boundary prompts
- Example: "Proceed autonomously, but stop at first test failure you cannot fix."
- Effect: establishes safe execution policy for implementation phases.

## Chronological Prompt Log (Condensed)

1. Goal definition
- User asked for code investigation and design specs suitable for Python porting.
- Output: stepwise plan and docs-first workflow.

2. Step 1 baseline constraints
- User clarified source-only Fortran (`.f` + `.inc`, no build scripts).
- Output: baseline docs aligned to source-only reality.

3. Step 1 quality gate
- User requested double-check against source comments before proceeding.
- Output: corrected baseline references and strengthened code/comment reconciliation.

4. Git initialization and branch conventions
- User requested repo creation and `master -> main` convention.
- Output: repo configured and branch standardized.

5. Plan clarification and reordering
- User requested repeating and reordering plan so Python architecture is last.
- Output: reordered plan adopted and documented.

6. LCModel understanding alignment
- User requested current understanding and spec updates based on that understanding.
- Output: domain intent reflected in source baseline and flow docs.

7. Documentation discoverability
- User requested docs reachable from base README.
- Output: README documentation index maintained and expanded.

8. Publish and remote workflow
- User requested commit/push and GitHub remote setup, including GH login/repo creation.
- Output: remote configured and synced.

9. Repository restructuring
- User requested Fortran source under `lcmodel_fortran/`.
- Output: structure adjusted to prepare root for new Python port.

10. AI-assisted disclosure
- User requested README clarification that specs/porting are AI-assisted.
- Output: workflow disclosure added.

11. Step 2 validation loop
- User requested step-2 doc cross-check against source/comments and `.inc` comments.
- Output: docs refined with code-first tie-break and include-comment integration.

12. Step 4 execution analysis
- User requested progression.
- Output: binary/test data runs produced; full vs prelim behavior characterized and documented.

13. TDD direction
- User asked if execution artifacts can drive TDD.
- Output: structured TDD approach defined; then converted into reusable harness plan.

14. Step 5 manual cross-check
- User requested progression.
- Output: CLI manual vs code/runtime matrix with explicit divergence handling.

15. Step 6 expansion
- User requested more detail to guide architecture.
- Output: architecture-driving functional spec with component/data/interface/state contracts.

16. Step 7 deepening
- User requested intermediate source-of-truth mapping and numerical unit tests.
- Output: checkpoint-based verification model + numerical kernel unit-test catalog.

17. Step 8 traceability enhancement
- User requested module-to-test-ID mapping.
- Output: architecture doc now includes module/test matrix and implementation gates.

18. Finalization
- User requested commit and push.
- Output: Steps 5-8 and README updates committed and pushed.

19. External gap remediation
- User provided third-party feedback on index logic, implicit typing, and error handling.
- Output: Step 6/7/8 updated with explicit requirements (`RQ-015..017`), new unit tests (`VT-U-I/*`, `VT-U-T/*`, `VT-U-E/*`), and architecture safety controls.

20. Session memory request
- User requested a prompt playbook for future reference.
- Output: this document created and linked from README.

21. Execution policy for implementation
- User requested autonomous implementation with early-stop rule on unfixable failing tests and mapping of test outcomes to Fortran code blocks.
- Output: implementation run policy established.

22. Prompt-playbook refresh + autonomous implementation start
- User requested prompt playbook update, commit/push, then autonomous implementation with fail-fast constraints.
- Output: playbook update committed/pushed; implementation started with Gate G1 passing tests and traceability anchors.

23. Gate G2 expansion via checkpoint-driven tests
- User requested autonomous continuation.
- Output: implemented basis/preliminary parsers + checkpoints and tests for `VT-I-003`, `VT-I-004`, `VT-S-001`, `VT-S-002`; all tests passed.

24. Gate G3 numerical kernel bootstrap
- User requested continued progression.
- Output: added numerical and indexing kernels with Suite E/F tests.
- First early failure encountered/fixed in `VT-U-N-010` (inflection test signal threshold interaction), then full suite passed.

25. Gate G4 baseline checkpoint extraction
- User requested continued fail-safe progression.
- Output: added `fullfit_stage` reference checkpoint extraction (`CP-FULL-001`) and tests for `VT-I-005`/`VT-N-001`; suite remained green.

26. External-dataset evidence run request
- User asked how to prove parity for the external test dataset in one run and requested implementation.
- Output: added `VT-E2E-EVID-001` evidence test and JSON/JUnit artifact generation with per-stage `pass/fail/not_implemented` statuses.

27. Next-gate continuation after evidence
- User requested proceeding immediately to next gate.
- Output: started Gate G5 with initial report writers (`table/coord/corraw`) plus contract tests.
- Encountered environment-specific tmp-directory permission issue; fixed by switching tests to repo-local `tests/.tmp` paths.

28. Commit-point documentation requirement
- User requested updating the prompt playbook at each commit point.
- Output: playbook now explicitly updated before every milestone commit.

29. External-dataset evidence hardening (G5 transition)
- User requested autonomous continuation.
- Output: replaced evidence `not_implemented` placeholders with executable stages:
  - Python output-stage generation (`python_pipeline_e2e_generation`)
  - generated-vs-reference numeric regression (`output_numeric_regression_stage`)
- Added vector/scalar comparisons with tolerance profile and machine-readable stage checks.

30. G5 output-stage expansion
- User requested autonomous progression.
- Output: added minimal output-stage orchestrator and `.print` writer, plus regression tests for case02/case03 generation paths.
- Result: full test suite passed after expansion.

31. G6 reference-mode orchestration start
- User requested autonomous continuation.
- Output: added case-level orchestrator with explicit stage sequencing and `DOFULL` branch behavior (`fullfit_loaded` only for full mode).
- Integrated evidence generation through orchestration path instead of direct output-stage calls.
- Result: suite remained green after orchestration integration.

32. Evidence branch-coverage expansion
- User requested autonomous continuation.
- Output: expanded `VT-E2E-EVID-001` generated-vs-reference regression checks from full-case only to both full (`case02`) and prelim-only (`case03`) branches.
- Result: evidence now validates branch-sensitive parity in one run.

33. G7 robustness hardening start
- User requested autonomous continuation.
- Output: enforced strict integer parsing for control integer fields (prevents silent float->int coercion) and added explicit error-path tests for missing control/reference files.
- Result: robustness tests added without breaking existing parity coverage.

34. PS visual-parity objective implementation
- User requested continuing toward a visually inspectable Python `out.ps` parity target.
- Output:
  - added `report/ps_writer.py`,
  - wired `.ps` generation into output-stage flow,
  - added PS contract/branch tests,
  - extended evidence checks with `ps_crude_marker_match` for both full/prelim branches,
  - added `docs/ps_visual_inspection.md` with explicit comparison paths.
- Result: generated Python `.ps` artifacts are now available for direct visual inspection.

35. PS-input intermediate checkpoint parity
- User clarified that if visual PS parity fails, intermediate PS-generating data should be checked first.
- Output:
  - added `CP-PS-INPUT-001` checkpoints for full and prelim external cases,
  - added dedicated PS-input checkpoint parity tests,
  - integrated `ps_input_parity_stage` into `VT-E2E-EVID-001` evidence run.
- Result: evidence report now shows an explicit pass/fail stage for PS-input parity before visual interpretation.

## Reusable Prompt Templates

Use these directly in future sessions.

1. Continue stage
- "Proceed to step <N> and keep outputs in docs with traceable anchors."

2. Accuracy guardrail
- "Double-check this doc against source comments and runtime artifacts before continuing."

3. Conflict policy
- "If docs/comments and code behavior differ, use executable behavior as truth and record divergence."

4. Verification hardening
- "Add intermediate checkpoints after each stage and map each checkpoint to test IDs."

5. Numerical rigor
- "Add module-level unit tests for numerical kernels (FFT, phase/shift, constrained solver, regularization)."

6. Architecture handoff
- "Map each functional component and module to explicit test IDs and implementation gates."

7. Publishing
- "Stage relevant files only, commit with milestone message, and push to origin main."

8. External review incorporation
- "Incorporate this review feedback into Step 6/7/8 as requirements, tests, and architecture controls."

9. Autonomous with fail-fast constraint
- "Proceed autonomously, but stop at the first unfixable test failure and report pass/fail mapped to Fortran blocks."

10. Autonomous gate expansion
- "Proceed to Gate G2/G3 incrementally; after each increment run tests and stop if failures are unfixable."

11. Commit-point playbook update
- "Before each commit, update `docs/prompt_playbook.md` with latest prompts, decisions, failures/fixes, and outcomes."

12. Evidence closure prompt
- "Promote `not_implemented` evidence stages to executable checks before advancing to the next gate."

13. Orchestration-first gate advance
- "Introduce gate-level orchestrator paths in reference mode first, then replace reference-backed state with true solver-generated state."

14. Evidence branch completeness
- "Ensure evidence runs validate both `DOFULL=T` and `DOFULL=F` branches before tightening tolerances."

15. Type safety hardening
- "Before expanding solver logic, remove permissive coercions (especially integer controls) and lock behavior with negative-path tests."

16. Visual parity progression
- "Prioritize generating inspectable `.ps` artifacts and branch-marker parity checks before attempting byte-level PS similarity."

17. PS fallback protocol
- "If PS visual parity is questionable, validate PS-input checkpoints (`ppm_axis`, `phased_data`, `fit`, `background`, branch markers) before modifying PS rendering."

## Operating Rules That Worked Well

1. Keep each step in a dedicated document.
2. Tie every major claim to either source lines or runtime artifacts.
3. Promote output contracts (`.table/.coord/.corraw`) as primary parity targets; treat `.ps` as weak parity.
4. Maintain README as the single entry point to all artifacts.
5. Use small, explicit prompts to advance one stage at a time.
6. When external review feedback is provided, convert it into requirement IDs plus test IDs, not prose-only edits.
7. During implementation, enforce an explicit stop condition tied to test failures.
8. For early numerical failures, patch only the failing kernel/test pair first, rerun, and avoid expanding scope until green.
9. Update `docs/prompt_playbook.md` before every commit so project memory stays synchronized with git history.
10. Prefer converting stage placeholders in evidence reports into executable comparisons as soon as parser/writer primitives exist.
11. For Gate G6 transitions, assert branch behavior (`DOFULL`) and stage-presence flags explicitly before tightening numeric parity.
12. Expand evidence scope by branch first, then by stricter numeric tolerances.
13. Add failure-path tests alongside new orchestration/writer code so CI catches missing-file and schema regressions early.
14. Keep `.ps` as weak contract in automated checks while enabling manual visual comparison as a first-class parity artifact.
15. Promote manual-debug fallback paths (like PS-input checkpoints) into automated evidence stages as soon as defined.

## Suggested Next Prompt
- "Continue G6/G7: replace parsed-reference-backed outputs with true computed stage-state incrementally, while keeping PS-input checkpoint parity and evidence stages green."
