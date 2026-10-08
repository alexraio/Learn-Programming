"""Entry point principale dell'applicazione TaskMaster API."""

import uvicorn
from fastapi import FastAPI

app = FastAPI(
    title="TaskMaster API",
    description="API REST professionale per la gestione di progetti e task",
    version="0.1.0",
)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Endpoint di health check per verificare che il servizio sia operativo."""
    return {"status": "healthy", "service": "taskmaster-api"}


def main() -> None:
    """Funzione di avvio per il comando CLI uv run taskmaster."""
    uvicorn.run("taskmaster.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
