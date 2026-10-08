# 🚀 TaskMaster API

[![Python 3.12](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Astral uv](https://img.shields.io/badge/package%20manager-uv-de5fe9.svg)](https://docs.astral.sh/uv/)
[![Ruff](https://img.shields.io/badge/linter-Ruff-orange.svg)](https://docs.astral.sh/ruff/)
[![Coverage](https://img.shields.io/badge/coverage-95.86%25-brightgreen.svg)]()
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF.svg)]()

> Un'API REST solida, sicura e modulare per la gestione di task e progetti multi-utente.  
> Sviluppata in **Antigravity IDE** come caso di studio end-to-end per padroneggiare le moderne pratiche di ingegneria del software: architettura a strati, dipendenze deterministiche con `uv`, regression testing e pipeline di CI/CD.

---

## 📖 Documentazione e Diario del Progetto

* 📋 **Specifiche & Decision Log (ADR):** [DESIGN.md](file:///Users/alessio/Insync/ballarin.alessio@gmail.com/GoogleDrive/programming/Learn-Programming/DESIGN.md)
* 📔 **Diario di Bordo & Tracciamento Sessioni:** [JOURNAL.md](file:///Users/alessio/Insync/ballarin.alessio@gmail.com/GoogleDrive/programming/Learn-Programming/JOURNAL.md)
* 🤖 **Regole Antigravity IDE & AI Governance:** [.agents/rules/coding_standards.md](file:///Users/alessio/Insync/ballarin.alessio@gmail.com/GoogleDrive/programming/Learn-Programming/.agents/rules/coding_standards.md)
* 🛠️ **Skill Locale di Automazione:** [.agents/skills/taskmaster-workflow/SKILL.md](file:///Users/alessio/Insync/ballarin.alessio@gmail.com/GoogleDrive/programming/Learn-Programming/.agents/skills/taskmaster-workflow/SKILL.md)

---

## 🏛️ Architettura del Software (Layered Architecture)

```text
HTTP Request (Client / Swagger UI)
       │
       ▼
┌────────────────────────────────────────────────────────┐
│  API Routers (src/taskmaster/api/v1/)                  │
│  - auth.py, projects.py, tasks.py                      │
│  - Iniezione Dipendenze: get_current_user, get_db      │
└──────────────────────────┬─────────────────────────────┘
                           │ Valida DTO (Pydantic V2)
                           ▼
┌────────────────────────────────────────────────────────┐
│  Domain Services (src/taskmaster/services/)            │
│  - user_service, project_service, task_service         │
│  - Macchina a stati dei Task & Vincoli di Dominio      │
│  - Solleva Eccezioni di Dominio (TaskMasterError)      │
└──────────────────────────┬─────────────────────────────┘
                           │ Esegue transazioni ORM
                           ▼
┌────────────────────────────────────────────────────────┐
│  Persistence Layer (src/taskmaster/models/)            │
│  - SQLAlchemy 2.0 (User, Project, Task)                │
│  - SQLite Engine con WAL Mode e PRAGMA foreign_keys    │
└────────────────────────────────────────────────────────┘
```

---

## 📡 Tabella degli Endpoint API (v1)

Tutte le rotte protette richiedono l'header `Authorization: Bearer <token>`.

| Metodo | Endpoint | Descrizione | Auth Richiesta |
| :--- | :--- | :--- | :---: |
| `GET` | `/health` | Health check del servizio | No |
| `POST` | `/api/v1/auth/register` | Registrazione nuovo utente (password con hash Argon2) | No |
| `POST` | `/api/v1/auth/login` | Login form standard OAuth2 (Swagger UI compatible) | No |
| `POST` | `/api/v1/auth/login/json` | Login con payload JSON | No |
| `POST` | `/api/v1/projects` | Creazione di un nuovo progetto | **Sì** |
| `GET` | `/api/v1/projects` | Elenco progetti di proprietà dell'utente | **Sì** |
| `GET` | `/api/v1/projects/{id}` | Dettagli di un singolo progetto | **Sì** |
| `PATCH`| `/api/v1/projects/{id}` | Modifica anagrafica del progetto | **Sì** |
| `DELETE`|`/api/v1/projects/{id}`| Eliminazione progetto e task in cascata | **Sì** |
| `GET` | `/api/v1/projects/{id}/stats` | Metriche e tasso di completamento (`completion_rate`) | **Sì** |
| `POST` | `/api/v1/tasks` | Creazione task associato a un progetto | **Sì** |
| `GET` | `/api/v1/tasks` | Elenco task con filtri (`project_id`, `status`) | **Sì** |
| `GET` | `/api/v1/tasks/{id}` | Dettagli di un singolo task | **Sì** |
| `PATCH`| `/api/v1/tasks/{id}` | Modifica titolo, descrizione, priorità, scadenza | **Sì** |
| `PATCH`| `/api/v1/tasks/{id}/status` | Transizione di stato controllata (`TODO`, `IN_PROGRESS`, `DONE`, `ARCHIVED`) | **Sì** |
| `DELETE`|`/api/v1/tasks/{id}` | Eliminazione definitiva di un task | **Sì** |

---

## ⚡ Quickstart Locale (con `uv`)

### 1. Installazione di `uv`
Se non lo hai già installato:
```bash
brew install uv
```

### 2. Sincronizzazione dell'ambiente
Crea e popola automaticamente il virtualenv con le versioni esatte bloccate in `uv.lock`:
```bash
uv sync
```

### 3. Avvio dell'Applicazione
```bash
uv run uvicorn taskmaster.main:app --reload --port 8000
```
* **API root:** `http://127.0.0.1:8000`
* **Swagger UI interattiva:** `http://127.0.0.1:8000/docs`
* **Documentazione ReDoc:** `http://127.0.0.1:8000/redoc`

---

## 🧪 Esecuzione Test, Regressioni & Controlli Qualità

```bash
# Linting ultra-rapido con Ruff
uv run ruff check .

# Controllo formattazione
uv run ruff format --check .

# Controllo statico dei tipi con Mypy
uv run mypy src tests

# Esecuzione completa di tutti i 33 test con report di copertura (soglia minima 80%)
uv run pytest --cov=src/taskmaster --cov-report=term-missing

# Esecuzione esclusiva dei test di regressione storici
uv run pytest -m regression -v
```

---

## 🐳 Esecuzione con Docker

L'applicazione include un `Dockerfile` multi-stage pronto per la produzione con utente non-root `appuser` e `HEALTHCHECK` integrato:

```bash
# Build dell'immagine Docker
docker build -t taskmaster-api:latest .

# Avvio del container
docker run -d --name taskmaster -p 8000:8000 taskmaster-api:latest

# Verifica dello stato di salute
docker ps
curl http://localhost:8000/health
```

---

## 🤖 Cooperazione con Antigravity IDE & AI
Il progetto include una configurazione native in `.agents/` che impone:
1. Standard di codifica con type annotations su ogni funzione.
2. Divieto assoluto di commit o merge su codice con test rossi o warning.
3. Obbligo di test di regressione riproducibile prima di qualsiasi bugfix.
4. Messaggi di commit semantici secondo la convenzione *Conventional Commits*.
