// SPDX-FileCopyrightText: Copyright 2026 Siemens AG
// SPDX-License-Identifier: BSD-3-Clause

package licenselynx

// LicenseSource identifies the source of a canonical license identifier.
type LicenseSource string

const (
	SourceSPDX              LicenseSource = "spdx"
	SourceScancodeLicenseDB LicenseSource = "scancode-licensedb"
	SourceCustom            LicenseSource = "custom"
)
