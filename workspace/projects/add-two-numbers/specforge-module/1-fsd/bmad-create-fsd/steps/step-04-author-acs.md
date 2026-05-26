# Step 4: Author Acceptance Criteria

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER generate content without user input
- 📖 CRITICAL: ALWAYS read the complete step file before taking any action
- ✅ Given/When/Then format for EVERY acceptance criterion
- 🚫 ONE scenario per AC — no compound scenarios
- 🚫 NO test cases, NO test code, NO execution steps
- ✅ YOU MUST ALWAYS SPEAK OUTPUT in `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 Process FRs in order (FR-001, FR-002, …)
- 💾 Write to FSD "Acceptance Criteria" section grouped by FR-ID
- 📖 Update frontmatter `stepsCompleted: [1, 2, 3, 4]` before loading next step

## YOUR TASK:

For each FR, write Given/When/Then acceptance criteria.

## AUTHORING PROCESS:

### 1. For Each FR-ID

Create a subsection:

```markdown
### FR-001: {requirement title}

**AC-001-01**

- **Given** {precondition — system state or context}
- **When** {user action or system event}
- **Then** {observable outcome}

**AC-001-02**
...
```

### 2. AC ID Convention

- Format: `AC-{FR-num}-{seq}` e.g. `AC-001-01`, `AC-001-02`
- At least one AC per FR
- Split compound conditions into separate ACs

### 3. Populate User Flows

Add narrative user flows covering primary paths referenced by ACs (no tech detail).

### 4. Populate Out of Scope

Extract explicit exclusions from PRD; add any user-confirmed exclusions.

### 5. Populate Open Questions

| ID | Question | Status |
| --- | --- | --- |
| OQ-001 | {question needing product decision} | Open |

Resolve questions with user during this step when possible. Mark **Resolved** when answered.

### 6. Present to User

Show AC summary per FR. Ask for revisions.

**[C] Continue to validation**

HALT — wait for [C].

## SUCCESS METRICS:

✅ Every FR has ≥1 Given/When/Then AC
✅ No compound scenarios
✅ Open Questions section populated

## NEXT STEP:

After [C], load `./step-05-validate.md`.
