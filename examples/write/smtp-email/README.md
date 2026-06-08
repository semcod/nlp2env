# SMTP email → `.env`

Symuluje typowe prompty użytkownika i zapis profilu SMTP do `.env`.

### `prompts-multilang.txt` — test wielojęzyczny NL → `.env`

Plik **`prompts-multilang.txt`** to zestaw **26 scenariuszy testowych** zapisanych w formacie `[prompt:id]` + pola klucz=wartość. Każdy scenariusz zawiera:

- **`lang=`** — kod języka promptu (pl, en, de, fr, es, ja, zh, ar, …)
- **`source=llm`** — prompt NL jest tłumaczony przez LLM (Ollama lub OpenRouter) na wywołanie MCP `nlp2env_set_email`
- **`nl=`** — treść promptu w danym języku (np. polski, niemiecki, japoński, arabski)
- **`expect=`** — oczekiwane linie w wygenerowanym `.env` (walidacja po zapisie)

**Czym różni się od `prompts.txt`?**

| | `prompts.txt` | `prompts-multilang.txt` |
|---|---------------|-------------------------|
| Liczba scenariuszy | 5 (mix inline + 1× LLM) | 26 (wszystkie `source=llm`) |
| Języki | głównie PL + 1× LLM | **16+ języków** |
| Cel | szybki smoke test (~30 s) | regresja wielojęzycznego NLP → MCP → `.env` (~3 min) |
| Runner | `./e2e.sh` | `./e2e-multilang.sh` / `make examples-multilang` |

**Przepływ (jeden blok):**

```
nl= (dowolny język)
  → Ollama/OpenRouter (JSON: tool + arguments)
  → nlp2env_set_email (MCP)
  → workdir-multilang/<prompt-id>/.env
  → sprawdzenie expect=SMTP_HOST/USER/PORT
  → wpis w prompts-multilang.log.txt
```

**Pliki powiązane:**

| Plik | Opis |
|------|------|
| `prompts-multilang.txt` | definicja 26 promptów (edytuj, aby dodać języki/scenariusze) |
| `e2e-multilang.sh` | uruchamia runner z `NLP2ENV_FORCE_OLLAMA=1` |
| `prompts-multilang.log.txt` | log wyników (append po każdym runie) |
| `workdir-multilang/<id>/.env` | wygenerowane pliki `.env` per scenariusz |

**Przykład bloku:**

```
[prompt:ja-gmail]
lang=ja
source=llm
nl=GmailのSMTPを設定してください。ホスト smtp.gmail.com、ユーザー tanaka@kaisha.jp、ポート 587
expect=SMTP_HOST=smtp.gmail.com
expect=SMTP_USER=tanaka@kaisha.jp
expect=SMTP_PORT=587
```

nlp2env-mcp **nie czyta** tego pliku — używa go wyłącznie warstwa testowa (`examples/lib/run_smtp_prompts.py`). W produkcji rolę `nl=` pełni użytkownik (Cursor, todomat), a tłumaczenie robi agent/LLM.

## Format scenariuszy (TestQL TestTOON)

Prompty e2e są w plikach **`*.testql.toon.yaml`** (standard **testql**, nie doql):

| Plik | Opis |
|------|------|
| `smtp-email-inline.testql.toon.yaml` | 5 scenariuszy inline/LLM — domyślny `./e2e.sh` |
| `smtp-email.testql.toon.yaml` | 22 scenariusze LLM w wielu językach |
| `smtp-email-multilang.testql.toon.yaml` | 26 scenariuszy wielojęzycznych |

**DOQL** (`app.doql.less`) deklaruje *co* buduje projekt i importuje testy; **TestQL** opisuje *jak* testować NL → `.env`.

Przykład:

```yaml
# SCENARIO: smtp-email-inline
# TYPE: nlp2env
# VERSION: 1.0

PROMPTS[1]{id, lang, source, nl, tool, after, assert_configured}:
  gmail-basic, pl, inline, "Ustaw SMTP...", nlp2env_set_email, -, false

PROMPT_FIELDS[2]{prompt_id, key, value}:
  gmail-basic, host, smtp.gmail.com
  gmail-basic, user, jan@firma.pl

ASSERT_ENV[1]{prompt_id, expect}:
  gmail-basic, SMTP_HOST=smtp.gmail.com
```

Legacy `prompts.txt` nadal działa, ale preferowany jest TestTOON.

## uri2env + nlp2uri

Pakiet **`uri2env`** (w tym repo) materializuje URI `env://` do pliku `.env`:

| URI | Działanie |
|-----|-----------|
| `env://nlp2env/smtp?dest=.env` | Zapis profilu SMTP z `SMTP_*` w środowisku |
| `env://getv/{cat}/{profile}` | Eksport profilu getv → `.env` |
| `env://file/{path}` | Kopia pliku `.env` |

Integracja z [nlp2uri](https://github.com/semcod/nlp2uri): `pip install nlp2uri[envmap]` → `NLP2URIService.materialize_env()`.

## Pliki promptów (skrót)

| Plik | Opis |
|------|------|
| `smtp-email-inline.testql.toon.yaml` | 5 scenariuszy — szybki test `./e2e.sh` |
| `smtp-email-multilang.testql.toon.yaml` | 26 scenariuszy wielojęzycznych |
| `prompts.log.txt` | Log po `./e2e.sh` |
| `prompts-multilang.log.txt` | Log po `./e2e-multilang.sh` |
| `.env.example` | Szablon startowy |

Hasło testowe (poza repo):

```bash
export SMTP_PASSWORD=e2e-test-secret-42
```

## Backend LLM (prompty `source=llm`)

| Warunek | Backend |
|---------|---------|
| `OPENROUTER_API_KEY` ustawiony | **OpenRouter** (`LLM_MODEL` lub domyślny qwen3-coder) |
| brak klucza, Ollama działa | **Ollama** (`PFIX_MODEL` / `ollama/gemma4:e4b`) |
| brak obu | tylko `source=inline` w `prompts.txt`; `source=llm` → FAIL w logu |

**nlp2env-mcp sam nie używa LLM** — tłumaczenie NL→MCP robi warstwa przykładu (agent / ten runner).

## Uruchom

```bash
export SMTP_PASSWORD=e2e-test-secret-42
./e2e.sh
cat prompts.log.txt
```

Docker:

```bash
docker compose up --build --abort-on-container-exit
```

## Test wielojęzyczny (26 promptów, Ollama LLM)

```bash
export SMTP_PASSWORD=e2e-test-secret-42
./e2e-multilang.sh
tail prompts-multilang.log.txt
```

Pliki: `prompts-multilang.txt`, `prompts-multilang.log.txt`, `workdir-multilang/<prompt-id>/.env`

Szczegóły formatu i celu pliku: sekcja **`prompts-multilang.txt`** w tym README.

## Format `prompts.txt`

```
[prompt:gmail-basic]
nl=Ustaw skrzynkę SMTP: host smtp.gmail.com, ...
source=inline
tool=nlp2env_set_email
host=smtp.gmail.com
...
expect=SMTP_HOST=smtp.gmail.com
```

## Oczekiwany wynik

Każdy blok ma własny katalog `workdir/<prompt-id>/.env` (lub `after=` współdzieli stan).
