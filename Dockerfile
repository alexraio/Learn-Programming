# Multi-stage Dockerfile ottimizzato per produzione con Astral uv e Python 3.12

# ==============================================================================
# 1. Builder Stage: Risoluzione dipendenze e compilazione bytecode
# ==============================================================================
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Copia solo i file di configurazione per sfruttare al massimo la cache dei layer Docker
COPY pyproject.toml uv.lock README.md ./

# Installazione delle sole dipendenze di produzione (esclude dependency-groups dev)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copia il codice sorgente dell'applicazione
COPY src/ ./src/

# Installazione del pacchetto applicativo
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# ==============================================================================
# 2. Final Runtime Stage: Immagine snella ed eseguita con utente non-root
# ==============================================================================
FROM python:3.12-slim-bookworm AS runner

WORKDIR /app

# Creazione utente e gruppo di sistema a bassi privilegi per sicurezza
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Copia dell'ambiente virtuale isolato dallo stage builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app/src /app/src

# Configurazione PATH e variabili Python
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Passaggio all'utente sicuro non-root
USER appuser

EXPOSE 8000

# Healthcheck nativo Docker per orchestratori (Docker Compose, Kubernetes, ECS)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Comando di avvio per l'applicazione FastAPI
CMD ["uvicorn", "taskmaster.main:app", "--host", "0.0.0.0", "--port", "8000"]
