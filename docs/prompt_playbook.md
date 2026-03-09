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

## Operating Rules That Worked Well

1. Keep each step in a dedicated document.
2. Tie every major claim to either source lines or runtime artifacts.
3. Promote output contracts (`.table/.coord/.corraw`) as primary parity targets; treat `.ps` as weak parity.
4. Maintain README as the single entry point to all artifacts.
5. Use small, explicit prompts to advance one stage at a time.
6. When external review feedback is provided, convert it into requirement IDs plus test IDs, not prose-only edits.
7. During implementation, enforce an explicit stop condition tied to test failures.

## Suggested Next Prompt (When Implementation Starts)
- "Start Phase A from Step 8: implement `config` and `io` layers with tests required for Gate G1 only; do not scaffold unrelated modules."
