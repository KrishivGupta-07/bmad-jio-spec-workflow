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

## Environment Setup

<!-- Commands run ONCE per environment, before any test iteration. One executable shell command per line. Idempotent where possible. -->

```
```

## Runner Command

<!-- Single executable shell line — runs EVERY iteration from project root. MUST include structured-output flag with path under .specforge/ -->

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
