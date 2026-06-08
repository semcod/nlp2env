# nlp2env examples

Każdy przykład jest w **`examples/<category>/<name>/`**.

nlp2env **nie** zawiera własnego modelu NLP — agent (Cursor, todomat/orchestrator-auto) tłumaczy prompt na wywołanie narzędzia MCP. Przykłady poniżej symulują ten przepływ: prompt NL → wywołanie MCP → weryfikacja `.env`.

## Index

| Path | Cel |
|------|-----|
| `examples/write/smtp-email` | Profil SMTP — **`*.testql.toon.yaml`** (TestQL), logi |
| `examples/write/apply-text` | Blok tekstu `KEY=value` przez `nlp2env_apply_text` |
| `examples/write/custom-keys` | Dowolne klucze przez `nlp2env_set` (JSON) |
| `examples/integrators/mcp-stdio` | Smoke test MCP stdio + config Cursor |
| `examples/integrators/todomat-dispatch` | Parsowanie komend `nlp2env_*` jak w todomat |

## Uruchom lokalnie

```bash
make install-mcp
make examples              # szybkie (~30s): pytest + 5 scenariuszy inline (TestTOON)
make examples-multilang    # 26 promptów LLM/Ollama, 16 języków (~3 min)
make examples-all          # oba powyższe

# lub ręcznie:
./examples/run-e2e.sh
NLP2ENV_RUN_MULTILANG=1 ./examples/run-e2e.sh   # + test wielojęzyczny
```

Jeśli masz dwa venv (`.venv` i `venv/`), skrypt wybiera Python z zainstalowanym `mcp`.

### Test wielojęzyczny — `smtp-email-multilang.testql.toon.yaml`

Scenariusze w formacie **TestQL TestTOON** (`*.testql.toon.yaml`) — kompatybilne z ekosystemem [testql](https://github.com/oqlos/testql). DOQL (`app.doql.less`) importuje te pliki jako `TESTS`.

```bash
export SMTP_PASSWORD=e2e-test-secret-42
./examples/write/smtp-email/e2e-multilang.sh
tail examples/write/smtp-email/prompts-multilang.log.txt
```

Dokumentacja formatu: [`examples/write/smtp-email/README.md`](write/smtp-email/README.md).

## Uruchom w Dockerze (pojedynczy przykład)

```bash
docker compose -f examples/write/smtp-email/docker-compose.yml up --build --abort-on-container-exit
```

## Integracja z todomat

W `todomat` router `orchestrator-auto` rozpoznaje prefiks `nlp2env_*` i wywołuje serwer przez mcpo (`:8020`):

```
nlp2env_set_email: host=smtp.gmail.com, user=jan@firma.pl, password_env=SMTP_PASSWORD, port=587
nlp2env_email_status
nlp2env_list
```

Konfiguracja MCP w Cursor: `examples/integrators/mcp-stdio/mcp-config.cursor.json`.
