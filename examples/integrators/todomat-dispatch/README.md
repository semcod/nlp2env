# todomat dispatch → nlp2env

Symuluje komendy wysyłane przez **todomat** (`orchestrator-auto`) z prefiksem `nlp2env_*`.
Parser jest zgodny z `todomat/domains/routing/mcp_dispatch.py`.

## Przykładowe prompty w czacie todomat

```
nlp2env_set_email: host=smtp.test.local, user=u@t.c, password_env=SMTP_PASSWORD, port=587
nlp2env_email_status
nlp2env_list
nlp2env_apply_text: text=APP_NAME=todomat-demo
```

## Uruchom

```bash
./e2e.sh
```

## Integracja z mcpo

Todomat wywołuje te same narzędzia przez HTTP OpenAPI (`http://localhost:8020/nlp2env/...`).
Ten przykład testuje warstwę parsowania + zapis `.env` bez uruchamiania mcpo.
