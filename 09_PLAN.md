# PSGE Implementation Plan (Phase 1)

Date: 2026-02-28

Source: 01_PRD.md, 08_ARCHITECT_DESIGN.md, 03_DIRECTORY_STRUCTURE.md, 06_VALIDATION_PLAN.md, 04_VARIANT_PANEL.md.

---

## 1. Milestone Breakdown

| Milestone | Scope | Deliverables |
|-----------|-------|--------------|
| M1 | Pipeline skeleton + CLI | pyproject.toml, src/psge layout, cli.py stub, empty pipeline stages, single variant run (mock) |
| M2 | Preflight routing + panel runner | VariantRecord, parse R59W/78insC/IVS2-2 a→c/I12T, panel YAML loader, route missense vs truncation/splice |
| M3 | Structure backend + caching | Sequence fetch, AlphaFold/ESMFold integration, cache layer, StructurePair output |
| M4 | Stability + context mapping | FoldX/Rosetta, DeltaFeatures, ContextFeatures, knowledge/ppox config |
| M5 | Mechanism classifier + report templates | MechanismHypothesis, rules engine, summary.json, report.md |
| M6 | Run panel + validation report | Full panel run, T2 assertions, validation report |
| M7 | Review with Pete | Domain sanity check (human) |

---

## 2. Ordered Task List (M1 Focus)

### M1: Pipeline Skeleton + CLI

| # | Task | Depends | Output |
|---|------|---------|--------|
| 1 | Create pyproject.toml (Python package, deps placeholder) | — | pyproject.toml |
| 2 | Create directory structure per 03_DIRECTORY_STRUCTURE | — | src/psge/, data/, configs/, tests/ |
| 3 | Define data types: VariantRecord, Config (stub) | — | core/types.py or core/models.py |
| 4 | Implement CLI: `psge run --variant R59W` (or similar) | 1, 2 | cli.py |
| 5 | Pipeline orchestrator stub: call stages in order, pass through | 3, 4 | pipeline/runner.py |
| 6 | Stage stubs: Preflight, Sequence, ..., Reporting (return mock/skip) | 5 | pipeline/*.py |
| 7 | Emit run_manifest.json (minimal: timestamp, input, config hash) | 5 | reporting/manifest.py |
| 8 | Config loader: default.yaml, merge CLI overrides | 4 | utils/config.py |

### M2 Tasks (for dependency graph)

| # | Task | Depends |
|---|------|---------|
| 9 | Preflight: parse variant string → VariantRecord | 3 |
| 10 | Preflight: classify type (missense/truncation/splice) | 9 |
| 11 | Panel YAML loader: parse 04_VARIANT_PANEL format | 4 |
| 12 | CLI: `psge run --panel path/to/panel.yaml` | 4, 11 |

### Dependencies (M1 critical path)

```
1, 2 → 3 → 4
         → 5 → 6, 7
8 → 4
```

---

## 3. Risk Ordering

| Risk | Severity | Mitigation | Phase |
|------|----------|------------|-------|
| Wrong variant routing (T1 fail) | High | Tests first for preflight; panel asserts | M2 |
| Structure backend unavailable | High | ESMFold fallback; mock for CI | M3 |
| Cache key collisions | Medium | Include variant, config, backend in key | M3 |
| Overinterpretation in report | Medium | Explicit limits in template; no phenotype | M5 |
| Reproducibility drift (T3) | Medium | run_manifest, strict cache keys | M1–M6 |

---

## 4. Sprint Slices (TDD-Friendly)

### Sprint 1 (M1)
- **Test first:** CLI accepts `--variant R59W` and exits 0; pipeline invoked.
- **Test first:** run_manifest.json emitted with input_hash, timestamp.
- Implement: 1–8.

### Sprint 2 (M2)
- **Test first:** Preflight: R59W → structural; 78insC → non-structural; IVS2-2 a→c → non-structural (T1).
- Implement: 9–12.

### Sprint 3 (M3)
- **Test first:** Sequence stage returns WT + mutant for R59W (or mocked).
- **Test first:** Structure stage cached; second run hits cache.
- Implement: structure backend, caching.

### Sprint 4 (M4)
- **Test first:** Stability returns ΔΔG; context returns distance/site flags.
- Implement: FoldX, context mapping.

### Sprint 5 (M5)
- **Test first:** MechanismHypothesis has class, confidence, limits.
- Implement: classifier, report templates.

### Sprint 6 (M6)
- **Test first:** Panel run produces summary.json per variant; T2 asserts.
- Implement: validation report.

---

## 5. Tests to Write First

(Per 06_VALIDATION_PLAN, TDD)

| Test | Validates | Write When |
|------|-----------|------------|
| test_cli_run_variant_exits_zero | CLI invokes pipeline | Sprint 1, before task 4 |
| test_run_manifest_emitted | run_manifest.json present, has fields | Sprint 1, before task 7 |
| test_preflight_r59w_structural | R59W → track=structural | Sprint 2, before task 9 |
| test_preflight_78insc_non_structural | 78insC → track=non_structural | Sprint 2 |
| test_preflight_ivs2_non_structural | IVS2-2 a→c → track=non_structural | Sprint 2 |
| test_preflight_i12t_structural | I12T → track=structural (missense) | Sprint 2 |
| test_panel_load | Load panel YAML, get variant list | Sprint 2, before task 11 |
| test_cache_hit | Second run reuses structure | Sprint 3 |
| test_mechanism_output_structure | MechanismHypothesis has required fields | Sprint 5 |
| test_panel_t2_assertions | Full panel matches 04_VARIANT_PANEL expected | Sprint 6 |

---

## 6. Panel Format (Reference)

From 04_VARIANT_PANEL.md. Panel YAML shall include:
- Variants by mechanism class (substrate-binding, destabilization, truncation, targeting)
- Expected mechanism class per variant for T2
- Format TBD but must support: variant string, expected_class
