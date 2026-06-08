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
sumd_declared_file('app.doql.less', 'doql').
sumd_declared_file('testql-scenarios/generated-cli-tests.testql.toon.yaml', 'testql').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/logic.pl', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').
sumd_interface('cli', 'argparse').
sumd_interface('cli', '').
sumd_workflow('venv', 'manual').
sumd_workflow_step('venv', 1, 'test -x "$(PIP)" || $(PYTHON) -m venv "$(VENV)"').
sumd_workflow('install', 'manual').
sumd_workflow_step('install', 1, '$(PIP) install -e .').
sumd_workflow('install-mcp', 'manual').
sumd_workflow_step('install-mcp', 1, '$(PIP) install -e ".[mcp]"').
sumd_workflow('test', 'manual').
sumd_workflow_step('test', 1, '$(PYTEST) tests/ -v').
sumd_workflow('test-mcp-live', 'manual').
sumd_workflow_step('test-mcp-live', 1, './scripts/test-mcp-live.sh').
sumd_workflow('examples', 'manual').
sumd_workflow_step('examples', 1, './examples/run-e2e.sh').
sumd_workflow('examples-multilang', 'manual').
sumd_workflow('examples-all', 'manual').
sumd_workflow_step('examples-all', 1, 'echo "ALL EXAMPLES + MULTILANG OK"').

