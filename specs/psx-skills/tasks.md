# Tasks: PSX Skills Creation

**Input**: Design documents from `/specs/psx-skills/`
**Prerequisites**: research.md (done), constitution.md (done), 4 skills (done)

**Tests**: Tests are NOT included (documentation/skills project — no code test suite).

**Organization**: Tasks are grouped by skill to enable independent implementation and testing of each skill.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which skill this task belongs to (US1-US4)
- Include exact file paths in descriptions

## Path Conventions

- **Skills**: `.claude/skills/<skill-name>/`
- **References**: `.claude/skills/<skill-name>/references/`
- **Constitution**: `.specify/memory/constitution.md`
- **ADR**: `history/adr/`

---

## Phase1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 [P] Create skill directories: `.claude/skills/psx-data-fetcher/`, `.claude/skills/financial-ratios-psx/`, `.claude/skills/trade-rules-engine/`, `.claude/skills/risk-management/`
- [ ] T002 [P] Create references directories for each skill under `.claude/skills/<skill-name>/references/`
- [ ] T003 [P] Initialize constitution at `.specify/memory/constitution.md` with PSX investment system principles
- [ ] T004 Create `history/adr/` and `history/prompts/constitution/` directories for governance artifacts

**Checkpoint**: Project structure ready — skill creation can begin.

---

## Phase2: Foundational (Blocking Prerequisites)

**Purpose**: Core research and constitution that ALL skills depend on.

- [ ] T005 Read and analyze `research.md` to extract system architecture (Layers 0-3), core philosophy, and strategy rules
- [ ] T006 Create constitution v1.0.0 at `.specify/memory/constitution.md` with 6 core principles (Strategy Over Tools, Finance-First, Risk Control Over Profit, Discipline Over Intelligence, Data-Driven Decisions Only, Consistent Process)
- [ ] T007 Create ADR-001 at `history/adr/ADR-001-psx-skills-architecture.md` documenting the 4-skill architecture decision with alternatives
- [ ] T008 [P] Research PSX DPS portal structure via WebFetch: `https://dps.psx.com.pk` and `https://www.psx.com.pk`
- [ ] T009 [P] Research PSX financial statement formats: column names, units (PKR millions), SECP requirements

**Checkpoint**: Foundation ready — individual skill implementation can now begin in parallel.

---

## Phase3: User Story 1 - PSX Data Fetcher Skill (Priority: P1) 🎯 MVP

**Goal**: Enable Claude Code to fetch data from PSX portals with correct endpoints, rate limits, and pagination.

**Independent Test**: Skill can be invoked to scrape a PSX company page and return structured data.

### Implementation for User Story 1

- [ ] T010 [P] [US1] Create `.claude/skills/psx-data-fetcher/SKILL.md` with DPS portal endpoint map, rate limits (30 req/min, 2-3s delay), pagination patterns, and scraping patterns (Playwright for dynamic pages)
- [ ] T011 [P] [US1] Create `.claude/skills/psx-data-fetcher/references/endpoints.md` with complete URL map for dps.psx.com.pk, www.psx.com.pk, and financials.psx.com.pk
- [ ] T012 [P] [US1] Create `.claude/skills/psx-data-fetcher/references/playwright-patterns.md` with Playwright recipes for pagination, table extraction, file downloads, and dynamic content waiting
- [ ] T013 [P] [US1] Create `.claude/skills/psx-data-fetcher/references/rate-limits.md` with delay strategies, exponential backoff, and session management patterns
- [ ] T014 [P] [US1] Create `.claude/skills/psx-data-fetcher/references/data-dictionary.md` with PSX field definitions, sector codes, and index symbols
- [ ] T015 [P] [US1] Create `.claude/skills/psx-data-fetcher/references/psx-symbols.md` with symbol format rules, large-cap reference, and company listing patterns

**Checkpoint**: At this point, PSX Data Fetcher skill is fully functional and testable independently.

---

## Phase4: User Story 2 - Financial Ratios PSX Skill (Priority: P2)

**Goal**: Enable correct financial ratio calculations using PSX-specific column names and statement formats.

**Independent Test**: Skill can compute ROE, P/E, EPS, Debt-to-Equity from a sample PSX financial statement.

### Implementation for User Story 2

- [ ] T016 [P] [US2] Create `.claude/skills/financial-ratios-psx/SKILL.md` with PSX vs standard column name mapping, core ratio formulas (ROE, P/E, EPS, Debt-to-Equity), and data quality checks
- [ ] T017 [P] [US2] Create `.claude/skills/financial-ratios-psx/references/psx-column-mapping.md` with exact PSX column names for income statement and balance sheet
- [ ] T018 [P] [US2] Create `.claude/skills/financial-ratios-psx/references/ratio-formulas.md` with Python implementations for all ratios, TTM EPS, and annualization
- [ ] T019 [P] [US2] Create `.claude/skills/financial-ratios-psx/references/statement-samples.md` with typical PSX income statement and balance sheet samples, common pitfalls
- [ ] T020 [P] [US2] Create `.claude/skills/financial-ratios-psx/references/unit-conversions.md` with PKR millions/thousands normalization and shares outstanding handling

**Checkpoint**: At this point, Financial Ratios PSX skill is fully functional and testable independently.

---

## Phase5: User Story 3 - Trade Rules Engine Skill (Priority: P3)

**Goal**: Encode exact entry/exit logic with MA crossovers, RSI thresholds, and volume confirmation.

**Independent Test**: Skill can generate BUY/HOLD/SELL signals given price, MA, RSI, and volume data.

### Implementation for User Story 3

- [ ] T021 [P] [US3] Create `.claude/skills/trade-rules-engine/SKILL.md` with Layer 0-3 rules, MA(20/50/200) crossover logic, RSI(14) 30/70 thresholds, volume confirmation (≥120%), and complete signal flow
- [ ] T022 [P] [US3] Create `.claude/skills/trade-rules-engine/references/ma-crossover-logic.md` with crossover detection, SMA calculation, and complete MA signal logic
- [ ] T023 [P] [US3] Create `.claude/skills/trade-rules-engine/references/rsi-rules.md` with RSI calculation, signal integration, and signal tier mapping
- [ ] T024 [P] [US3] Create `.claude/skills/trade-rules-engine/references/volume-confirmation.md` with volume metrics, confirmation logic, spike investigation, and PSX-specific notes
- [ ] T025 [P] [US3] Create `.claude/skills/trade-rules-engine/references/signal-examples.md` with 5 worked examples (Strong Buy through No Trade)

**Checkpoint**: At this point, Trade Rules Engine skill is fully functional and testable independently.

---

## Phase6: User Story 4 - Risk Management Skill (Priority: P4)

**Goal**: Encode capital protection rules: 3-5% max loss, position sizing, stop-loss logic, and prohibited behaviors.

**Independent Test**: Skill can calculate position size, stop-loss levels, and validate a trade against all risk rules.

### Implementation for User Story 4

- [ ] T026 [P] [US4] Create `.claude/skills/risk-management/SKILL.md` with 3-5% max loss rule, position sizing formula, initial/trailing stop-loss logic, portfolio-level limits, and 7 prohibited behaviors
- [ ] T027 [P] [US4] Create `.claude/skills/risk-management/references/position-sizing.md` with core formula, conservative vs standard sizing, and extended Python example
- [ ] T028 [P] [US4] Create `.claude/skills/risk-management/references/stop-loss.md` with initial stop, trailing stop logic, stop-loss scenarios, and PSX-specific notes (circuit breakers)
- [ ] T029 [P] [US4] Create `.claude/skills/risk-management/references/portfolio-limits.md` with exposure limits, health metrics, and enforcement actions
- [ ] T030 [P] [US4] Create `.claude/skills/risk-management/references/prohibited-behaviors.md` with 7 forbidden behaviors, enforcement code, and alternative actions

**Checkpoint**: All 4 skills are now independently functional.

---

## Phase7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple skills

- [ ] T031 [P] Create PHR (Prompt History Record) for constitution creation at `history/prompts/constitution/001-create-psx-skills.constitution.prompt.md`
- [ ] T032 [P] Create PHR for ADR creation at `history/prompts/constitution/002-psx-skills-architecture-adr.constitution.prompt.md`
- [ ] T033 Validate all 4 SKILL.md files are <500 lines each
- [ ] T034 Validate all skills have "Before Implementation" section with context gathering table
- [ ] T035 Validate all skills have "What This Skill Does" and "What This Skill Does NOT Do" sections
- [ ] T036 Validate all skills have Output Checklist with ≥7 items
- [ ] T037 [P] Cross-reference skills: ensure `trade-rules-engine` references `psx-data-fetcher` and `risk-management`, ensure `financial-ratios-psx` references `psx-data-fetcher`
- [ ] T038 Validate constitution.md has no bracketed placeholders, correct version (1.0.0), and ISO date format
- [ ] T039 Validate ADR-001 passes all 3 significance tests (impact, alternatives, scope)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase1)**: No dependencies — can start immediately
- **Foundational (Phase2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase3-6)**: All depend on Foundational (Phase2) completion
  - US1 (Phase3) → US2 (Phase4) → US3 (Phase5) → US4 (Phase6): Can be sequential or parallel if staffed
  - All are independently testable
- **Polish (Phase7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase2) — No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase2) — May reference US1 patterns but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase2) — References US1 (data) and US2 (ratios) but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase2) — References US3 (trading rules) but independently testable

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase2)
- Once Foundational phase completes, all user stories CAN run in parallel (if team capacity allows)
- All reference file tasks within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1 (PSX Data Fetcher)

```bash
# Launch all reference files for US1 together:
Task: "Create endpoints.md" in .claude/skills/psx-data-fetcher/references/endpoints.md
Task: "Create playwright-patterns.md" in .claude/skills/psx-data-fetcher/references/playwright-patterns.md
Task: "Create rate-limits.md" in .claude/skills/psx-data-fetcher/references/rate-limits.md
Task: "Create data-dictionary.md" in .claude/skills/psx-data-fetcher/references/data-dictionary.md
Task: "Create psx-symbols.md" in .claude/skills/psx-data-fetcher/references/psx-symbols.md
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase1: Setup
2. Complete Phase2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase3: User Story 1 (PSX Data Fetcher)
4. **STOP and VALIDATE**: Test skill independently by invoking it
5. Deploy/use if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Use (MVP!)
3. Add User Story 2 → Test independently → Use
4. Add User Story 3 → Test independently → Use
5. Add User Story 4 → Test independently → Use
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (psx-data-fetcher)
   - Developer B: User Story 2 (financial-ratios-psx)
   - Developer C: User Story 3 (trade-rules-engine)
   - Developer D: User Story 4 (risk-management)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify all skills follow skill-creator-pro framework
- Stop at any checkpoint to validate story independently
- All 4 skills are now CREATED — these tasks represent the planned work that was executed
