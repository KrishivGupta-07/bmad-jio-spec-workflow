# Step 1: FSD Workflow Initialization

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- 🔄 CRITICAL: When loading next step with 'C', ensure the entire file is read and understood before proceeding
- ✅ ALWAYS treat this as collaborative discovery
- 📋 YOU ARE A FACILITATOR, not a content generator
- 💬 FOCUS on initialization and setup only — don't look ahead to future steps
- 🚪 DETECT existing workflow state and handle continuation properly
- ⚠️ ABSOLUTELY NO TIME ESTIMATES
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 Show your analysis before taking any action
- 💾 Initialize document and update frontmatter
- 📖 Set up frontmatter `stepsCompleted: [1]` before loading next step
- 🚫 FORBIDDEN to load next step until setup is complete

## YOUR TASK:

Initialize the Create FSD workflow by discovering the PRD, halting if missing, and setting up the FSD document.

## INITIALIZATION SEQUENCE:

### 1. Check for Existing Workflow

Look for existing `{planning_artifacts}/fsd.md` (or `{output_file}` if customized):

- If exists with `stepsCompleted` in frontmatter, resume from last completed step
- If exists without frontmatter, treat as continuation candidate — confirm with user

### 2. PRD Discovery (REQUIRED)

Search using v6 document discovery protocol:

1. `{planning_artifacts}/*prd*.md` (whole document)
2. `{planning_artifacts}/*prd*/index.md` (sharded — load index first, then ALL shard files)

Also search: `{output_folder}/**`, `{project_knowledge}/**`, `{project-root}/docs/**`

**If no PRD found:**

> FSD creation requires a PRD. Please run the `bmad-prd` workflow first or provide the PRD file path.

**HALT** — do not proceed.

### 3. Fresh Workflow Setup

If no FSD document exists:

- Copy `../template.md` to `{output_file}` (default: `{planning_artifacts}/fsd.md`)
- Initialize frontmatter: `stepsCompleted: [1]`, `workflowType: 'fsd'`, `inputDocuments: []`
- Record discovered PRD path(s) in `inputDocuments` (do not FULL_LOAD yet — step 02 handles that)

### 4. Report to User

Report document setup and PRD discovery results. Ask user to confirm before continuing.

**[C] Continue to PRD discovery and confirmation**

HALT — wait for user to select [C].

## SUCCESS METRICS:

✅ PRD discovered or HALT with clear message
✅ FSD document initialized from template
✅ Frontmatter updated with `stepsCompleted: [1]`

## NEXT STEP:

After user selects [C], load `./step-02-discover-prd.md`.
