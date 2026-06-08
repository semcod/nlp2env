# nlp2env

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Dependencies](#dependencies)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `nlp2env`
- **version**: `0.1.2`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(1), app.doql.less, goal.yaml, .env.example, project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: nlp2env;
  version: 0.1.2;
}

dependencies {
  dev: "pytest>=8.0, mcp>=1.0, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
}

interface[type="cli"] {
  framework: argparse;
}
interface[type="cli"] page[name="nlp2env-mcp"] {

}

workflow[name="venv"] {
  trigger: manual;
  step-1: run cmd=test -x "$(PIP)" || $(PYTHON) -m venv "$(VENV)";
}

workflow[name="install"] {
  trigger: manual;
  step-1: run cmd=$(PIP) install -e .;
}

workflow[name="install-mcp"] {
  trigger: manual;
  step-1: run cmd=$(PIP) install -e ".[mcp]";
}

workflow[name="test"] {
  trigger: manual;
  step-1: run cmd=$(PYTEST) tests/ -v;
}

workflow[name="test-mcp-live"] {
  trigger: manual;
  step-1: run cmd=./scripts/test-mcp-live.sh;
}

workflow[name="examples"] {
  trigger: manual;
  step-1: run cmd=./examples/run-e2e.sh;
}

workflow[name="examples-multilang"] {
  trigger: manual;
  step-1: run cmd=export SMTP_PASSWORD="$${SMTP_PASSWORD:-e2e-test-secret-42}"; \;
  step-2: run cmd=bash examples/write/smtp-email/e2e-multilang.sh;
}

workflow[name="examples-all"] {
  trigger: manual;
  step-1: run cmd=echo "ALL EXAMPLES + MULTILANG OK";
}

deploy {
  target: makefile;
}

environment[name="local"] {
  runtime: docker-compose;
  env_file: .env;
  python_version: >=3.10;
}
```

## Workflows

## Dependencies

### Runtime

*(see pyproject.toml)*

### Development

```text markpact:deps python scope=dev
pytest>=8.0
mcp>=1.0
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Call Graph

*6 nodes · 3 edges · 2 modules · CC̄=2.8*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `build_mcp` *(in src.nlp2env_mcp.server)* | 2 | 1 | 95 | **96** |
| `resolve_env_path` *(in src.nlp2env.env_file)* | 4 | 2 | 14 | **16** |
| `load` *(in src.nlp2env.env_file.EnvFile)* | 10 ⚠ | 0 | 15 | **15** |
| `mask_value` *(in src.nlp2env.env_file)* | 4 | 7 | 2 | **9** |
| `list_masked` *(in src.nlp2env.env_file.EnvFile)* | 2 | 0 | 3 | **3** |
| `main` *(in src.nlp2env_mcp.server)* | 1 | 0 | 2 | **2** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/nlp2env
# generated in 0.00s
# nodes: 6 | edges: 3 | modules: 2
# CC̄=2.8

HUBS[20]:
  src.nlp2env_mcp.server.build_mcp
    CC=2  in:1  out:95  total:96
  src.nlp2env.env_file.resolve_env_path
    CC=4  in:2  out:14  total:16
  src.nlp2env.env_file.EnvFile.load
    CC=10  in:0  out:15  total:15
  src.nlp2env.env_file.mask_value
    CC=4  in:7  out:2  total:9
  src.nlp2env.env_file.EnvFile.list_masked
    CC=2  in:0  out:3  total:3
  src.nlp2env_mcp.server.main
    CC=1  in:0  out:2  total:2

MODULES:
  src.nlp2env.env_file  [4 funcs]
    list_masked  CC=2  out:3
    load  CC=10  out:15
    mask_value  CC=4  out:2
    resolve_env_path  CC=4  out:14
  src.nlp2env_mcp.server  [2 funcs]
    build_mcp  CC=2  out:95
    main  CC=1  out:2

EDGES:
  src.nlp2env_mcp.server.main → src.nlp2env_mcp.server.build_mcp
  src.nlp2env.env_file.EnvFile.load → src.nlp2env.env_file.resolve_env_path
  src.nlp2env.env_file.EnvFile.list_masked → src.nlp2env.env_file.mask_value
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/nlp2env
# generated in 0.00s
# nodes: 6 | edges: 3 | modules: 2
# CC̄=2.8

HUBS[20]:
  src.nlp2env_mcp.server.build_mcp
    CC=2  in:1  out:95  total:96
  src.nlp2env.env_file.resolve_env_path
    CC=4  in:2  out:14  total:16
  src.nlp2env.env_file.EnvFile.load
    CC=10  in:0  out:15  total:15
  src.nlp2env.env_file.mask_value
    CC=4  in:7  out:2  total:9
  src.nlp2env.env_file.EnvFile.list_masked
    CC=2  in:0  out:3  total:3
  src.nlp2env_mcp.server.main
    CC=1  in:0  out:2  total:2

MODULES:
  src.nlp2env.env_file  [4 funcs]
    list_masked  CC=2  out:3
    load  CC=10  out:15
    mask_value  CC=4  out:2
    resolve_env_path  CC=4  out:14
  src.nlp2env_mcp.server  [2 funcs]
    build_mcp  CC=2  out:95
    main  CC=1  out:2

EDGES:
  src.nlp2env_mcp.server.main → src.nlp2env_mcp.server.build_mcp
  src.nlp2env.env_file.EnvFile.load → src.nlp2env.env_file.resolve_env_path
  src.nlp2env.env_file.EnvFile.list_masked → src.nlp2env.env_file.mask_value
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 28f 1885L | shell:10,python:6,yml:5,txt:2,yaml:1,toml:1,json:1,env:1 | 2026-06-08
# generated in 0.01s
# CC̅=2.8 | critical:0/22 | dups:0 | cycles:0

HEALTH[0]: ok

REFACTOR[0]: none needed

PIPELINES[8]:
  [1] Src [main]: main → build_mcp → resolve_env_path
      PURITY: 100% pure
  [2] Src [load]: load → resolve_env_path
      PURITY: 100% pure
  [3] Src [get]: get
      PURITY: 100% pure
  [4] Src [set_many]: set_many
      PURITY: 100% pure
  [5] Src [list_masked]: list_masked → mask_value
      PURITY: 100% pure
  [6] Src [backup]: backup
      PURITY: 100% pure
  [7] Src [save]: save
      PURITY: 100% pure
  [8] Src [apply_text]: apply_text
      PURITY: 100% pure

LAYERS:
  src/                            CC̄=3.6    ←in:0  →out:0
  │ server                     243L  0C    5m  CC=2      ←0
  │ env_file                   126L  1C   10m  CC=10     ←1
  │ profiles                    65L  0C    2m  CC=5      ←1
  │ __init__                    13L  0C    0m  CC=0.0    ←0
  │ __main__                     6L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=0.0    ←in:0  →out:0
  │ prompts-multilang.txt      229L  0C    0m  CC=0.0    ←0
  │ e2e.sh                      80L  0C    1m  CC=0.0    ←0
  │ prompts-multilang.log.txt    63L  0C    0m  CC=0.0    ←0
  │ e2e.sh                      60L  0C    1m  CC=0.0    ←0
  │ e2e.sh                      58L  0C    1m  CC=0.0    ←0
  │ e2e.sh                      55L  0C    1m  CC=0.0    ←0
  │ run-e2e.sh                  39L  0C    0m  CC=0.0    ←0
  │ e2e.sh                      31L  0C    0m  CC=0.0    ←0
  │ e2e-multilang.sh            28L  0C    0m  CC=0.0    ←0
  │ mcp-config.cursor.json      11L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml           7L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml           7L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml           7L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml           7L  0C    0m  CC=0.0    ←0
  │ docker-compose.yml           7L  0C    0m  CC=0.0    ←0
  │ prompts.env                  2L  0C    0m  CC=0.0    ←0
  │
  scripts/                        CC̄=0.0    ←in:0  →out:0
  │ test-mcp-live.sh            67L  0C    1m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              59L  0C    0m  CC=0.0    ←0
  │ project.sh                  59L  0C    0m  CC=0.0    ←0
  │ Makefile                    42L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │

COUPLING:
                       src.nlp2env  src.nlp2env_mcp
      src.nlp2env               ──              ←10  hub
  src.nlp2env_mcp               10               ──  !! fan-out
  CYCLES: none
  HUB: src.nlp2env/ (fan-in=10)
  SMELL: src.nlp2env_mcp/ fan-out=10 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 0 groups | 5f 328L | 2026-06-08

SUMMARY:
  files_scanned: 5
  total_lines:   328
  dup_groups:    0
  dup_fragments: 0
  saved_lines:   0
  scan_ms:       3575
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 17 func | 3f | 2026-06-08
# generated in 0.00s

NEXT[1] (ranked by impact):
  [1] !! SPLIT           goal.yaml
      WHY: 512L, 0 classes, max CC=0
      EFFORT: ~4h  IMPACT: 0


RISKS[1]:
  ⚠ Splitting goal.yaml may break 0 import paths

METRICS-TARGET:
  CC̄:          3.6 → ≤2.5
  max-CC:      10 → ≤5
  god-modules: 1 → 0
  high-CC(≥15): 0 → ≤0
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  (first run — no previous data)
```

## Intent

MCP server for reading and writing .env variables (email/SMTP and custom keys)
