# Tekst KEY=value → `.env`

Symuluje prompt z wklejonym blokiem konfiguracji (agent wywołuje `nlp2env_apply_text`).

## Przykładowe prompty (NL)

| Prompt użytkownika | Oczekiwane wywołanie MCP |
|--------------------|--------------------------|
| „Zapisz do .env: `API_URL=https://api.firma.pl` i `LOG_LEVEL=debug`” | `nlp2env_apply_text` z blokiem tekstu |
| „Dodaj zmienne: SMTP_HOST=smtp.office365.com, SMTP_PORT: 587” | `nlp2env_apply_text` (obsługuje `=` i `key: value`) |

## Uruchom

```bash
./e2e.sh
```

## Oczekiwany wynik

```
API_URL=https://api.firma.pl
LOG_LEVEL=debug
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
```
