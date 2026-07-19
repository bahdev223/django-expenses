class DjangoExpensesError(Exception):
    """Base exception for django-expenses."""


class WorkflowError(DjangoExpensesError):
    """Raised when an invalid workflow transition is attempted."""


class PermissionError(DjangoExpensesError):
    """Raised when a user lacks required permissions."""


class ValidationError(DjangoExpensesError):
    """Raised when expense data validation fails."""
