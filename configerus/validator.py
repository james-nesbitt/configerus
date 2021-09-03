"""

Configuration validation.

Shared Validation code, which really just comes down to the shared Exception
used to inidcate a validation failure.

"""


class ValidationError(ValueError):
    """Configerus Validation has failed."""
