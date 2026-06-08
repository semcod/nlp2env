# nlp2env


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.3-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.44-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-3.0h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.4415 (2 commits)
- 👤 **Human dev:** ~$300 (3.0h @ $100/h, 30min dedup)

Generated on 2026-06-08 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

MCP server do odczytu i zapisu pliku `.env` — w tym profilu **SMTP/email** dla workflow `send_email` (nlp2dsl-worker).

## Instalacja

```bash
cd ~/github/semcod/nlp2env
pip install -e ".[mcp]"
```

## Uruchomienie MCP

```bash
export NLP2ENV_ENV_FILE=~/github/wronai/todomat/.env   # opcjonalnie
nlp2env-mcp
```

## Narzędzia MCP

| Tool | Opis |
|------|------|
| `nlp2env_interfaces` | Metadane, ścieżka `.env`, profile |
| `nlp2env_list` | Lista kluczy (sekrety zamaskowane) |
| `nlp2env_get` | Odczyt kluczy (comma-separated) |
| `nlp2env_set` | Zapis z JSON `{"SMTP_HOST":"..."}` |
| `nlp2env_set_email` | Zapis profilu SMTP (host, user, password, …) |
| `nlp2env_apply_text` | Parsuj bloki `KEY=value` z tekstu |
| `nlp2env_backup` | Kopia `.env` → `.nlp2env/backups/` |
| `nlp2env_email_status` | Czy SMTP jest kompletny |

## Profil email (nlp2dsl)

Klucze zgodne z `nlp2dsl` worker:

```
SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_TLS, SMTP_FROM, SMTP_TIMEOUT
```

Po zapisie zrestartuj worker:

```bash
docker compose -f ~/github/wronai/nlp2dsl/docker-compose.yml restart worker
```

## Cursor (`mcp.json`)

```json
{
  "mcpServers": {
    "nlp2env": {
      "command": "nlp2env-mcp",
      "env": {
        "NLP2ENV_ENV_FILE": "/home/tom/github/wronai/todomat/.env"
      }
    }
  }
}
```

## uri2env

Pakiet `uri2env` (w `src/uri2env/`) mapuje URI `env://` na plik `.env` — używany przez **nlp2uri** do adresowania konfiguracji:

```bash
pip install -e ".[mcp,nlp2uri]"
uri2env materialize --uri 'env://nlp2env/smtp?dest=./.env'
```

W nlp2uri: `resolve_env()` → `env://…` → `materialize_env()`.

## Testy

```bash
pip install -e ".[dev]"
pytest
make examples              # szybkie e2e
make examples-multilang    # 26 promptów LLM/Ollama (16 języków)
make examples-all          # oba
```

**`prompts-multilang.txt`** (`examples/write/smtp-email/`) — 26 wielojęzycznych promptów NL testujących ścieżkę LLM → MCP → `.env`; uruchamiane przez `make examples-multilang`. Opis: [`examples/write/smtp-email/README.md`](examples/write/smtp-email/README.md).

Przykłady NL → `.env` (Docker + README): [`examples/README.md`](examples/README.md).


## License

Licensed under Apache-2.0.
