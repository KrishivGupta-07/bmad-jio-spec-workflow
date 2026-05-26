# Step 2: Discover FSD and Architecture

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- ✅ FULL_LOAD the entire FSD and architecture — no partial loading
- 📋 YOU ARE A FACILITATOR — summarize back for user confirmation
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 FULL_LOAD all FSD and architecture content
- 💾 Update frontmatter `inputDocuments` with loaded paths
- 📖 Update frontmatter `stepsCompleted: [1, 2]` before loading next step
- 🚫 FORBIDDEN to build coverage matrix until user confirms summary

## YOUR TASK:

Load the complete FSD and architecture documents and present a structured summary for user confirmation.

## DISCOVERY SEQUENCE:

### 1. Load FSD (FULL_LOAD)

- Read entire `{planning_artifacts}/fsd.md`
- Extract FR-ID list for later traceability
- Track path in frontmatter `inputDocuments`

### 2. Load Architecture (FULL_LOAD)

- If whole file: read entire architecture document
- If sharded: read index.md, then read EVERY shard file completely
- Track all loaded paths in frontmatter `inputDocuments`

**If no architecture found:**

> Test strategy creation requires an architecture document. Please run `bmad-create-architecture` first or provide the architecture file path.

**HALT** — do not proceed.

### 3. Summarize for Confirmation

Present to user:

- **FSD summary:** FR count, key functional areas, AC count
- **FR-ID inventory:** complete list (FR-001, FR-002, …)
- **Architecture summary:** tech stack, key modules/components, test-relevant decisions
- **Files loaded:** list of all file paths

Ask: "Does this summary accurately represent the inputs for test strategy? Any documents to add or exclude?"

### 4. Handle User Response

- If user adds documents: FULL_LOAD those too, update summary, re-confirm
- If user confirms: proceed

**[C] Continue to coverage matrix**

HALT — wait for [C].

## SUCCESS METRICS:

✅ FSD and architecture FULL_LOAD complete
✅ User confirmed input summary
✅ Complete FR-ID inventory captured
✅ `inputDocuments` updated in frontmatter

## NEXT STEP:

After [C], load `./step-03-coverage-matrix.md`.
