# Step 6: Test Strategy Completion

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

Complete the test strategy workflow and guide the user to test execution.

## COMPLETION SEQUENCE:

### 1. Congratulate the User

Summarize what was achieved: FR coverage count, test levels assigned, primary runner command.

### 2. Update Document Frontmatter

```yaml
stepsCompleted: [1, 2, 3, 4, 5, 6]
workflowType: 'test-strategy'
lastStep: 6
status: 'complete'
completedAt: '{{current_date}}'
```

### 3. Next Steps Guidance

Test strategy complete. Invoke the `bmad-help` skill.

Recommended next step: invoke `bmad-run-tests` (or talk to Rex via `bmad-agent-runner`) to execute the primary runner command.

Upon completion: offer to answer questions about the test strategy.

## On Complete

Run: `python3 {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --key workflow.on_complete`

If the resolved `workflow.on_complete` is non-empty, follow it as the final terminal instruction before exiting.

## WORKFLOW COMPLETE

The test strategy is ready for execution. The runner agent will read the Primary Runner Command verbatim and write results to `{specforge_artifacts}/last-run.json`.
