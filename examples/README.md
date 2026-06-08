# nlp2env examples

Każdy przykład jest w **`examples/<category>/<name>/`**.

nlp2env **nie** zawiera własnego modelu NLP — agent (Cursor, todomat/orchestrator-auto) tłumaczy prompt na wywołanie narzędzia MCP. Przykłady poniżej symulują ten przepływ: prompt NL → wywołanie MCP → weryfikacja `.env`.

## Index

| Path | Cel |
|------|-----|
| `examples/write/smtp-email` | Profil SMTP przez `nlp2env_set_email` |
| `examples/write/apply-text` | Blok tekstu `KEY=value` przez `nlp2env_apply_text` |
| `examples/write/custom-keys` | Dowolne klucze przez `nlp2env_set` (JSON) |
| `examples/integrators/mcp-stdio` | Smoke test MCP stdio + config Cursor |
| `examples/integrators/todomat-dispatch` | Parsowanie komend `nlp2env_*` jak w todomat |

## Uruchom lokalnie

```bash
./examples/run-e2e.sh
```

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
