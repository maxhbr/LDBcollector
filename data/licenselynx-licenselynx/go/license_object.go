// SPDX-FileCopyrightText: Copyright 2026 Siemens AG
// SPDX-License-Identifier: BSD-3-Clause

package licenselynx

// LicenseObject represents a canonical license identifier and its source.
type LicenseObject struct {
	ID  string
	Src string
}

// IsSpdxId reports whether the canonical identifier comes from SPDX.
func (l LicenseObject) IsSpdxId() bool {
	return l.Src == string(SourceSPDX)
}

// IsScancodeLicenseId reports whether the canonical identifier comes from ScanCode LicenseDB.
func (l LicenseObject) IsScancodeLicenseId() bool {
	return l.Src == string(SourceScancodeLicenseDB)
}

// IsCustomId reports whether the canonical identifier comes from the custom namespace.
func (l LicenseObject) IsCustomId() bool {
	return l.Src == string(SourceCustom)
}

// IsOrganizationSource reports whether the canonical identifier comes from any organization namespace.
func (l LicenseObject) IsOrganizationSource() bool {
	_, ok := generatedOrgMaps[Organization(l.Src)]
	return ok
}

// IsOrganizationSourceOf reports whether the canonical identifier comes from the provided organization namespace.
func (l LicenseObject) IsOrganizationSourceOf(org Organization) bool {
	return l.Src == string(org)
}
