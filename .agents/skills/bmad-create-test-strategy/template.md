---
stepsCompleted: []
inputDocuments: []
workflowType: 'test-strategy'
project_name: '{{project_name}}'
user_name: '{{user_name}}'
date: '{{date}}'
---

# Test Strategy

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through coverage and runner selection together._

## Frameworks and Runner

| Level | Framework | Command |
| --- | --- | --- |
| unit | | |
| integration | | |
| e2e | | |

## Primary Runner Command

<!-- Single executable shell line — runner agent executes this verbatim from project root -->

```
```

## Directory Layout

<!-- Test directory structure mirroring src/ -->

```
tests/
  unit/
  integration/
  e2e/
```

## Coverage Targets

<!-- Per module — specific and modest -->

| Module / Area | Target | Notes |
| --- | --- | --- |
| | | |

## Risk-Based Priorities

<!-- At least one FR with reasoning -->

| FR-ID | Risk | Rationale | Priority |
| --- | --- | --- | --- |
| FR-001 | | | High / Medium / Low |

## Fixtures and Test Data

<!-- Shared fixtures, factories, seed data strategy -->

## Explicitly Not Tested

<!-- Out of scope for automated testing with rationale -->

## Coverage Matrix

<!-- EVERY FR-ID from FSD must appear -->

| FR-ID | Test Level | Notes |
| --- | --- | --- |
| FR-001 | unit / integration / e2e | |

## Test Naming Convention (REQUIRED for SpecForge)

<!-- All automated tests MUST use test_FR_NNN_* naming so bmad-run-tests can extract fr_id for dev handoff. QA agents (bmad-qa-generate-e2e-tests) must follow this pattern when generating tests. -->
