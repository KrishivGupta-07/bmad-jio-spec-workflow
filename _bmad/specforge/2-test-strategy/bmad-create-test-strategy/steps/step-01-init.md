# Step 1: Test Strategy Workflow Initialization

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- ✅ ALWAYS treat this as collaborative discovery
- 📋 YOU ARE A FACILITATOR, not a content generator
- 💬 FOCUS on initialization and setup only
- 🚪 DETECT existing workflow state and handle continuation properly
- ⚠️ ABSOLUTELY NO TIME ESTIMATES
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 Show your analysis before taking any action
- 💾 Initialize document and update frontmatter
- 📖 Set up frontmatter `stepsCompleted: [1]` before loading next step
- 🚫 FORBIDDEN to load next step until setup is complete

## YOUR TASK:

Initialize the Create Test Strategy workflow by discovering FSD and architecture prerequisites.

## INITIALIZATION SEQUENCE:

### 1. Check for Existing Workflow

Look for existing `{planning_artifacts}/test-strategy.md` (or `{output_file}` if customized):

- If exists with `stepsCompleted` in frontmatter, resume from last completed step
- If exists without frontmatter, treat as continuation candidate — confirm with user

### 2. Prerequisite Discovery

Search using v6 document discovery protocol:

**FSD (REQUIRED):**

1. `{planning_artifacts}/fsd.md`

**Architecture (REQUIRED for step 02):**

1. `{planning_artifacts}/*architecture*.md` (whole document)
2. `{planning_artifacts}/*architecture*/index.md` (sharded)

Also search: `{output_folder}/**`, `{project_knowledge}/**`, `{project-root}/docs/**`

**If no FSD found:**

> Test strategy creation requires an FSD. Please run `bmad-create-fsd` first or provide the FSD file path.

**HALT** — do not proceed without FSD.

Note architecture availability — step 02 will HALT if architecture is missing.

### 3. Fresh Workflow Setup

If no test-strategy document exists:

- Copy `../template.md` to `{output_file}` (default: `{planning_artifacts}/test-strategy.md`)
- Initialize frontmatter: `stepsCompleted: [1]`, `workflowType: 'test-strategy'`, `inputDocuments: []`
- Record discovered FSD and architecture path(s) in `inputDocuments` (do not FULL_LOAD yet)

### 4. Report to User

Report document setup and prerequisite discovery results. Ask user to confirm before continuing.

**[C] Continue to discover FSD and architecture**

HALT — wait for user to select [C].

## SUCCESS METRICS:

✅ FSD discovered or HALT with clear message
✅ Test strategy document initialized from template
✅ Frontmatter updated with `stepsCompleted: [1]`

## NEXT STEP:

After user selects [C], load `./step-02-discover-fsd-and-arch.md`.
