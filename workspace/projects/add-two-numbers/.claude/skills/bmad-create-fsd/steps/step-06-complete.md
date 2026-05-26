# Step 6: FSD Completion

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- 🎯 PROVIDE clear next steps
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 Present completion summary
- 📖 Update frontmatter with final workflow state
- 🚫 THIS IS THE FINAL STEP IN THIS WORKFLOW

## YOUR TASK:

Complete the FSD workflow and guide the user to test strategy creation.

## COMPLETION SEQUENCE:

### 1. Congratulate the User

Summarize what was achieved: FR count, AC count, traceability to PRD.

### 2. Update Document Frontmatter

```yaml
stepsCompleted: [1, 2, 3, 4, 5, 6]
workflowType: 'fsd'
lastStep: 6
status: 'complete'
completedAt: '{{current_date}}'
```

### 3. Next Steps Guidance

FSD complete. Invoke the `bmad-help` skill.

Recommended next step: run `bmad-create-test-strategy` after architecture is available (or in parallel if architecture exists).

Upon completion: offer to answer questions about the FSD.

## On Complete

Run: `python3 {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --key workflow.on_complete`

If the resolved `workflow.on_complete` is non-empty, follow it as the final terminal instruction before exiting.

## WORKFLOW COMPLETE

The FSD is ready for test strategy creation. Every FR-ID will trace forward to the coverage matrix and test naming convention `test_FR_NNN_*`.
