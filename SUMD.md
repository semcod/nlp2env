# nlp2env

MCP server for reading and writing .env variables (email/SMTP and custom keys)

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Workflows](#workflows)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Makefile Targets](#makefile-targets)
- [Code Analysis](#code-analysis)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `nlp2env`
- **version**: `0.1.2`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(1), app.doql.less, goal.yaml, .env.example, project/(3 analysis files)

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

## Interfaces

### CLI Entry Points

- `nlp2env-mcp`

### testql Scenarios

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m nlp2env
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m nlp2env --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: CLI version command
SHELL "python -m nlp2env --version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m nlp2env --help" 10000
ASSERT_EXIT_CODE 0
```

## Workflows

## Configuration

```yaml
project:
  name: nlp2env
  version: 0.1.2
  env: local
```

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

## Deployment

```bash markpact:run
pip install nlp2env

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `SMTP_HOST` | `smtp.example.com` | Email / SMTP profile (nlp2dsl-worker compatible) |
| `SMTP_PORT` | `587` |  |
| `SMTP_USER` | `user@example.com` |  |
| `SMTP_PASSWORD` | `change-me` |  |
| `SMTP_TLS` | `1` |  |
| `SMTP_FROM` | `user@example.com` |  |
| `SMTP_TIMEOUT` | `30` |  |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`nlp2env`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `venv/lib/python3.12/site-packages/cryptography/__init__.py:__version__`

## Makefile Targets

- `SHELL`
- `PIP`
- `PYTEST`
- `help`
- `venv`
- `install`
- `install-mcp`
- `test`
- `test-mcp-live`
- `examples`
- `examples-multilang`
- `examples-all`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# nlp2env | 26f 1742L | python:15,shell:10,less:1 | 2026-06-08
# stats: 43 func | 6 cls | 26 mod | CC̄=4.1 | critical:4 | cycles:0
# alerts[5]: CC scenarios_from_toon=14; CC resolve_prompt_to_env_uri=14; CC _materialize_nlp2env=12; CC parse_testtoon=11; CC _split_row=7
# hotspots[5]: build_mcp fan=32; parse_testtoon fan=15; resolve_prompt_to_env_uri fan=14; _materialize_file fan=13; _materialize_getv fan=11
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[26]:
  app.doql.less,69
  examples/integrators/mcp-stdio/e2e.sh,61
  examples/integrators/todomat-dispatch/e2e.sh,81
  examples/run-e2e.sh,40
  examples/write/apply-text/e2e.sh,59
  examples/write/custom-keys/e2e.sh,56
  examples/write/smtp-email/e2e-multilang.sh,29
  examples/write/smtp-email/e2e.sh,32
  project.sh,59
  scripts/test-mcp-live.sh,68
  src/nlp2env/__init__.py,14
  src/nlp2env/env_file.py,127
  src/nlp2env/profiles.py,66
  src/nlp2env/toon_scenarios.py,204
  src/nlp2env_mcp/__init__.py,2
  src/nlp2env_mcp/__main__.py,7
  src/nlp2env_mcp/server.py,244
  src/uri2env/__init__.py,27
  src/uri2env/cli.py,30
  src/uri2env/compile.py,31
  src/uri2env/materialize.py,162
  src/uri2env/resolve.py,79
  src/uri2env/uri.py,89
  tests/test_env_file.py,47
  tests/test_mcp_tools.py,57
  tree.sh,2
D:
  src/nlp2env/__init__.py:
  src/nlp2env/env_file.py:
    e: mask_value,resolve_env_path,EnvFile
    EnvFile: load(2),get(2),set_many(1),delete(1),list_masked(0),backup(1),save(0),apply_text(1)
    mask_value(key;value)
    resolve_env_path(path)
  src/nlp2env/profiles.py:
    e: email_profile_from_dict,email_profile_status
    email_profile_from_dict(data)
    email_profile_status(values)
  src/nlp2env/toon_scenarios.py:
    e: _strip_quoted,_detect_sep,_split_row,_parse_value,parse_testtoon,scenarios_from_toon,load_scenarios,ToonSection,ToonScript,PromptScenario
    ToonSection:
    ToonScript:
    PromptScenario: nl(0),source(0),tool(0),after(0),assert_configured(0),inline_arguments(0)
    _strip_quoted(line)
    _detect_sep(line)
    _split_row(line;sep)
    _parse_value(raw)
    parse_testtoon(text)
    scenarios_from_toon(script)
    load_scenarios(path)
  src/nlp2env_mcp/__init__.py:
  src/nlp2env_mcp/__main__.py:
  src/nlp2env_mcp/server.py:
    e: _ok,_err,_load,build_mcp,main
    _ok(payload)
    _err(message)
    _load(path)
    build_mcp()
    main()
  src/uri2env/__init__.py:
  src/uri2env/cli.py:
    e: main
    main(argv)
  src/uri2env/compile.py:
    e: compile_env_uri
    compile_env_uri(uri;host)
  src/uri2env/materialize.py:
    e: _resolve_dest,_load_getv_profile,_materialize_getv,_materialize_file,_materialize_nlp2env,materialize_uri,MaterializeResult
    MaterializeResult: to_dict(0)
    _resolve_dest(params;fallback)
    _load_getv_profile(category;profile)
    _materialize_getv(parts;dest)
    _materialize_file(parts;dest)
    _materialize_nlp2env(parts;dest;params)
    materialize_uri(uri)
  src/uri2env/resolve.py:
    e: resolve_prompt_to_env_uri,ResolvedEnvUri
    ResolvedEnvUri: to_dict(0)
    resolve_prompt_to_env_uri(prompt)
  src/uri2env/uri.py:
    e: _encode,_decode,uri_for_getv_profile,uri_for_getv_var,uri_for_env_file,uri_for_nlp2env_profile,is_env_uri,parse_env_uri,build_env_uri_index
    _encode(value)
    _decode(value)
    uri_for_getv_profile(category;profile)
    uri_for_getv_var(category;profile;var_name)
    uri_for_env_file(path)
    uri_for_nlp2env_profile(profile)
    is_env_uri(uri)
    parse_env_uri(uri)
    build_env_uri_index()
  tests/test_env_file.py:
    e: test_mask_secret,test_load_and_save_roundtrip,test_apply_text,test_email_profile,test_email_profile_missing
    test_mask_secret()
    test_load_and_save_roundtrip(tmp_path)
    test_apply_text(tmp_path)
    test_email_profile()
    test_email_profile_missing()
  tests/test_mcp_tools.py:
    e: env_path,test_interfaces,test_set_email_via_tool,test_delete_via_tool
    env_path(tmp_path;monkeypatch)
    test_interfaces()
    test_set_email_via_tool(env_path)
    test_delete_via_tool(env_path)
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('nlp2env', '0.1.2', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 69, 'less').
project_file('examples/integrators/mcp-stdio/e2e.sh', 61, 'shell').
project_file('examples/integrators/todomat-dispatch/e2e.sh', 81, 'shell').
project_file('examples/run-e2e.sh', 40, 'shell').
project_file('examples/write/apply-text/e2e.sh', 59, 'shell').
project_file('examples/write/custom-keys/e2e.sh', 56, 'shell').
project_file('examples/write/smtp-email/e2e-multilang.sh', 29, 'shell').
project_file('examples/write/smtp-email/e2e.sh', 32, 'shell').
project_file('project.sh', 59, 'shell').
project_file('scripts/test-mcp-live.sh', 68, 'shell').
project_file('src/nlp2env/__init__.py', 14, 'python').
project_file('src/nlp2env/env_file.py', 127, 'python').
project_file('src/nlp2env/profiles.py', 66, 'python').
project_file('src/nlp2env/toon_scenarios.py', 204, 'python').
project_file('src/nlp2env_mcp/__init__.py', 2, 'python').
project_file('src/nlp2env_mcp/__main__.py', 7, 'python').
project_file('src/nlp2env_mcp/server.py', 244, 'python').
project_file('src/uri2env/__init__.py', 27, 'python').
project_file('src/uri2env/cli.py', 30, 'python').
project_file('src/uri2env/compile.py', 31, 'python').
project_file('src/uri2env/materialize.py', 162, 'python').
project_file('src/uri2env/resolve.py', 79, 'python').
project_file('src/uri2env/uri.py', 89, 'python').
project_file('tests/test_env_file.py', 47, 'python').
project_file('tests/test_mcp_tools.py', 57, 'python').
project_file('tree.sh', 2, 'shell').

% ── Python Functions ─────────────────────────────────────
python_function('src/nlp2env/env_file.py', 'mask_value', 2, 4, 2).
python_function('src/nlp2env/env_file.py', 'resolve_env_path', 1, 4, 6).
python_function('src/nlp2env/profiles.py', 'email_profile_from_dict', 1, 5, 7).
python_function('src/nlp2env/profiles.py', 'email_profile_status', 1, 4, 2).
python_function('src/nlp2env/toon_scenarios.py', '_strip_quoted', 1, 6, 2).
python_function('src/nlp2env/toon_scenarios.py', '_detect_sep', 1, 2, 1).
python_function('src/nlp2env/toon_scenarios.py', '_split_row', 2, 7, 2).
python_function('src/nlp2env/toon_scenarios.py', '_parse_value', 1, 6, 4).
python_function('src/nlp2env/toon_scenarios.py', 'parse_testtoon', 1, 11, 15).
python_function('src/nlp2env/toon_scenarios.py', 'scenarios_from_toon', 1, 14, 10).
python_function('src/nlp2env/toon_scenarios.py', 'load_scenarios', 1, 1, 4).
python_function('src/nlp2env_mcp/server.py', '_ok', 1, 1, 1).
python_function('src/nlp2env_mcp/server.py', '_err', 1, 1, 1).
python_function('src/nlp2env_mcp/server.py', '_load', 1, 2, 2).
python_function('src/nlp2env_mcp/server.py', 'build_mcp', 0, 2, 32).
python_function('src/nlp2env_mcp/server.py', 'main', 0, 1, 2).
python_function('src/uri2env/cli.py', 'main', 1, 4, 9).
python_function('src/uri2env/compile.py', 'compile_env_uri', 2, 3, 6).
python_function('src/uri2env/materialize.py', '_resolve_dest', 2, 4, 5).
python_function('src/uri2env/materialize.py', '_load_getv_profile', 2, 3, 4).
python_function('src/uri2env/materialize.py', '_materialize_getv', 2, 4, 11).
python_function('src/uri2env/materialize.py', '_materialize_file', 2, 3, 13).
python_function('src/uri2env/materialize.py', '_materialize_nlp2env', 3, 12, 11).
python_function('src/uri2env/materialize.py', 'materialize_uri', 1, 5, 8).
python_function('src/uri2env/resolve.py', 'resolve_prompt_to_env_uri', 1, 14, 14).
python_function('src/uri2env/uri.py', '_encode', 1, 1, 1).
python_function('src/uri2env/uri.py', '_decode', 1, 2, 1).
python_function('src/uri2env/uri.py', 'uri_for_getv_profile', 2, 2, 1).
python_function('src/uri2env/uri.py', 'uri_for_getv_var', 3, 2, 1).
python_function('src/uri2env/uri.py', 'uri_for_env_file', 1, 2, 1).
python_function('src/uri2env/uri.py', 'uri_for_nlp2env_profile', 1, 2, 1).
python_function('src/uri2env/uri.py', 'is_env_uri', 1, 1, 2).
python_function('src/uri2env/uri.py', 'parse_env_uri', 1, 7, 6).
python_function('src/uri2env/uri.py', 'build_env_uri_index', 0, 2, 1).
python_function('tests/test_env_file.py', 'test_mask_secret', 0, 2, 1).
python_function('tests/test_env_file.py', 'test_load_and_save_roundtrip', 1, 4, 5).
python_function('tests/test_env_file.py', 'test_apply_text', 1, 3, 2).
python_function('tests/test_env_file.py', 'test_email_profile', 0, 5, 2).
python_function('tests/test_env_file.py', 'test_email_profile_missing', 0, 3, 1).
python_function('tests/test_mcp_tools.py', 'env_path', 2, 1, 2).
python_function('tests/test_mcp_tools.py', 'test_interfaces', 0, 5, 2).
python_function('tests/test_mcp_tools.py', 'test_set_email_via_tool', 1, 5, 5).
python_function('tests/test_mcp_tools.py', 'test_delete_via_tool', 1, 6, 5).

% ── Python Classes ───────────────────────────────────────
python_class('src/nlp2env/env_file.py', 'EnvFile').
python_method('EnvFile', 'load', 2, 10, 10).
python_method('EnvFile', 'get', 2, 1, 1).
python_method('EnvFile', 'set_many', 1, 7, 4).
python_method('EnvFile', 'delete', 1, 2, 0).
python_method('EnvFile', 'list_masked', 0, 2, 3).
python_method('EnvFile', 'backup', 1, 3, 5).
python_method('EnvFile', 'save', 0, 6, 11).
python_method('EnvFile', 'apply_text', 1, 7, 7).
python_class('src/nlp2env/toon_scenarios.py', 'ToonSection').
python_class('src/nlp2env/toon_scenarios.py', 'ToonScript').
python_class('src/nlp2env/toon_scenarios.py', 'PromptScenario').
python_method('PromptScenario', 'nl', 0, 1, 1).
python_method('PromptScenario', 'source', 0, 1, 2).
python_method('PromptScenario', 'tool', 0, 1, 1).
python_method('PromptScenario', 'after', 0, 1, 1).
python_method('PromptScenario', 'assert_configured', 0, 1, 2).
python_method('PromptScenario', 'inline_arguments', 0, 4, 1).
python_class('src/uri2env/materialize.py', 'MaterializeResult').
python_method('MaterializeResult', 'to_dict', 0, 1, 0).
python_class('src/uri2env/resolve.py', 'ResolvedEnvUri').
python_method('ResolvedEnvUri', 'to_dict', 0, 1, 0).

% ── Dependencies ─────────────────────────────────────────

% ── Makefile Targets ─────────────────────────────────────
makefile_target('SHELL', '').
makefile_target('PIP', '').
makefile_target('PYTEST', '').
makefile_target('help', '').
makefile_target('venv', '').
makefile_target('install', '').
makefile_target('install-mcp', '').
makefile_target('test', '').
makefile_target('test-mcp-live', '').
makefile_target('examples', '').
makefile_target('examples-multilang', '').
makefile_target('examples-all', '').

% ── Taskfile Tasks ───────────────────────────────────────

% ── Environment Variables ────────────────────────────────
env_variable('SMTP_HOST', 'smtp.example.com', 'Email / SMTP profile (nlp2dsl-worker compatible)').
env_variable('SMTP_PORT', '587', '').
env_variable('SMTP_USER', 'user@example.com', '').
env_variable('SMTP_PASSWORD', 'change-me', '').
env_variable('SMTP_TLS', '1', '').
env_variable('SMTP_FROM', 'user@example.com', '').
env_variable('SMTP_TIMEOUT', '30', '').

% ── TestQL Scenarios ─────────────────────────────────────
testql_scenario('generated-cli-tests.testql.toon.yaml', 'cli').

% ── Semantic Facts from SUMD.md ──────────────────────────
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

## Intent

MCP server for reading and writing .env variables (email/SMTP and custom keys)
