from enum import StrEnum


class CanonicalSource(StrEnum):
    """Enum representing the source of a canonical identifier."""
    SPDX = "spdx"
    SCANCODE_LICENSEDB = "scancode-licensedb"
    OSI = "osi"
    CUSTOM = "custom"
