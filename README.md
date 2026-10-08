# 🚀 TaskMaster API

> Progetto didattico e dimostrativo di sviluppo software professionale con **Python 3.12+**, **FastAPI**, **SQLAlchemy 2.0**, **uv**, suite di test (**Pytest** con **Regression Testing**) e pipeline **CI/CD con GitHub Actions**.

---

## 📖 Documentazione e Diario del Progetto

* **Specifiche & Decision Log:** [DESIGN.md](file:///Users/alessio/Insync/ballarin.alessio@gmail.com/GoogleDrive/programming/Learn-Programming/DESIGN.md)
* **Diario di Bordo & Tracciamento Sessioni:** [JOURNAL.md](file:///Users/alessio/Insync/ballarin.alessio@gmail.com/GoogleDrive/programming/Learn-Programming/JOURNAL.md)
* **Regole Antigravity IDE & AI:** [.agents/rules/coding_standards.md](file:///Users/alessio/Insync/ballarin.alessio@gmail.com/GoogleDrive/programming/Learn-Programming/.agents/rules/coding_standards.md)

---

## 🛠️ Stack Tecnologico

* **Linguaggio & Runtime:** Python 3.12+ gestito tramite `uv`
* **Framework Web:** FastAPI (con documentazione automatica OpenAPI/Swagger)
* **Validazione Dati:** Pydantic V2 & Pydantic Settings
* **ORM & Database:** SQLAlchemy 2.0 con SQLite (WAL mode)
* **Sicurezza & Auth:** JWT Bearer Token + hashing password con Argon2
* **Qualità del Codice:** Ruff (Linter & Formatter ultra-rapido) + Mypy (Type checking)
* **Testing:** Pytest (Unit, Integration, Regression) con coverage report

---

## ⚡ Quickstart

### 1. Prerequisiti
Assicurati di avere installato [`uv`](https://docs.astral.sh/uv/):
```bash
brew install uv
```

### 2. Installazione delle dipendenze
`uv` crea e sincronizza automaticamente il virtualenv con il lockfile:
```bash
uv sync
```

### 3. Avvio del Server di Sviluppo
```bash
uv run uvicorn taskmaster.main:app --reload --port 8000
```
L'API sarà disponibile all'indirizzo: `http://127.0.0.1:8000`  
Documentazione interattiva Swagger: `http://127.0.0.1:8000/docs`

---

## 🧪 Esecuzione Test & Controlli Qualità

```bash
# Linting del codice
uv run ruff check .

# Formattazione
uv run ruff format .

# Type checking statico
uv run mypy src

# Test suite completa con coverage
uv run pytest --cov=src/taskmaster --cov-report=term-missing

# Esecuzione esclusiva dei test di regressione
uv run pytest tests/regression -v
```
