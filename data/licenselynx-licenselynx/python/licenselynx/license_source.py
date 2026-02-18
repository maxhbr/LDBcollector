from enum import StrEnum


class LicenseSource(StrEnum):
    """Enum representing the source of a canonical identifier."""
    SPDX = "spdx"
    SCANCODE_LICENSEDB = "scancode-licensedb"
    CUSTOM = "custom"
