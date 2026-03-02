# PSGE Repository Layout

Date: 2026-02-28

```text
psge/
  README.md
  pyproject.toml
  00_OVERVIEW.md
  01_PRD.md
  02_ARCHITECTURE.md
  03_DIRECTORY_STRUCTURE.md
  04_VARIANT_PANEL.md
  05_MECHANISM_TAXONOMY.md
  06_VALIDATION_PLAN.md
  07_REFERENCES.md
  08_ARCHITECT_DESIGN.md
  09_PLAN.md
  PROGRESS.md
  docs/
    USER_GUIDE.md
    OUTPUT_SCHEMA.md
    CONTRIBUTING.md
    PHASE1_5_REMAP.md
    SUPERVISOR_REPORT.md
    VALIDATION_LOGIC.md
    VALIDATION_SCIENCE.md
    M7_PETE_OVERVIEW.md
    COMMIT_PREP_REVIEW.md
    m7_examples/
  data/
    public/
      sequences/
      structures/
      annotations/
      structures/pdb/          # PDB files (e.g. 3NKS.cif)
      structures/cache/       # derived; local only
    private/                  # excluded from git
      README.md
    testdata/
      variants/
        ppox_panel.yaml
        ppox_panel_expected.yaml
      expected/               # placeholder for expected outputs
  configs/
    default.yaml
    backends/                 # placeholder
    environments/             # placeholder
  src/psge/
    cli.py
    core/
    pipeline/
    backends/
    knowledge/ppox/
    reporting/
    utils/
  tests/
  scripts/
  .github/
    workflows/
      ci.yml
  docker/                     # placeholder; Phase 1 scope per PRD §9
  results/                    # local output; ignored by git
```

## Conventions

- Root-level `00_`–`09_` docs are primary project spec. `docs/` holds Phase 1.5 material, validation, and supervisor reports.
- `data/public` is allowed in git if it contains only public assets (e.g. 3NKS.cif). `data/public/structures/cache/` is derived and may be ignored.
- `data/private` is excluded from git; for future VCF/WGS artifacts.
- `knowledge/ppox` stores domain config (sites, motifs); see `sites.yaml`.
- `results/` is local output (ignored by git).
- `docker/`, `configs/backends/`, `configs/environments/`, `data/testdata/expected/` are placeholders for planned or optional content.
