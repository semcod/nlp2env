# MCP stdio integrator

Smoke test serwera `nlp2env-mcp` (JSON-RPC przez stdin/stdout).

## Narzędzia MCP

- `nlp2env_interfaces` — metadane i ścieżka `.env`
- `nlp2env_set_email` — profil SMTP
- `nlp2env_apply_text` — parsowanie bloku tekstu
- `nlp2env_set` — zapis JSON
- `nlp2env_list` / `nlp2env_get` — odczyt
- `nlp2env_email_status` — kompletność SMTP
- `nlp2env_backup` / `nlp2env_delete` — zarządzanie

## Cursor config

Szablon: [`mcp-config.cursor.json`](mcp-config.cursor.json)

```json
{
  "mcpServers": {
    "nlp2env": {
      "command": "nlp2env-mcp",
      "env": {
        "NLP2ENV_ENV_FILE": "${workspaceFolder}/.env"
      }
    }
  }
}
```

## Uruchom

```bash
./e2e.sh
```
