---
name: taskmaster-workflow
description: "Flusso di lavoro e automazione per il progetto TaskMaster in Antigravity: linting con Ruff, esecuzione test con Pytest e aggiornamento del diario JOURNAL.md"
---

# TaskMaster Workflow Skill

Questa skill fornisce all'agente le procedure standard per verificare la qualità del codice e mantenere aggiornato il progetto TaskMaster.

## Comandi di Verifica Rapida

### 1. Controllo di Qualità Completo (Lint + Test + Coverage)
```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest --cov=src/taskmaster --cov-report=term-missing
```

### 2. Esecuzione Specifica dei Regression Tests
```bash
uv run pytest tests/regression -v
```

### 3. Avvio del Server di Sviluppo
```bash
uv run uvicorn taskmaster.main:app --reload --port 8000
```

## Workflow Operativo
1. **Prima di implementare:** Consultare `DESIGN.md` e la sessione attiva in `JOURNAL.md`.
2. **Durante l'implementazione:** Rispettare la separazione a strati (`models/`, `schemas/`, `services/`, `api/`).
3. **Dopo l'implementazione:** Eseguire sempre i test prima di qualsiasi commit git.
4. **Al termine della sessione:** Aggiornare `JOURNAL.md` con il riassunto del lavoro svolto.
