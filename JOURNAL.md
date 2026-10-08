# 📔 Diario di Bordo: Progetto TaskMaster API

Questo documento tiene traccia dell'avanzamento giorno per giorno, dei concetti appresi, delle sfide tecniche e delle decisioni architetturali del percorso verso uno sviluppo software professionale con Python, Antigravity IDE, Git e GitHub Actions.

---

## 📌 Indice delle Sessioni

* [Sessione 1 (2026-10-08): Fondamenta, Scaffolding & Setup IDE Antigravity](#sessione-1-2026-10-08-fondamenta-scaffolding--setup-ide-antigravity)
* [Sessione 2 (2026-10-08): Architettura Core, Modelli SQLAlchemy 2.0 & Auth JWT](#sessione-2-2026-10-08-architettura-core-modelli-sqlalchemy-20--auth-jwt)
* *Sessione 3: Testing Strategy & Laboratorio di Regression Testing (In programma)*
* *Sessione 4: Git Flow & Pipeline CI/CD con GitHub Actions (In programma)*
* *Sessione 5: Documentazione, Containerizzazione & Rilascio (In programma)*

---

## Sessione 1 (2026-10-08): Fondamenta, Scaffolding & Setup IDE Antigravity

### 🎯 Obiettivi della Sessione
1. Definire le specifiche architetturali e i requisiti non funzionali tramite il metodo di *Brainstorming*.
2. Inizializzare il repository Git locale sul branch `main` con un `.gitignore` completo.
3. Configurare la gestione pacchetti e l'ambiente virtuale con **`uv`** (standard moderno per Python).
4. Configurare l'ambiente di lavoro in **Antigravity IDE** con regole esplicite (`.agents/rules/`) e skill di workspace (`.agents/skills/`).
5. Costruire l'alberatura delle cartelle con layout a strati (`src/taskmaster/...` e `tests/...`).
6. Configurare gli strumenti di qualità del codice (**Ruff**, **Pytest**, **Mypy**) all'interno di `pyproject.toml`.
7. Eseguire il primo smoke test e registrare il primo commit semantico.

---

### 💡 Concetti Professionali Appresi

#### 1. Perché `uv` al posto di `pip` e `requirements.txt` tradizionali?
* **Velocità e determinismo:** `uv` risolve e installa pacchetti in millisecondi (scritto in Rust).
* **Gestione integrata del Python interpreter:** `uv` può scaricare e agganciare versioni specifiche di CPython (es. 3.12) senza dipendere da installazioni globali di sistema.
* **Lockfile deterministico (`uv.lock`):** A differenza di un `requirements.txt` che spesso tralascia versioni esatte delle sotto-dipendenze, `uv.lock` garantisce che il codice giri esattamente identico sul computer locale, sui computer dei colleghi e sui server di CI/CD in cloud.

#### 2. Perché la struttura `src/` (Src Layout)?
* Nel modello a radice piatta (`taskmaster/` nella root), i comandi Python rischiano di importare la cartella locale non installata invece del pacchetto verificato dal virtualenv, mascherando errori di packaging.
* Il layout `src/` costringe i test e gli strumenti a eseguire il codice attraverso l'ambiente virtuale, garantendo fedeltà rispetto a come il pacchetto si comporterà una volta installato o distribuito.

#### 3. Configurazione Agentica per Antigravity IDE (`.agents/`)
* Lo sviluppo assistito da AI ("vibecoding" controllato) richiede **guardrail**.
* La cartella `.agents/rules/` dice al modello: "Non puoi fare commit se i test falliscono; devi usare type hints; devi usare conventional commits". In questo modo l'AI agisce come un senior developer coscienzioso e non come un generatore di codice casuale.
* La skill `.agents/skills/taskmaster-workflow/` rende automatizzabili le procedure ripetitive (esecuzione della test suite, regression checking, verifica coverage).

---

### 🛠️ Stato del Progetto al Termine della Sessione 1
- Repository Git locale inizializzato su branch `main`.
- Dipendenze installate e congelate in `uv.lock` (FastAPI, SQLAlchemy, Pydantic, Pwdlib, Pytest, Ruff, Mypy).
- Struttura directory creata: `core`, `models`, `schemas`, `services`, `api/v1`.
- Suite test impostata: `unit`, `integration`, `regression` con fixtures in `tests/conftest.py`.
- Health check endpoint `/health` operativo e verificato dallo smoke test.

---

### 📋 Checklist di Chiusura Sessione 1
- [x] Inizializzazione Git e `.gitignore`
- [x] `uv init` con dipendenze di produzione e sviluppo
- [x] Configurazione `pyproject.toml` (Ruff + Pytest + Mypy)
- [x] Creazione regole e skill Antigravity in `.agents/`
- [x] Scaffolding moduli `src/taskmaster` e `tests/`
- [x] Smoke test verde con `uv run pytest`
- [x] Primo commit Git semantico (`feat: initial project scaffolding and tooling setup`)

---

## Sessione 2 (2026-10-08): Architettura Core, Modelli SQLAlchemy 2.0 & Auth JWT

### 🎯 Obiettivi della Sessione
1. Implementare la gestione delle impostazioni e variabili d'ambiente con `pydantic-settings` (`core/config.py` e `.env.example`).
2. Configurare SQLAlchemy 2.0 (`core/database.py`) con abilitazione esplicita dei pragma SQLite (Foreign Keys e WAL mode).
3. Definire eccezioni di dominio personalizzate ed exception handler centralizzati per prevenire leak di dettagli interni.
4. Costruire i modelli ORM dichiarativi `User`, `Project`, `Task` e gli enum tipizzati (`StrEnum`).
5. Realizzare gli schemi Pydantic V2 per la validazione di input e serializzazione sicura di output (senza esporre hash password).
6. Implementare il layer di sicurezza con hashing password moderno (**Argon2**) e firma/verifica token Bearer JWT.
7. Implementare i servizi di business pura (`user_service.py`, `project_service.py`, `task_service.py`) con macchina a stati formale per i task.
8. Creare i router API REST v1 (`auth`, `projects`, `tasks`) protetti da iniezione delle dipendenze (`get_current_user`, `get_db`).
9. Scrivere una suite completa di test unitari e di integrazione (17 test, copertura $\ge 95\%$).

---

### 💡 Concetti Professionali Appresi

#### 1. SQLAlchemy 2.0 & SQLite Pragmas (Foreign Keys & WAL Mode)
* In SQLite, per motivi di retrocompatibilità storica, i vincoli di **Foreign Key sono disabilitati di default** a meno che non si invochi `PRAGMA foreign_keys=ON;` all'apertura di ogni connessione. Usando `@event.listens_for(Engine, "connect")`, abbiamo garantito l'integrità referenziale automatica.
* La modalità **WAL (Write-Ahead Logging)** permette ai lettori di non bloccare gli scrittori e viceversa, eliminando gli errori di *database locked*.

#### 2. Hashing Password Moderno: Perché Argon2 invece di MD5 o SHA?
* Algoritmi generici come SHA-256 o MD5 sono progettati per essere velocissimi, il che li rende vulnerabili ad attacchi brute-force su GPU.
* **Argon2** (vincitore della Password Hashing Competition) è memory-hard e CPU-hard con fattore di costo configurabile, resistendo efficacemente ad attacchi hardware accelerati.

#### 3. Eccezioni di Dominio vs `raise HTTPException` Sparso
* Nei progetti amatoriali, il codice di business è spesso disseminato di `raise HTTPException(status_code=404, detail="...")`. Questo accoppia la logica di business al framework web HTTP.
* Con la nostra architettura, i servizi sollevano eccezioni di dominio pure (`EntityNotFoundError`, `InvalidStateTransitionError`, `DuplicateEntityError`). È FastAPI, tramite exception handler centralizzati in `main.py`, a tradurli in risposte JSON e codici HTTP semantici (404, 422, 409). I servizi rimangono testabili e riutilizzabili ovunque (CLI, worker, gRPC).

#### 4. Isolamento dei Test con SQLite In-Memory e `StaticPool`
* Nei test usiamo `sqlite:///:memory:` con `poolclass=StaticPool`. Ogni esecuzione dei test gira in RAM a velocità fulminea (< 1.1s per l'intera suite), azzerando lo stato tra un test e l'altro senza lasciare file sporchi su disco.
* Tramite `app.dependency_overrides[get_db]`, il client di test sostituisce al volo il DB reale con quello in memoria.

---

### 🛠️ Stato del Progetto al Termine della Sessione 2
- API REST v1 completamente operativa con documentazione OpenAPI/Swagger interattiva (`/docs`).
- Autenticazione JWT Bearer attiva (registrazione, login OAuth2 form e login JSON).
- Gestione Progetti e Task con segregazione multi-utente (nessun utente può vedere o modificare task altrui).
- Macchina a stati per i task con transizioni legali e controllate.
- Suite test estesa a **17 test (unitari + integrazione)** con **95.48% di copertura**.

---

### 📋 Checklist di Chiusura Sessione 2
- [x] Configurazione applicativa `core/config.py` e `.env.example`
- [x] Motore e sessioni DB in `core/database.py` con FK e WAL
- [x] Eccezioni di dominio ed exception handlers centralizzati
- [x] Modelli SQLAlchemy 2.0 `User`, `Project`, `Task` e `StrEnum`
- [x] Modulo di sicurezza con Argon2 e JWT in `core/security.py`
- [x] Schemi Pydantic V2 per tutte le entità
- [x] Servizi di dominio per utenti, progetti e task
- [x] Controller REST v1 con dipendenze e Bearer authentication
- [x] Test unitari e di integrazione verdi con copertura $\ge 95\%$
- [x] Commit Git semantico (`feat: implement core domain, sqlalchemy models, jwt auth and task management api`)

