# 📔 Diario di Bordo: Progetto TaskMaster API

Questo documento tiene traccia dell'avanzamento giorno per giorno, dei concetti appresi, delle sfide tecniche e delle decisioni architetturali del percorso verso uno sviluppo software professionale con Python, Antigravity IDE, Git e GitHub Actions.

---

## 📌 Indice delle Sessioni

* [Sessione 1 (2026-10-08): Fondamenta, Scaffolding & Setup IDE Antigravity](#sessione-1-2026-10-08-fondamenta-scaffolding--setup-ide-antigravity)
* *Sessione 2: Architettura Core, Modelli SQLAlchemy & Auth JWT (In programma)*
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
