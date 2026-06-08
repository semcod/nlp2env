# JSON klucze → `.env`

Symuluje prompt o ustawieniu dowolnych zmiennych (agent wywołuje `nlp2env_set` z JSON).

## Przykładowe prompty (NL)

| Prompt użytkownika | Oczekiwane wywołanie MCP |
|--------------------|--------------------------|
| „Ustaw DATABASE_URL i REDIS_URL w .env” | `nlp2env_set` z `{"DATABASE_URL":"...", "REDIS_URL":"..."}` |
| „Pokaż co jest w .env” | `nlp2env_list` |

## Uruchom

```bash
./e2e.sh
```
