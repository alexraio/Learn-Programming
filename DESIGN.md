# Progetto TaskMaster API: Design Architetturale & Programma Professionale

Questo documento definisce le specifiche architetturali, i requisiti, il registro delle decisioni (Decision Log) e il programma di studio passo-passo per il progetto **TaskMaster API**, sviluppato all'interno di Antigravity IDE con Python, Git e GitHub Actions.

---

## 1. Understanding Summary (Sintesi Requisiti)

* **Prodotto:** Un'API REST solida e modulare per la gestione di task e progetti multi-utente.
* **Scopo:** Servire da percorso formativo pratico ("imparare facendo") per assimilare le pratiche professionali di ingegneria del software: architettura a strati, isolamento delle dipendenze con `uv`, standard di qualità (PEP 8 / Ruff), configurazione IDE agentica, testing multilivello (incluso **Regression Testing**), versionamento con Git e pipeline di **CI/CD con GitHub Actions**.
* **Destinatario:** Sviluppatore con solide basi di programmazione che desidera elevare il proprio metodo operativo a standard professionali dell'industria.
* **Non-Goals:**
  * Nessun frontend monolitico o SPA complesso (focus rigoroso su backend, architettura, automazione e affidabilità).
  * Nessuna infrastruttura cloud complessa o servizi a pagamento (tutto eseguibile localmente su macOS e su runner GitHub Actions gratuiti).
  * Nessuna complicazione distribuita superflua (microservizi, code Celery, cluster Redis): rispetto ferreo del principio *YAGNI*.

---

## 2. Assunzioni e Vincoli Non Funzionali

1. **Stack Tecnologico:** Python 3.12+, FastAPI, Pydantic V2, SQLAlchemy 2.0, SQLite (WAL mode), `uv` per il package management.
2. **Performance:** Latenze sub-50ms per le chiamate CRUD ordinarie; database locale compatto e veloce.
3. **Sicurezza:** Password memorizzate con hash sicuro, autenticazione stateless basata su token Bearer JWT con rotazione temporale.
4. **Qualità & Stile:** Formattazione e linting con **Ruff** integrati nel file di configurazione `pyproject.toml`.
5. **Testing & Copertura:** Framework `pytest` con copertura target $\ge 85\%$, con partizione netta tra test unitari, test di integrazione e suite dedicata al **Regression Testing**.
6. **Tracciamento:** File persistente `JOURNAL.md` per registrare i progressi, le scoperte e i punti di ripresa giorno per giorno.

---

## 3. Gestione Rischi (Risk Assessment)

| Rischio Identificato | Impatto | Mitigazione |
| :--- | :--- | :--- |
| **Deriva verso l'over-engineering** (troppi file/pattern per un'app compagna) | Alto | Adozione rigorosa della *Layered Architecture* pragmatica: solo i file e gli strati necessari senza astrazioni premature. |
| **Concorrenza e lock su SQLite durante i test** | Medio | Abilitazione della modalità WAL e utilizzo di SQLite in memoria (`:memory:`) con sessioni isolate per la suite di test. |
| **Allucinazioni o deviazioni dell'AI durante lo sviluppo (vibecoding)** | Medio | Definizione di regole di progetto in `.agents/rules/` che impongono la verifica dei test prima di ogni commit e standard di codice immutabili. |
| **Mancanza di continuità tra sessioni su più giorni** | Medio | Utilizzo rigoroso del diario di bordo `JOURNAL.md` con checklist esplicite di avvio e chiusura sessione. |

---

## 4. Decision Log Completo

| ID | Decisione | Opzioni Considerate | Scelta | Motivazione |
| :---: | :--- | :--- | :--- | :--- |
| **DEC-01** | **Dominio Applicativo** | Task Manager, Budget Tracker, Library, Inventory | **Task & Project Manager** | Eccellente per relazioni 1-a-N, N-a-N, transizioni di stato e scenari concreti di regressione. |
| **DEC-02** | **Tipo di Progetto** | REST API, CLI, Full-Stack, Worker | **REST API (FastAPI)** | Consente di esplorare validazione, modelli, contratti OpenAPI, sicurezza e CI in modo standard. |
| **DEC-03** | **Package & Tooling** | uv, Poetry, pip/venv | **uv** | Moderno standard dell'ecosistema Python: velocità elevata, virtual environment nativo e lockfile deterministico. |
| **DEC-04** | **Autenticazione** | JWT Bearer, API Key, Nessuna | **JWT Bearer Token** | Standard industriale essenziale per mostrare sicurezza stateless e test con utenti autenticati. |
| **DEC-05** | **Architettura del Codice** | Layered Modular, Vertical Slice, Hexagonal/Clean | **Layered Modular (`src/`)** | Separazione limpida (Core, Models, Schemas, Services, API) con massimo rapporto chiarezza/manutenibilità. |
| **DEC-06** | **Configurazione IDE / AI** | Setup generico vs Antigravity Native | **Antigravity `.agents/`** | Regole esplicite per l'LLM, standard di qualità automatizzati e tracciamento continuo nel journal. |
| **DEC-07** | **Strategia di Gestione Errori** | `raise HTTPException` sparso vs Eccezioni di Dominio centralizzate | **Eccezioni di Dominio centralizzate** | Servizi indipendenti dal framework web, testabili senza contesto HTTP e risposte standardizzate. |
| **DEC-08** | **Isolamento Regressione** | Test uniti indistintamente vs Cartella dedicata | **Suite `tests/regression/` dedicata** | Evidenza chiara della cronologia dei bugfix e protezione permanente contro la riapertura di bug risolti. |
| **DEC-09** | **Database di Test** | DB su disco vs SQLite in memoria | **SQLite `:memory:`** | Esecuzione istantanea della test suite (< 2 secondi) e zero residui tra le esecuzioni. |
| **DEC-10** | **Pipeline CI/CD** | Script bash manuali vs GitHub Actions | **GitHub Actions (`ci.yml`)** | Standard industriale riproducibile su macchine vergini a ogni Pull Request o Push. |

---

## 5. Architettura e Struttura del Repository

```text
Learn-Programming/
├── .agents/                      # Configurazione Antigravity IDE
│   ├── rules/                    # Regole di comportamento e codifica per l'AI
│   └── skills/                   # Skill locali per task automatici (es. test-checker, journal)
├── .github/
│   └── workflows/
│       └── ci.yml                # CI/CD: linting (Ruff), type check, test suite
├── src/taskmaster/
│   ├── core/                     # Configurazione (Settings), DB session, JWT/Security
│   ├── models/                   # Modelli relazionali SQLAlchemy (User, Project, Task)
│   ├── schemas/                  # Schemi Pydantic V2 per validazione I/O e serializzazione
│   ├── services/                 # Business logic pura (transizioni di stato, permessi, scadenze)
│   ├── api/v1/                   # Endpoint FastAPI suddivisi per risorsa (auth, projects, tasks)
│   └── main.py                   # Entry point applicativo, lifespan e registrazione router
├── tests/
│   ├── conftest.py               # Fixtures condivise (DB in memoria, client HTTP, token)
│   ├── unit/                     # Test unitari per servizi e funzioni di utilità
│   ├── integration/              # Test integrazione endpoint API e query database
│   └── regression/               # Suite dedicata ai test di regressione (bug fix storici)
├── docs/                         # Documentazione architetturale e guide
├── pyproject.toml                # Metadati, dipendenze uv e configurazione Ruff/Pytest
├── uv.lock                       # Lockfile deterministico delle dipendenze
├── JOURNAL.md                    # Diario di bordo e registro avanzamento sessioni
├── DESIGN.md                     # Questo documento di design e roadmap
└── README.md                     # Documentazione per l'avvio e guida del progetto
```

---

## 6. Il Programma Didattico Passo-Passo (Le 5 Fasi)

### 🔹 Fase 1: Setup dell'Ambiente, Scaffolding & Antigravity IDE
* Inizializzazione del repository Git con file `.gitignore` professionale.
* Configurazione dell'ambiente virtuale e gestione pacchetti con `uv` (`pyproject.toml`).
* Configurazione delle regole per l'IDE Antigravity (`.agents/rules/` o `GEMINI.md`) per guidare la cooperazione con l'AI.
* Creazione della struttura delle directory e inizializzazione del diario di bordo `JOURNAL.md`.

### 🔹 Fase 2: Architettura Core, Modelli & Sicurezza
* Configurazione delle variabili d'ambiente con `pydantic-settings`.
* Configurazione del database SQLite con SQLAlchemy 2.0 e session management.
* Implementazione dei modelli ORM (`User`, `Project`, `Task`).
* Implementazione del modulo di sicurezza (hashing password e token JWT Bearer).
* Creazione degli schemi Pydantic e primi endpoint di autenticazione e CRUD.

### 🔹 Fase 3: Testing Strategy & Regression Testing
* Setup di `pytest` con fixtures isolate in `conftest.py`.
* Scrittura di test unitari sui servizi di business (validazioni, stati dei task).
* Scrittura di test di integrazione con `httpx.AsyncClient` o `TestClient` per verificare gli endpoint API e l'autenticazione.
* **Laboratorio di Regression Testing:**
  * Introduzione simulata di un bug subdolo (es. filtro permessi o fuso orario scadenza).
  * Scrittura del test di regressione fallente in `tests/regression/`.
  * Risoluzione del bug e verifica permanente del test verde.
* Misurazione della copertura del codice con `pytest-cov`.

### 🔹 Fase 4: Git Flow & Pipeline CI/CD con GitHub Actions
* Definizione delle convenzioni di branching (`main`, `feature/*`, `bugfix/*`) e *Conventional Commits*.
* Creazione della pipeline GitHub Actions (`.github/workflows/ci.yml`).
* Test della pipeline: linting con Ruff, esecuzione test unitari, di integrazione e di regressione.
* Simulazione di una Pull Request con checklist di approvazione.

### 🔹 Fase 5: Documentazione, Rifinitura, Packaging & Rilascio
* Arricchimento della documentazione automatica OpenAPI/Swagger (`/docs`).
* Creazione di un `README.md` esaustivo e professionale.
* Dockerfile / Containerizzazione minimale come opzione di rilascio.
* Chiusura del diario di bordo `JOURNAL.md` e retrospettiva sulle competenze acquisite.
