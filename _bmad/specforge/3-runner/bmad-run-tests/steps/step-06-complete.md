# Step 6: Run Tests Completion (Green Path Only)

## MANDATORY EXECUTION RULES (READ FIRST):

- 📖 CRITICAL: Read complete step file before acting
- ✅ Run `../checklist.md` green-build gate
- 🚫 THIS STEP IS ONLY FOR GREEN BUILDS

## YOUR TASK:

Validate green build and complete workflow.

## COMPLETION SEQUENCE:

### 1. Run Green Build Checklist

Execute `../checklist.md` gate criteria. All must pass (they should if routed here correctly).

### 2. Congratulate User

Report: all tests passed, iteration number, total test count.

### 3. Completion Message

Run tests workflow complete. Invoke the `bmad-help` skill.

Upon completion: offer to answer questions about the test run or suggest next steps (code review, sprint status, etc.).

## On Complete

Run: `python3 {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --key workflow.on_complete`

If non-empty, follow as final instruction.

## WORKFLOW COMPLETE

Green build confirmed. `{specforge_artifacts}/last-run.json` records the successful run.
