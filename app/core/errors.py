class DomainError(Exception):
    """The request broke a business rule."""


class NotFoundError(DomainError):
    """The requested record was not found."""


class ConflictError(DomainError):
    """The request conflicts with an existing record."""


class BusinessRuleError(DomainError):
    """The request does not meet a business rule."""


class AuthenticationError(DomainError):
    """The request is not authenticated."""


class PermissionDeniedError(DomainError):
    """The signed-in user is not allowed to perform the action."""


class DataStoreError(Exception):
    """The data store is broken or malformed."""
