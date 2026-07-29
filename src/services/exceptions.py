"""Application service exceptions."""


class ServiceError(Exception):
    """Base exception for expected service-layer failures."""


class EntityNotFoundError(ServiceError):
    """Raised when an entity cannot be found in the requested scope."""


class ConflictError(ServiceError):
    """Raised when an operation conflicts with existing persisted data."""


class AuthenticationError(ServiceError):
    """Raised when credentials cannot authenticate an active account."""
