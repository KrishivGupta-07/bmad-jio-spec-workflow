# Step 2: Execute Tests

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER edit src/, tests, or docs
- 📖 CRITICAL: Read complete step file before acting
- ✅ Execute from project root (`{project-root}`)
- ✅ Capture stdout, stderr, and exit code completely
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in `{communication_language}`

## YOUR TASK:

Run the primary runner command and capture all output.

## EXECUTION:

### 1. Run Command

From `{project-root}`, execute the extracted primary runner command using the shell:

```bash
cd {project-root} && {primary_runner_command}
```

Use appropriate permissions for test execution (network if integration/e2e tests require it).

### 2. Capture Output

Store:

- `{{stdout}}` — full standard output
- `{{stderr}}` — full standard error
- `{{exit_code}}` — process exit code

### 3. Report Execution Status

Report to user: command run, exit code, brief output summary (first/last lines if voluminous).

Do NOT parse failures yet — step-03 handles parsing.

## NEXT STEP:

Load `./step-03-parse-failures.md`.
