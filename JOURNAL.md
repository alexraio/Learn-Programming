# 📔 Diario di Bordo: Progetto TaskMaster API

Questo documento tiene traccia dell'avanzamento giorno per giorno, dei concetti appresi, delle sfide tecniche e delle decisioni architetturali del percorso verso uno sviluppo software professionale con Python, Antigravity IDE, Git e GitHub Actions.

---

## 📌 Indice delle Sessioni

* [Sessione 1 (2026-10-08): Fondamenta, Scaffolding & Setup IDE Antigravity](#sessione-1-2026-10-08-fondamenta-scaffolding--setup-ide-antigravity)
* [Sessione 2 (2026-10-08): Architettura Core, Modelli SQLAlchemy 2.0 & Auth JWT](#sessione-2-2026-10-08-architettura-core-modelli-sqlalchemy-20--auth-jwt)
* [Sessione 3 (2026-10-08): Testing Strategy, Laboratorio di Regression Testing & Parametri](#sessione-3-2026-10-08-testing-strategy-laboratorio-di-regression-testing--parametri)
* [Sessione 4 (2026-10-08): Git Flow, Pull Request Lifecycle & Pipeline CI/CD con GitHub Actions](#sessione-4-2026-10-08-git-flow-pull-request-lifecycle--pipeline-cicd-con-github-actions)
* [Sessione 5 (2026-10-08): Documentazione, Containerizzazione Docker & Rilascio Finale v1.0.0](#sessione-5-2026-10-08-documentazione-containerizzazione-docker--rilascio-finale-v100)

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

---

## Sessione 3 (2026-10-08): Testing Strategy, Laboratorio di Regression Testing & Parametri

### 🎯 Obiettivi della Sessione
1. Comprendere la distinzione metodologica tra test unitari, test di integrazione e **test di regressione**.
2. Eseguire un laboratorio pratico di **Regression Testing TDD**:
   * **Issue #101:** Riproduzione del bug di modifica di un task ARCHIVIATO (RED) ➔ Correzione con protezione immutabilità in `task_service.py` (GREEN).
   * **Issue #102:** Riproduzione del bug di data scadenza nel passato (RED) ➔ Correzione con `@field_validator` in `schemas/task.py` (GREEN).
3. Implementare test avanzati a matrice tramite **`@pytest.mark.parametrize`** (`tests/unit/test_parameterized_transitions.py`) per testare in modo esaustivo tutte le 8 transizioni legali e le transizioni vietate.
4. Eseguire la suite completa e verificare che tutti i 32 test superino i controlli con copertura $\ge 95\%$.

---

### 💡 Concetti Professionali Appresi

#### 1. Che cos'è il Regression Testing e perché è il pilastro del software duraturo?
* Nel software reale, ogni volta che un bug viene risolto ("fixed"), esiste un rischio concreto che modifiche future, refactoring o nuovi sviluppatori riaprano inavvertitamente quel bug (una **regressione**).
* **Flusso TDD per Bugfix:**
  1. Si scrive un test nella suite di regressione (`tests/regression/test_regression_<id>.py`) che riproduce esattamente le condizioni del bug.
  2. Si verifica che il test fallisca (fase **RED**): questo prova scientificamente l'esistenza del bug.
  3. Si scrive il codice correttivo minimo indispensabile (fase **GREEN**): il test passa.
  4. Il test **non viene mai cancellato**: rimane per sempre attivo nella suite automatizzata e nella CI/CD. Se chiunque reintroduce il bug in futuro, la pipeline blocca il rilascio all'istante.

#### 2. Test Parametrizzati con `@pytest.mark.parametrize`
* Invece di scrivere dozzine di funzioni di test quasi identiche, `@pytest.mark.parametrize` permette di alimentare un singolo corpo di test con una tabella/matrice di casi di input e output attesi.
* Nel nostro caso, abbiamo testato l'intera matrice della macchina a stati dei task (8 transizioni permesse + 4 combinazioni vietate) con sole due funzioni eleganti e leggibili.

#### 3. Organizzazione delle Fixture e Setup degli Stati
* Se un test verifica una transizione da `DONE` ad `ARCHIVED`, il task non può essere creato magicamente in `DONE` se le regole di business impongono che nasca in `TODO`. Il test deve orchestrare il percorso legale (`TODO -> IN_PROGRESS -> DONE`) per predisporre lo stato iniziale senza violare le invarianti di dominio.

---

### 🛠️ Stato del Progetto al Termine della Sessione 3
- Suite di test espansa a **32 test complessivi** eseguiti in soli 1.7 secondi.
- Suite dedicata ai test di regressione (`tests/regression/`) con marcatore `@pytest.mark.regression`.
- Copertura del codice salita al **95.68%**.
- 0 warning di linting o formattazione con Ruff; 0 errori di tipizzazione con Mypy.

---

### 📋 Checklist di Chiusura Sessione 3
- [x] Creazione suite `tests/regression/` con marcatore Pytest dedicato
- [x] Scrittura test fallente Issue #101 (immutabilità task archiviati) ➔ Fix nel servizio ➔ Test verde
- [x] Scrittura test fallente Issue #102 (validazione date scadenze passate) ➔ Fix nello schema ➔ Test verde
- [x] Implementazione test a matrice parametrizzati `@pytest.mark.parametrize`
- [x] Esecuzione verifica selettiva: `uv run pytest -m regression`
- [x] Esecuzione suite completa: 32 test passati con copertura al 95.68%
- [x] Commit Git semantico (`test: add regression test suite and advanced parameterized testing`)

---

## Sessione 4 (2026-10-08): Git Flow, Pull Request Lifecycle & Pipeline CI/CD con GitHub Actions

### 🎯 Obiettivi della Sessione
1. Creare la pipeline completa di automazione CI/CD con **GitHub Actions** (`.github/workflows/ci.yml`).
2. Configurare l'action ufficiale Astral `astral-sh/setup-uv@v5` con caching automatico delle dipendenze basato sul lockfile.
3. Definire i gatekeeper di build:
   - Ruff Linter & Formatter (`check` e `format --check`)
   - Mypy Static Type Checking
   - Pytest con verifica di copertura minima ($fail\_under = 80\%$)
   - Esecuzione obbligatoria della suite di regressione (`pytest -m regression`)
4. Creare il template standard per le Pull Request (`.github/pull_request_template.md`).
5. Simulare il ciclo di vita reale del Git Flow professionale:
   - Creazione branch isolato `feature/project-stats`
   - Sviluppo della nuova funzionalità (endpoint metriche e tasso di completamento progetti)
   - Verifica dei test locali sul branch
   - Commit semantico sul branch
   - Merge su `main` tramite simulazione PR (`--no-ff`) ed eliminazione del branch completato

---

### 💡 Concetti Professionali Appresi

#### 1. Perché la CI/CD deve girare su macchine "vergini" (Ubuntu Runner)?
* Il classico errore "sulla mia macchina funziona" (*works on my machine*) si verifica quando il computer dello sviluppatore ha file temporanei, variabili d'ambiente globali o librerie installate fuori dal lockfile.
* GitHub Actions avvia una macchina virtuale Ubuntu completamente pulita a ogni Push o Pull Request, clona il repository, installa solo ed esclusivamente ciò che è presente in `uv.lock` e lancia i test. Se passa in CI, c'è la certezza matematica che il software sia riproducibile ovunque.

#### 2. Caching delle Dipendenze con `astral-sh/setup-uv`
* Scaricare decine di pacchetti a ogni commit spreca minuti e banda. Con `enable-cache: true` e `cache-dependency-glob: "uv.lock"`, GitHub memorizza la cache delle wheel scaricate e la invalida solo se il file `uv.lock` viene effettivamente modificato. L'installazione delle dipendenze passa da 20 secondi a meno di 1 secondo.

#### 3. Git Flow e Pull Request Template
* Non si sviluppa mai direttamente sul ramo `main`. Il ramo `main` rappresenta lo stato stabile e pronto per il rilascio.
* L'apertura di un branch dedicato (`feature/...` o `bugfix/...`) consente di lavorare in sicurezza senza disturbare il codice principale.
* Il template di Pull Request (`pull_request_template.md`) costringe lo sviluppatore a fare una retrospettiva di autovalutazione prima di chiedere la revisione del codice (verifica checklist dei test, assenza di warning, aggiunta di regression test).

---

### 🛠️ Stato del Progetto al Termine della Sessione 4
- Pipeline GitHub Actions configurata e pronta all'uso su qualsiasi remote GitHub.
- Endpoint nuovo aggiunto: `GET /api/v1/projects/{id}/stats` con calcolo della `completion_rate`.
- Test suite espansa a **33 test passati** con **95.86% di copertura**.
- Albero Git arricchito con branch topologico e merge commit documentato (`git log --graph`).

---

### 📋 Checklist di Chiusura Sessione 4
- [x] Configurazione workflow `.github/workflows/ci.yml` (Ruff, Mypy, Pytest con coverage, Regression)
- [x] Creazione `.github/pull_request_template.md`
- [x] Creazione branch feature `feature/project-stats`
- [x] Implementazione endpoint `GET /api/v1/projects/{id}/stats` e test di integrazione
- [x] Commit semantico su branch feature
- [x] Merge PR con `--no-ff` su branch `main` ed eliminazione pulita del branch
- [x] Verifica integrità della suite completa sul branch `main` (33 test verdi, 95.86% coverage)

---

## Sessione 5 (2026-10-08): Documentazione, Containerizzazione Docker & Rilascio Finale v1.0.0

### 🎯 Obiettivi della Sessione
1. Creare un **Dockerfile multi-stage** di livello enterprise ottimizzato per la produzione con `uv`.
2. Configurare `.dockerignore` per isolare il context di compilazione Docker.
3. Riscrivere e completare il file `README.md` con badge, diagramma architetturale, tabella esaustiva di tutti gli endpoint API e comandi di quickstart locale e containerizzato.
4. Eseguire tutti i controlli di qualità e taggare formalmente la prima release di produzione: **`v1.0.0`**.
5. Stilare la retrospettiva finale delle competenze acquisite nel percorso.

---

### 💡 Concetti Professionali Appresi

#### 1. Multi-Stage Dockerfile con `uv`
* Nei container tradizionali, strumenti pesanti di build (compilatori C, package manager, cache) finivano nell'immagine finale, gonfiando la dimensione oltre 1 GB e aumentando la superficie di attacco CVE.
* Nel nostro approccio multi-stage:
  * Lo stage **builder** usa `ghcr.io/astral-sh/uv` per compilare il bytecode e risolvere le dipendenze in `.venv` sfruttando la cache dei layer.
  * Lo stage **runner** copia solo il virtual environment pulito dentro una base `python:3.12-slim-bookworm`, ottenendo un'immagine leggera e minimale.

#### 2. Sicurezza nei Container: Principio del Minimo Privilegio (Non-Root User)
* Non si eseguono mai processi web containerizzati come `root`.
* Nel Dockerfile abbiamo creato un utente dedicato `appuser` a bassi privilegi (`useradd -r -g appuser ...`), a cui appartiene l'applicazione (`--chown=appuser:appuser`). Se un aggressore riuscisse a compromettere l'API, non avrebbe permessi di root all'interno dell'ambiente containerizzato.

#### 3. Healthcheck Nativo Docker
* L'istruzione `HEALTHCHECK` interroga periodicamente l'endpoint `/health`. Questo consente a Docker Compose, Kubernetes o AWS ECS di sapere se l'applicazione è realmente viva ed escluderla dal routing di rete se bloccata.

---

### 🎓 Retrospettiva Finale del Percorso (Dall'Inizio alla Produzione)

In questo percorso abbiamo trasformato un'idea grezza in un prodotto software professionale completo:

1. **Pianificazione & Brainstorming disciplinato:** Definizione dell'Understanding Lock, mitigazione preventiva dei rischi e Decision Log archiviato in `DESIGN.md`.
2. **Ambiente IDE Moderno & AI Governance:** Configurazione di Antigravity IDE con `.agents/rules/` e skill dedicate per lavorare con gli LLM ("vibecoding" controllato) senza mai sacrificare la qualità.
3. **Tooling & Packaging Moderno:** Adozione di `uv` come moderno standard dell'ecosistema Python (risoluzione in millisecondi, virtualenv integrato, lockfile deterministico `uv.lock`).
4. **Architettura a Strati Pulita:** Separazione netta tra ORM (`models/`), schemi DTO (`schemas/`), logica di dominio (`services/`) e controller HTTP (`api/v1/`), con eccezioni di dominio personalizzate e gestione globale degli errori.
5. **Testing di Livello Industriale:**
   * Test isolati in-memory con SQLite `StaticPool` (< 2 secondi per l'intera suite).
   * Matrice di test parametrizzati con `@pytest.mark.parametrize`.
   * Suite permanente di **Regression Testing** con approccio TDD (Red-Green-Refactor) a guardia dei bug storici.
   * Copertura del codice verificata e mantenuta al **95.86%**.
6. **Git Flow & Continuous Integration (CI/CD):**
   * Flusso a branch tematici (`feature/...`) con merge non-fast-forward (`--no-ff`) e Conventional Commits.
   * Pipeline automatica su GitHub Actions con caching dei runner Ubuntu.
   * Template standardizzato per le Pull Request.
7. **Packaging & Rilascio:** Dockerfile multi-stage sicuro, documentazione `README.md` ricca e tagging semantico `v1.0.0`.

---

### 📋 Checklist di Chiusura Sessione 5
- [x] Creazione `Dockerfile` multi-stage con utente non-root `appuser` e `HEALTHCHECK`
- [x] Configurazione file `.dockerignore`
- [x] Documentazione finale esaustiva in `README.md`
- [x] Verifica globale di tutti i 33 test con 95.86% di coverage
- [x] Registrazione retrospettiva in `JOURNAL.md`
- [x] Creazione Git Release Tag `v1.0.0`




