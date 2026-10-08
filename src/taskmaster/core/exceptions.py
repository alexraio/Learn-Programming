"""Eccezioni di dominio personalizzate per TaskMaster API."""


class TaskMasterError(Exception):
    """Eccezione base per tutti gli errori specifici dell'applicazione."""

    def __init__(self, message: str, code: str = "APPLICATION_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class EntityNotFoundError(TaskMasterError):
    """Sollevata quando una risorsa richiesta non esiste nel database."""

    def __init__(self, entity_name: str, identifier: str | int) -> None:
        super().__init__(
            message=f"{entity_name} con identificatore '{identifier}' non trovato.",
            code="ENTITY_NOT_FOUND",
        )


class PermissionDeniedError(TaskMasterError):
    """Sollevata quando l'utente non dispone dei permessi per la risorsa."""

    def __init__(self, message: str = "Permesso negato per l'operazione richiesta.") -> None:
        super().__init__(message=message, code="PERMISSION_DENIED")


class DuplicateEntityError(TaskMasterError):
    """Sollevata quando si tenta di creare una risorsa con un vincolo univoco duplicato."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, code="DUPLICATE_ENTITY")


class InvalidStateTransitionError(TaskMasterError):
    """Sollevata quando una transizione di stato non è ammessa dalle regole di business."""

    def __init__(self, current_status: str, target_status: str) -> None:
        super().__init__(
            message=f"Transizione di stato non consentita da '{current_status}' a '{target_status}'.",
            code="INVALID_STATE_TRANSITION",
        )


class InvalidCredentialsError(TaskMasterError):
    """Sollevata quando le credenziali fornite per l'autenticazione non sono valide."""

    def __init__(self, message: str = "Credenziali di accesso non valide.") -> None:
        super().__init__(message=message, code="INVALID_CREDENTIALS")
