class DomainError(Exception):
    """Base class for violations of domain rules."""


class UnknownUnitError(DomainError):
    """A source unit has no canonical conversion."""
