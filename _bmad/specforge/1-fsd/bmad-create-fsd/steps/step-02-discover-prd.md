# Step 2: Discover and Confirm PRD

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- ✅ FULL_LOAD the entire PRD — no offset/limit, no summarization-only loading
- 📋 YOU ARE A FACILITATOR — summarize back for user confirmation
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 FULL_LOAD all PRD content (whole file or all shards)
- 💾 Update frontmatter `inputDocuments` with loaded PRD paths
- 📖 Update frontmatter `stepsCompleted: [1, 2]` before loading next step
- 🚫 FORBIDDEN to extract FRs until user confirms PRD summary

## YOUR TASK:

Load the complete PRD and present a structured summary for user confirmation.

## DISCOVERY SEQUENCE:

### 1. Load PRD (FULL_LOAD)

- If whole PRD file: read entire file
- If sharded: read index.md, then read EVERY shard file completely
- Track all loaded paths in frontmatter `inputDocuments`

### 2. Summarize for Confirmation

Present to user:

- **Product scope** (1–3 sentences)
- **Key user stories / features** (bulleted list)
- **Constraints or assumptions** from PRD
- **Files loaded:** list of PRD file paths

Ask: "Does this PRD summary accurately represent what we're specifying? Any documents to add or exclude?"

### 3. Handle User Response

- If user adds documents: FULL_LOAD those too, update summary, re-confirm
- If user confirms: proceed

**[C] Continue to extract functional requirements**

HALT — wait for [C].

## SUCCESS METRICS:

✅ PRD FULL_LOAD complete
✅ User confirmed PRD summary
✅ `inputDocuments` updated in frontmatter

## NEXT STEP:

After [C], load `./step-03-extract-frs.md`.
