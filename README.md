# nlp2env


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.4-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.70-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-5.2h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.6993 (4 commits)
- 👤 **Human dev:** ~$516 (5.2h @ $100/h, 30min dedup)

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
| `nlp2env_delete` | Usuń klucze (comma-separated) z `.env` |
| `nlp2env_backup` | Kopia `.env` → `.nlp2env/backups/` |
| `nlp2env_email_status` | Czy SMTP jest kompletny |
| `nlp2env_set_api` | Zapis kluczy API (OpenAI, Anthropic, Groq, HF) |
| `nlp2env_api_status` | Czy jakieś klucze API są skonfigurowane |
| `nlp2env_set_db` | Zapis profilu bazy danych (Postgres, Redis, Mongo) |
| `nlp2env_db_status` | Czy profil bazy danych jest kompletny |
| `nlp2env_generate_key` | Generuj nowy klucz szyfrowania Fernet |
| `nlp2env_encrypt` | Szyfruj plaintext → `enc:<base64>` |
| `nlp2env_decrypt` | Odszyfruj `enc:<base64>` → plaintext |
| `nlp2env_load_multi` | Połącz `.env` + `.env.{suffix}` (override wins) |
| `nlp2env_list_files` | Lista plików `.env*` w katalogu projektu |

## Profil email (nlp2dsl)

Klucze zgodne z `nlp2dsl` worker:

```
SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_TLS, SMTP_FROM, SMTP_TIMEOUT
```

Po zapisie zrestartuj worker:

```bash
docker compose -f ~/github/wronai/nlp2dsl/docker-compose.yml restart worker
```

## Profil API keys

Klucze LLM/API zapisywane przez `nlp2env_set_api`:

```bash
OPENAI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY, HUGGINGFACE_API_TOKEN
```

## Profil database

Klucze PostgreSQL, Redis i MongoDB zapisywane przez `nlp2env_set_db`:

```bash
POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
REDIS_URL, REDIS_HOST, REDIS_PORT
MONGO_URI
```

`nlp2env_db_status` sprawdza czy PostgreSQL jest kompletny (host, db, user, password) oraz czy Redis/Mongo są skonfigurowane.

## Wiele `.env` (suffix)

`resolve_env_path` obsługuje suffix — automatycznie wybiera `.env.local`, `.env.production`:

```bash
# env_file.py
resolve_env_path(suffix="local")      # → ./.env.local
resolve_env_path(suffix="production") # → ./.env.production
```

MCP tool `nlp2env_load_multi` ładuje base `.env` a potem overlay `.env.{suffix}` (override nadpisuje base):

```bash
# .env
SMTP_HOST=prod.server.com
SMTP_PORT=587

# .env.local
SMTP_HOST=localhost
SMTP_PORT=2525
```

`nlp2env_load_multi(suffix="local")` → `SMTP_HOST=localhost`, `SMTP_PORT=2525`

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

## Walidacja formatów

`nlp2env_set` i `nlp2env_set_email` automatycznie walidują wartości:

| Format | Klucze (suffix/prefix) | Przykład poprawny |
|--------|------------------------|-------------------|
| Email | `_EMAIL`, `_USER` | `jan@firma.pl` |
| Host/IP | `_HOST`, `SERVER`, `ADDRESS` | `smtp.gmail.com`, `192.168.1.1` |
| Port | `_PORT`, `_TIMEOUT` | `587`, `30` |
| URL | `_URL` | `https://api.example.com` |
| Bool | `_TLS`, `_ENABLED` | `1`, `true`, `yes`, `on` |
| API key | `_API_KEY`, `_TOKEN` | `sk-...`, `gsk-...`, `hf_...` |

Błędy walidacji zatrzymują zapis i zwracają `validation_errors` w odpowiedzi MCP.

## Szyfrowanie wartości

Wartości w `.env` mogą być szyfrowane AES-128-CBC + HMAC (Fernet):

```bash
# Generuj klucz
nlp2env_generate_key()  # → zapisz do ~/.nlp2env/key lub NLP2ENV_MASTER_KEY

# Szyfruj
nlp2env_encrypt("sekret123")  # → "enc:gAAAAAB..."

# Zapisz zaszyfrowane do .env
nlp2env_set('{"API_KEY": "enc:gAAAAAB..."}')

# Odszyfruj (automatycznie przy odczycie przez MCP)
nlp2env_decrypt("enc:gAAAAAB...")  # → "sekret123"
```

**Klucz** — 32 bajty base64 (44 znaki), generowany przez `generate_key()` lub hasło przez `_derive_key()`.

**Maskowanie** — zaszyfrowane wartości wyświetlane jako `enc:****wxyz`.

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
