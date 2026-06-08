# SMTP email → `.env`

Symuluje typowy prompt użytkownika i zapis profilu SMTP do `.env`.

## Przykładowe prompty (NL)

| Prompt użytkownika | Oczekiwane wywołanie MCP |
|--------------------|--------------------------|
| „Ustaw skrzynkę SMTP: host smtp.gmail.com, użytkownik jan@firma.pl, port 587” | `nlp2env_set_email` z `host`, `user`, `port`, `password_env` |
| „Skonfiguruj email wysyłkowy dla nlp2dsl” | `nlp2env_set_email` + `nlp2env_email_status` |
| „Czy SMTP jest skonfigurowany?” | `nlp2env_email_status` |

Hasło **nie** powinno trafiać do czatu — użyj `password_env=SMTP_PASSWORD` (zmienna ustawiona przed startem MCP).

## Pliki

| Plik | Opis |
|------|------|
| `.env.example` | Szablon startowy (pusty profil) |
| `prompts.env` | Hasło testowe dla `password_env` (nie commituj prawdziwych sekretów) |
| `e2e.sh` | Symuluje prompt → MCP → weryfikuje `.env` |

## Uruchom

```bash
./e2e.sh
# lub
docker compose up --build --abort-on-container-exit
```

## Oczekiwany wynik w `.env`

```
SMTP_FROM=jan@firma.pl
SMTP_HOST=smtp.gmail.com
SMTP_PASSWORD=<z password_env>
SMTP_PORT=587
SMTP_TIMEOUT=30
SMTP_TLS=1
SMTP_USER=jan@firma.pl
```
