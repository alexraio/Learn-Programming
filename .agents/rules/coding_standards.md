---
description: "Standard di codifica, qualità del software e regole operative per Antigravity IDE nel progetto TaskMaster"
globs: ["**/*.py", "**/*.toml", "**/*.md"]
---

# Regole di Sviluppo & Qualità per Antigravity IDE (TaskMaster)

Queste regole governano il comportamento dell'assistente AI e dello sviluppatore all'interno del progetto **TaskMaster**. Devono essere rispettate rigorosamente in ogni sessione.

## 1. Principi di Codifica Python
- **Type Annotations Rigorose:** Tutte le funzioni, metodi e parametri devono includere type hints espliciti (standard Python 3.12+).
- **Separazione delle Responsabilità (Layered Architecture):**
  - I controller HTTP in `src/taskmaster/api/` NON contengono logica di business o query SQL dirette.
  - La logica di business risiede esclusivamente nei `services/`.
  - La persistenza risiede nei `models/` (SQLAlchemy 2.0).
  - La validazione di input/output risiede negli `schemas/` (Pydantic V2).
- **Gestione Errori:** Non sollevare eccezioni HTTP generiche nei servizi. Utilizzare eccezioni di dominio personalizzate catturate da exception handler centralizzati in `main.py`.

## 2. Gatekeeper di Qualità (Pre-Commit & Pre-Merge)
Prima di proporre o finalizzare un commit o una pull request:
1. Eseguire sempre il linting: `uv run ruff check .`
2. Eseguire la formattazione: `uv run ruff format --check .`
3. Eseguire la suite di test: `uv run pytest`
4. **Regola Aurea:** NESSUN commit deve essere eseguito se anche un solo test è rosso o se ci sono warning bloccanti del linter.

## 3. Politica di Regression Testing
- Ogni volta che viene identificato o segnalato un bug:
  1. Scrivere PRIMA un test riproducibile in `tests/regression/test_regression_<id>.py`.
  2. Verificare che il test fallisca (RED).
  3. Applicare la correzione minima nel codice (GREEN).
  4. Mantenere il test per sempre nella suite per garantire che il bug non si ripresenti mai più.

## 4. Convenzione Git (Conventional Commits)
I messaggi di commit devono seguire lo standard:
- `feat: <descrizione>` per nuove funzionalità
- `fix: <descrizione>` per correzioni di bug
- `test: <descrizione>` per aggiunta o modifica di test
- `refactor: <descrizione>` per modifiche di codice senza alterazione del comportamento esterno
- `docs: <descrizione>` per documentazione e diario di bordo
- `chore: <descrizione>` per configurazioni o manutenzione dipendenze

## 5. Diario di Bordo (`JOURNAL.md`)
- Ogni sessione di lavoro deve essere registrata in `JOURNAL.md`.
- Registrare obiettivi, concetti appresi, problemi affrontati e stato di avanzamento.
