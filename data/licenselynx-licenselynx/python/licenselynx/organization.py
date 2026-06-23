from enum import StrEnum


class Organization(StrEnum):
    """Enum representing organizations in the data which is also the canonical source of organization-specific license identifiers."""
    SIEMENS = "siemens"
