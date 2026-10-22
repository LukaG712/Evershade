---
sessionId: session-261022-155542-tvec
---

# Requirements

## Overview & Goals

Transform Evershade into a Factory-inspired autonomous software engineering ecosystem. The core capability is a **mission control system** that can coordinate multiple agents to plan, execute, validate, and deliver software engineering tasks — from natural language requests to verified results.

The ecosystem already has substantial infrastructure: 10 services, a workflow engine, workstations, model routing (Shrewd), code execution (Slinker), web scraping (Trapper), persistent storage (Gobber), and a React dashboard (Slammer). This plan **extends** that infrastructure rather than replacing it.

## Scope

### In Scope
- **Mission control layer**: First-class mission entities with milestones, planning, parallel worker execution, and independent validation
- **Extended workflow engine**: New step types (PLANNER, WORKER, VALIDATOR), milestone grouping, parallel execution support
- **Mission execution engine**: Orchestrator that coordinates child workflows per milestone, handles handoffs, aggregates results
- **Model routing integration**: Use Shrewd for planning (high-quality model), coding (efficient model), and review (skeptic model)
- **Slammer dashboard**: New Missions page showing active missions, milestone progress, execution logs, validation results
- **Repository intelligence**: Lightweight project analysis before missions start
- **Automated code review**: Validation pipeline for agent-generated changes
- **Automation engine**: Event-driven triggers (GitHub webhooks, schedules) that create missions
- **Persistence**: Mission state survives restarts with SQLite storage
- **Security**: Autonomy levels, approval gates, secret redaction

### Out of Scope
- New microservices (all changes go in existing Greenie, Slinker, Shrewd, Slammer)
- User authentication system (deferred per existing roadmap)
- Virtual machine-based workstations (container driver exists, VM driver deferred)
- Cross-repository dependency management beyond the Evershade ecosystem
- Cloud deployment (local-first, self-hosted only)

## User Stories

1. As a developer, I want to submit a natural-language task and have it automatically planned, executed, and validated so I can ship features with minimal intervention.
2. As a developer, I want to monitor active missions in real time so I can see progress, intervene when needed, and approve sensitive operations.
3. As a developer, I want missions to resume after restarts so interrupted work is not lost.
4. As a developer, I want to configure autonomy levels so I control how much agents can do without approval.
5. As a developer, I want to review changes before they're merged so I maintain quality control.
6. As a developer, I want GitHub issues to automatically create missions so recurring work happens without manual triggers.

## Acceptance Criteria

- A mission can be created from a natural-language description
- The mission is decomposed into milestones with features, success criteria, and validation contracts
- Worker tasks execute in parallel within a milestone
- Independent validators check completed work before the next milestone starts
- Validation failures create fix features that workers implement
- Mission state persists across application restarts
- The Slammer dashboard shows real-time mission progress
- Failed missions can be resumed from the last checkpoint
- Sensitive operations require human approval
- Model selection is configurable per role (planner, worker, validator)

# Technical Design

## Current Implementation

**Greenie** (`Greenie/hub/`): Central API with 50+ route modules under `hub/api/`. Workflow engine in `hub/workflow/` with models (`WorkflowDefinition`, `WorkflowRun`, `WorkflowStep`), storage (SQLite), executor, and triggers. Step types: AGENT, SERVICE, APPROVAL, CONDITION, NOTIFY, WORKSTATION.

**Slinker** (`Slinker/junie_adapter/`): Code execution engine with Junie CLI integration, worktree isolation, worker executor, and a pluggable runner interface. Tasks are submitted via API and executed in isolated Git worktrees.

**Shrewd** (`Shrewd/shrewd/`): LLM abstraction with model routing, cost tracking, privacy classification. Providers: OpenAI, Anthropic, Google, Ollama. Model registry with context windows and private/public classification.

**Slammer** (`Slammer/src/`): React dashboard with components for Workflows, Workstations, Metrics, Logs, Plugins, Terminal. Integrates with Greenie API.

**Gobber**: Persistent storage with SQLite, knowledge graph, Obsidian vault integration.

**Existing workflow engine** supports sequential execution with dependencies, approval gates, and triggers — but lacks milestone grouping, parallel worker execution, independent validation, and mission-level orchestration.

## Key Decisions

1. **Missions as first-class entities**: A mission is a top-level entity that creates child workflows for each milestone. The mission controller coordinates between workflows, handles handoffs, and aggregates results. This provides isolation between milestones while reusing the workflow engine.

2. **Three-role architecture**: Following Factory's pattern — orchestrator (planning LLM), workers (execution via Slinker), validators (independent review). Each role can use a different model via Shrewd routing.

3. **Hybrid workflow extension**: New step types (PLANNER, WORKER, VALIDATOR, MILESTONE) added to the existing workflow engine. The executor gains parallel execution support and milestone-aware scheduling.

4. **SQLite persistence**: Mission state stored in Greenie's SQLite database alongside existing workflow data. No new database introduced.

5. **Slammer for UI**: New Missions component added to the existing Slammer dashboard, reusing the Greenie API integration pattern.

## Proposed Changes

### 1. Mission Data Models (`Greenie/hub/mission/models.py`)

New entities:
- **Mission**: Top-level entity with ID, description, target repository, status, assigned model preferences, milestones, validation contract, artifacts, timestamps.
- **MissionMilestone**: Grouped set of features with success criteria. Status: PLANNING, EXECUTING, VALIDATING, COMPLETED, FAILED.
- **MissionFeature**: Individual unit of work within a milestone. Has role (worker/validator), assigned model, status, output, dependencies.
- **ValidationContract**: Testable behavioral assertions defining completion. Created before any code is written.
- **ValidationResult**: Independent review findings with severity, file/line, explanation, suggested correction.
- **MissionCheckpoint**: Snapshot of mission state at a point in time for recovery.

### 2. Mission Storage (`Greenie/hub/mission/storage.py`)

SQLite-based storage with tables for missions, milestones, features, validation contracts, results, and checkpoints. Integration with existing `hub/workflow/storage.py` patterns.

### 3. Mission Controller (`Greenie/hub/mission/controller.py`)

Coordinates mission lifecycle:
- **Create mission**: Parse natural-language request, create mission entity, start planning milestone.
- **Planning phase**: Invoke orchestrator (via Shrewd with a high-quality model) to decompose the goal into milestones, features, and a validation contract.
- **Execution phase**: For each milestone, create a child workflow with worker steps (parallel) and a validator step. Workers use Slinker for code tasks. Validators run tests, linting, and AI review.
- **Validation phase**: Independent validator checks results against the validation contract. Failures create fix features.
- **Completion**: Aggregate results, produce summary, create branch/PR if requested.
- **Recovery**: Load last checkpoint on restart, resume from that point.

### 4. Extended Workflow Engine

Changes to `Greenie/hub/workflow/`:
- New `StepType` values: PLANNER, WORKER, VALIDATOR, MILESTONE
- `WorkflowStep` gains `role` field (orchestrator/worker/validator) and `model_override` field
- `WorkflowExecutor` gains parallel execution support (concurrent step execution for independent steps within a milestone)
- Milestone-aware scheduling: all workers in a milestone must complete before validator runs

### 5. Mission API (`Greenie/hub/api/missions.py`)

REST endpoints:
- `POST /api/missions` — Create a mission
- `GET /api/missions` — List missions (filterable by status)
- `GET /api/missions/{id}` — Mission detail with milestones, features, logs
- `POST /api/missions/{id}/cancel` — Cancel a mission
- `POST /api/missions/{id}/resume` — Resume from checkpoint
- `POST /api/missions/{id}/approve` — Approve a pending approval gate
- `GET /api/missions/{id}/logs` — Execution logs (SSE streaming)
- `GET /api/missions/{id}/diff` — Changed files and diffs
- `GET /api/missions/{id}/validation` — Validation results

### 6. Repository Intelligence (`Greenie/hub/mission/repo_intelligence.py`)

Before mission planning, analyze the target repository:
- Directory structure and entry points
- Build/test commands from existing config files
- Dependencies and framework detection
- Existing conventions (from AGENTS.md, README, CONTRIBUTING)
- Relevant files for the mission scope

Output stored as mission context, not sent to models repeatedly.

### 7. Automated Review (`Greenie/hub/mission/auto_review.py`)

Extends existing `hub/auto_review.py`:
- Deterministic checks: build, test, lint, type check
- AI-assisted review: security, correctness, completeness, edge cases
- Configurable severity levels and merge policies
- Structured findings with file/line, explanation, suggested correction

### 8. Automation Engine (`Greenie/hub/mission/automation.py`)

Event-driven mission creation:
- GitHub webhook handler (issues, PRs, CI failures)
- Schedule-based triggers (extends existing workflow triggers)
- Idempotency: duplicate event protection
- Rate limiting
- Action registry: analyze issue, create plan, review PR, update docs

### 9. Slammer Missions Dashboard (`Slammer/src/components/Missions.tsx`)

New React component:
- Mission list view (active, queued, completed, failed)
- Mission detail view with milestone progress bars
- Feature-level status and assignment
- Execution log viewer (SSE-connected)
- Diff viewer for changed files
- Validation results panel
- Approve/reject controls
- Cancel/resume buttons

### 10. Model Routing Integration

Mission roles map to model preferences via Shrewd:
- **Orchestrator**: High-quality model (e.g., gpt-4o, claude-3-sonnet) for planning and judgment
- **Worker**: Efficient model (e.g., gpt-4o-mini, local model) for implementation
- **Validator**: Thorough model (e.g., claude-3-sonnet) for review
- Configurable per mission and per role
- Privacy enforcement: local-only models when `require_private=true`

## Architecture Diagram

``` mermaid
graph LR
  subgraph User
    U[User] --> |Natural Language| S[Slammer Dashboard]
    U --> |GitHub Webhook| G[Greenie API]
  end

  subgraph Greenie
    S --> |API| MA[Mission API]
    MA --> MC[Mission Controller]
    MC --> |Planning| SH[Shrewd Routing]
    MC --> |Create Workflows| WE[Workflow Engine]
    MC --> |Checkpoints| DB[(SQLite)]
    WE --> |Code Tasks| SL[Slinker]
    WE --> |Validation| AR[Auto Review]
    WE --> |LLM Review| SH
    AR --> |Deterministic| SL
    SH --> |Model Selection| MC
    RI[Repo Intelligence] --> |Context| MC
  end

  subgraph Execution
    SL --> |Junie CLI| WT[Worktrees]
    SH --> |OpenAI/Anthropic/Ollama| M[Models]
  end

  DB --> |Persistence| MC
```

## File Structure

```
Greenie/hub/mission/
  __init__.py
  models.py           # Mission, Milestone, Feature, ValidationContract, etc.
  storage.py          # SQLite persistence
  controller.py       # Mission lifecycle coordinator
  planner.py          # Orchestrator logic (planning via LLM)
  repo_intelligence.py # Repository analysis before missions
  automation.py       # Event-driven mission creation
  
Greenie/hub/api/
  missions.py         # REST API endpoints for missions

Greenie/hub/workflow/
  models.py           # Extended: new StepType values
  executor.py         # Extended: parallel execution, milestone awareness

Slammer/src/components/
  Missions.tsx        # Mission control dashboard

Slammer/src/App.tsx   # Updated: Missions route
```

## Risks

- **Workflow executor complexity**: Adding parallel execution and milestone awareness to the existing executor is the riskiest change. Mitigation: keep sequential execution as the default, add parallel as opt-in.
- **Model dependency**: Planning quality depends on the orchestrator model. Mitigation: allow model override per mission, expose routing decisions.
- **State management**: Mission state across child workflows is complex. Mitigation: mission controller is the single source of truth; child workflows are ephemeral.
- **Slinker availability**: If Junie CLI is not installed, code execution fails. Mitigation: graceful degradation with clear error messages.

# Testing

## Validation Approach

Tests are integrated into each delivery stage. The existing test infrastructure (`tests/`, `pytest.ini`, `conftest.py`) is reused. Mocks are used for external services (Shrewd, Slinker) in unit tests; integration tests use real services where available.

## Key Scenarios

1. **Mission creation**: Submit a natural-language task → mission created with PLANNING status → orchestrator produces plan → milestones and features created.
2. **Milestone execution**: Workers execute in parallel → validator runs after all workers complete → validation passes → next milestone starts.
3. **Validation failure**: Validator finds issues → fix features created → workers implement fixes → re-validation passes.
4. **Mission cancellation**: Active mission cancelled → running workers stopped → state saved → mission marked CANCELLED.
5. **Mission recovery**: Application restarts → mission state loaded from checkpoint → execution resumes from last completed milestone.
6. **Approval gate**: Sensitive operation triggers approval → mission pauses → user approves → execution continues.
7. **Model routing**: Orchestrator uses high-quality model, workers use efficient model, validator uses thorough model → all routed via Shrewd.
8. **Repository intelligence**: Target repo analyzed before planning → context used in planning prompt → relevant files identified.
9. **Automation trigger**: GitHub issue created → webhook received → mission created automatically → idempotency prevents duplicates.
10. **Dashboard integration**: Mission visible in Slammer → real-time progress updates → logs stream via SSE → diffs displayed.

## Edge Cases

- Mission with no target repository (should fail with clear error)
- All workers fail in a milestone (mission should fail, not hang)
- Validator disagrees with worker on completion (fix features created, not infinite loop)
- Model provider unavailable during execution (fallback to next available provider)
- Concurrent missions on the same repository (conflict detection, safe isolation via worktrees)
- Very large repositories (repo intelligence should be incremental, not exhaustive)
- Mission timeout exceeded (graceful cancellation, checkpoint saved)

## Test Changes

- `tests/integration/test_missions.py` — Mission lifecycle tests (creation, execution, validation, recovery)
- `tests/unit/test_mission_models.py` — Model serialization/deserialization
- `tests/unit/test_mission_controller.py` — Controller logic with mocked dependencies
- `tests/unit/test_repo_intelligence.py` — Repository analysis with test fixtures
- `tests/unit/test_automation.py` — Webhook handling, idempotency, rate limiting
- `Slammer/src/components/__tests__/Missions.test.tsx` — Dashboard component tests
- Extend `tests/integration/test_integration.py` with mission-related cross-service tests

# Delivery Steps

### ✓ Step 1: Phase 1 — Mission data models and storage
Implement the core mission data model and SQLite persistence layer.

- Create `Greenie/hub/mission/models.py` with Mission, MissionMilestone, MissionFeature, ValidationContract, ValidationResult, and MissionCheckpoint dataclasses.
- Create `Greenie/hub/mission/storage.py` with SQLite tables and CRUD operations (follow the pattern from `hub/workflow/storage.py`).
- Create `Greenie/hub/mission/__init__.py` with public exports.
- Add unit tests for model serialization/deserialization in `tests/unit/test_mission_models.py`.
- Register the mission module in `Greenie/hub/__init__.py`.

### ✓ Step 2: Phase 2 — Mission API and controller
Build the REST API and mission lifecycle controller.

- Create `Greenie/hub/api/missions.py` with endpoints: POST/GET missions, GET mission detail, cancel/resume/approve, logs (SSE), diff, validation results.
- Create `Greenie/hub/mission/controller.py` with mission lifecycle: create → planning → execution → validation → completion → recovery.
- Register the route module in `Greenie/hub/api/__init__.py`.
- Add integration tests in `tests/integration/test_missions.py` for mission CRUD and lifecycle.
- Verify the API endpoints are accessible via Swagger UI.

### ✓ Step 3: Phase 3 — Extended workflow engine
Add parallel execution and milestone awareness to the workflow engine.

- Extend `Greenie/hub/workflow/models.py`: add PLANNER, WORKER, VALIDATOR, MILESTONE to StepType; add `role` and `model_override` fields to WorkflowStep.
- Extend `Greenie/hub/workflow/executor.py`: implement parallel step execution for independent steps within a milestone; milestone-aware scheduling (all workers complete before validator).
- Keep sequential execution as the default; parallel is opt-in via a mission flag.
- Add tests for parallel execution and milestone scheduling.
- Ensure backward compatibility with existing workflows.

### ✓ Step 4: Phase 4 — Planning and repository intelligence
Implement the orchestrator planning phase and repository analysis.

- Create `Greenie/hub/mission/planner.py`: orchestrator logic that decomposes a goal into milestones, features, and a validation contract using Shrewd for LLM calls.
- Create `Greenie/hub/mission/repo_intelligence.py`: analyze target repository structure, build/test commands, dependencies, conventions, and relevant files.
- Integrate repo intelligence output into the planning prompt context.
- Add unit tests for planner with mocked Shrewd and repo intelligence with test fixtures.
- Verify planning produces structured output (milestones, features, validation contract).

### ✓ Step 5: Phase 5 — Execution, validation, and auto-review
Implement worker execution, independent validation, and automated code review.

- Extend the mission controller to create child workflows for each milestone with worker steps (parallel) and validator steps.
- Workers use Slinker for code tasks; validators run deterministic checks (build, test, lint) and AI-assisted review.
- Extend `Greenie/hub/auto_review.py` with structured findings (severity, file/line, explanation, correction).
- Implement validation failure handling: fix features created, workers implement, re-validation.
- Add integration tests for the full execution cycle (worker → validator → fix → re-validate).
- Verify model routing via Shrewd (different models for orchestrator, worker, validator).

### ✓ Step 6: Phase 6 — Slammer mission dashboard
Build the mission control UI in the Slammer dashboard.

- Create `Slammer/src/components/Missions.tsx` with mission list (active/queued/completed/failed), mission detail with milestone progress, feature status, execution logs (SSE), diff viewer, validation results, and approve/cancel/resume controls.
- Update `Slammer/src/App.tsx` to add the Missions route.
- Connect to the Greenie mission API endpoints.
- Add component tests in `Slammer/src/components/__tests__/Missions.test.tsx`.
- Verify real-time updates via SSE for mission progress and logs.

### ✓ Step 7: Phase 7 — Automation engine and hardening
Add event-driven mission creation, persistence, security controls, and final integration.

- Create `Greenie/hub/mission/automation.py`: GitHub webhook handler (issues, PRs, CI failures), schedule-based triggers, idempotency (duplicate event protection), rate limiting, action registry.
- Implement mission checkpoint persistence: save state at milestone boundaries, resume from checkpoint on restart.
- Add autonomy levels: supervised (all operations require approval), restricted autonomous (only sensitive operations require approval), full autonomous.
- Add secret redaction in mission logs and model context.
- Extend `tests/integration/test_integration.py` with mission-related cross-service tests.
- Add an end-to-end smoke test: create a mission against a test repository, run checks, generate a completion report.
- Update documentation: README.md, docs/ARCHITECTURE.md, ROADMAP.md, CHANGELOG.md.

### ✓ Step 8: Phase 8 — Mission analytics, SSE streaming, and fix-revalidate cycle
Complete the remaining deferred items from the original requirements.

- Create `Greenie/hub/mission/analytics.py`: Mission-specific analytics (success/failure rates, time in lifecycle stages, model usage per mission, validation findings summary, retry counts).
- Implement SSE (Server-Sent Events) log streaming endpoint: `GET /api/missions/{id}/logs` for real-time execution logs in the Slammer dashboard.
- Implement the fix-revalidate cycle: When validation fails, automatically create fix features, assign to workers, re-run validation, and iterate until passed or max retries exceeded.
- Add mission execution log storage and retrieval in `storage.py`.
- Add API endpoint for mission diffs: `GET /api/missions/{id}/diff` showing changed files.
- Add unit tests for analytics, SSE streaming, and fix-revalidate cycle.
- Add integration tests for the full fix-revalidate loop.
- Update documentation with the new capabilities.

### ✓ Step 9: Phase 9 — End-to-end smoke test, cross-service integration, and final hardening
Close out the remaining deferred items from the mission control system deliverables.

- Add cross-service mission integration tests to `tests/integration/test_integration.py`: Mission API health check, mission creation via Greenie API, mission lifecycle via API endpoints, and cross-service mission workflow (mission → Slinker task → Shrewd routing).
- Implement end-to-end smoke test: Create a mission against a test repository, run planning, execute a simple milestone, validate, and generate a completion report — all without requiring Junie CLI or external services.
- Fix the unused `format_duration` helper in `Slammer/src/components/Missions.tsx` by integrating it into the mission detail view to show mission duration.
- Add mission-related analytics to the Slammer dashboard: A simple analytics panel showing success rate, average duration, and recent missions.
- Update documentation: CHANGELOG.md (v1.10.0), docs/ARCHITECTURE.md (Phase 9 changes), ROADMAP.md (Phase 10 entry).
- Add unit tests for the smoke test components and cross-service integration.
- Run full test suite to verify backward compatibility.

### ✓ Step 10: Phase 10 — CSRF protection, rate limiting, Gobber embeddings, and Sneaker OTLP
Implement the remaining Phase 10 items from the ROADMAP that are feasible in the current environment.

- Add CSRF protection middleware to Greenie (`Greenie/hub/api/csrf.py`) with token generation and validation.
- Complete rate limiting on auth endpoints in Greenie (`Greenie/hub/api/core.py`) — already partially implemented.
- Add vector embedding API endpoints to Gobber (`Gobber/gobber/api.py`) for semantic search integration.
- Add OTLP export support to Sneaker (`Sneaker/sneaker/otlp_export.py`) for metrics, traces, and logs.
- Add tests for CSRF protection, rate limiting completion, Gobber embeddings API, and Sneaker OTLP export.
- Update documentation: CHANGELOG.md (v1.11.0), docs/ARCHITECTURE.md (Phase 10 changes), ROADMAP.md (Phase 10 marked complete).
- Items deferred: User authentication (requires substantial infra), Junie CLI integration (requires CLI install), clean-clone verification (requires fresh env), Ubuntu VM test (requires VM), reboot persistence (requires reboot).

### ✓ Step 11: Phase 11 — Agent Harness: Spec Mode, Custom Droids, Skills, Hooks, and Environments
Implement Factory-inspired agent harness capabilities that extend the mission control system with reusable workflows, specialized subagents, and event-driven automation.

- **Spec Mode** (`Greenie/hub/mission/spec_mode.py`): Read-only research phase before implementation. Analyze the repository, propose a concrete implementation plan, and require human approval before any code changes. Store specs in a persistent spec store with queryable history. API endpoints: `POST /api/specs` (create spec), `GET /api/specs` (list specs), `GET /api/specs/{id}` (detail), `POST /api/specs/{id}/approve` (approve and start mission), `POST /api/specs/{id}/reject` (reject with feedback).
- **Custom Droids** (`Greenie/hub/mission/droids.py`): Specialized subagents defined in Markdown with their own system prompt, model preference, and tool policy. Project droids in `.evershade/droids/`, personal droids in config directory. Built-in droids: `worker` (implementation), `explorer` (research), `reviewer` (code review), `validator` (validation). Discovery, validation, and invocation via Task tool. API endpoints: `GET /api/droids` (list), `POST /api/droids` (create), `GET /api/droids/{name}` (detail), `DELETE /api/droids/{name}` (delete).
- **Skills System** (`Greenie/hub/mission/skills.py`): Reusable SKILL.md workflows. Skills are directories with SKILL.md entry point, optional supporting files, and frontmatter (name, description, triggers). Project skills in `.evershade/skills/`, personal skills in config directory. Model-invoked (auto-discovered based on task), composable, and token-efficient. API endpoints: `GET /api/skills` (list), `POST /api/skills` (create), `GET /api/skills/{name}` (detail), `POST /api/skills/{name}/invoke` (manual invocation).
- **Hooks System** (`Greenie/hub/mission/hooks.py`): Event-driven lifecycle hooks. Supported events: `PreToolUse` (before tool execution, can block), `PostToolUse` (after tool completion), `SessionStart` (context injection), `SessionEnd` (cleanup), `MissionStart`, `MissionEnd`, `MilestoneComplete`, `ValidationFail`. Hooks are scripts or webhooks configured in `hooks.json`. API endpoints: `GET /api/hooks` (list), `POST /api/hooks` (register), `DELETE /api/hooks/{id}` (remove), `POST /api/hooks/{id}/test` (dry-run).
- **Environments** (`Greenie/hub/mission/environments.py`): Reusable sandbox definitions. Environment describes repositories, tools, dependencies, setup commands, and health checks. API endpoints: `GET /api/environments` (list), `POST /api/environments` (create), `GET /api/environments/{id}` (detail), `POST /api/environments/{id}/validate` (health check), `DELETE /api/environments/{id}` (delete).
- **Slammer UI updates**: Add Specs page (list, create, approve/reject), Droids page (manage custom droids), Skills page (browse and invoke skills), Hooks page (configure lifecycle hooks).
- **Tests**: Unit tests for each component, integration tests for spec-to-mission flow, droid invocation, skill discovery, and hook execution.
- **Documentation**: Update CHANGELOG.md (v1.12.0), docs/ARCHITECTURE.md (Phase 11), ROADMAP.md (Phase 11 marked complete).