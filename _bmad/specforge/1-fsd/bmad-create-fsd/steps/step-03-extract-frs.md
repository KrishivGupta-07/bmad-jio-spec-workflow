# Step 3: Extract Functional Requirements

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- ✅ Collaborate with user on FR decomposition
- 📋 Assign sequential FR-IDs: FR-001, FR-002, FR-003, …
- 🚫 NO tech stack, NO test cases in FSD
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 Walk PRD user stories and features systematically
- 💾 Write to FSD template "Functional Requirements" table
- 📖 Update frontmatter `stepsCompleted: [1, 2, 3]` before loading next step
- 🚫 FORBIDDEN to write acceptance criteria in this step (step 04)

## YOUR TASK:

Decompose PRD content into functional requirements with FR-IDs.

## EXTRACTION PROCESS:

### 1. Walk PRD Content

For each user story, feature, or requirement block in the PRD:

- Identify discrete functional capabilities
- One PRD item may yield one or more FRs if it contains multiple independent capabilities
- Merge trivial sub-bullets into parent FR when they are not independently testable

### 2. Assign FR-IDs

- Format: `FR-001`, `FR-002`, … (three-digit zero-padded)
- Sequential, no gaps
- Record PRD source reference in working notes (story ID, section heading)

### 3. Populate Functional Requirements Table

Update `{output_file}` section **Functional Requirements**:

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-001 | Clear, testable requirement statement | Must / Should / Could |

**Priority guidance:**

- **Must** — MVP / release blocker
- **Should** — important but deferrable
- **Could** — nice-to-have

### 4. Populate Overview and Actors (if empty)

- **Overview:** 2–4 sentences on what the system does functionally
- **Actors:** table of roles interacting with the system

### 5. Present to User

Show the FR table. Ask for additions, splits, merges, or priority changes.

**[C] Continue to author acceptance criteria**

HALT — wait for [C].

## SUCCESS METRICS:

✅ Every PRD story/feature mapped to at least one FR
✅ FR-IDs sequential and unique
✅ No tech stack language in requirements

## NEXT STEP:

After [C], load `./step-04-author-acs.md`.
