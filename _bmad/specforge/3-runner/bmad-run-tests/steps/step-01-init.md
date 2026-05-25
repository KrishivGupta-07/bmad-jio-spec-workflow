# Step 1: Run Tests Initialization

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER edit src/, tests, or docs
- 📖 CRITICAL: Read complete step file before acting
- ✅ Load test-strategy and extract primary runner command
- ✅ Ensure `{specforge_artifacts}/` directory exists
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 FULL_LOAD test-strategy.md
- 💾 Compute next iteration number from prior last-run.json
- 🚫 FORBIDDEN to execute tests in this step

## YOUR TASK:

Initialize the run-tests workflow: load test strategy, extract runner command, prepare iteration counter.

## INITIALIZATION SEQUENCE:

### 1. Load Test Strategy (FULL_LOAD)

Search:

1. `{planning_artifacts}/test-strategy.md`

**If not found:**

> Run tests requires a test strategy. Please run `bmad-create-test-strategy` first or provide the test-strategy file path.

**HALT** — do not proceed.

### 2. Extract Primary Runner Command

From test-strategy.md section **Primary Runner Command**, extract the single executable shell line.

**If missing or empty:**

> Test strategy is missing Primary Runner Command. Complete `bmad-create-test-strategy` step-04 first.

**HALT** — do not proceed.

Store as `{{primary_runner_command}}`.

### 3. Ensure Output Directory

Create `{specforge_artifacts}/` if it does not exist.

### 4. Compute Iteration Number

Read `{specforge_artifacts}/last-run.json` if present:

- If exists: `{{next_iteration}}` = prior `iteration` + 1
- If absent: `{{next_iteration}}` = 1

Report to user:

- Primary runner command to execute
- Current iteration number (`{{next_iteration}}` of 5 max)
- Prior run summary if last-run.json existed

### 5. Confirm Execution

**[C] Continue to execute tests**

HALT — wait for [C].

## SUCCESS METRICS:

✅ Test strategy loaded
✅ Primary runner command extracted
✅ specforge_artifacts directory ready
✅ Iteration number computed

## NEXT STEP:

After [C], load `./step-02-execute.md`.
