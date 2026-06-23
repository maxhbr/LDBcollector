// SPDX-FileCopyrightText: Copyright 2026 Siemens AG
// SPDX-License-Identifier: BSD-3-Clause

package licenselynx

import "testing"

func TestLicenseObjectHelpers(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name               string
		license            LicenseObject
		organization       Organization
		wantSpdxID         bool
		wantScancodeID     bool
		wantCustomID       bool
		wantOrganization   bool
		wantOrganizationOf bool
	}{
		{
			name:               "spdx source",
			license:            LicenseObject{ID: "MIT", Src: string(SourceSPDX)},
			organization:       OrgSiemens,
			wantSpdxID:         true,
			wantOrganizationOf: false,
		},
		{
			name:               "scancode source",
			license:            LicenseObject{ID: "LicenseRef-scancode", Src: string(SourceScancodeLicenseDB)},
			organization:       OrgSiemens,
			wantScancodeID:     true,
			wantOrganizationOf: false,
		},
		{
			name:               "custom source",
			license:            LicenseObject{ID: "CUSTOM-LIC", Src: string(SourceCustom)},
			organization:       OrgSiemens,
			wantCustomID:       true,
			wantOrganizationOf: false,
		},
		{
			name:               "organization source",
			license:            LicenseObject{ID: "SISL-1.5", Src: string(OrgSiemens)},
			organization:       OrgSiemens,
			wantOrganization:   true,
			wantOrganizationOf: true,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()

			if got := test.license.IsSpdxId(); got != test.wantSpdxID {
				t.Fatalf("IsSpdxId mismatch: got %v want %v", got, test.wantSpdxID)
			}
			if got := test.license.IsScancodeLicenseId(); got != test.wantScancodeID {
				t.Fatalf("IsScancodeLicenseId mismatch: got %v want %v", got, test.wantScancodeID)
			}
			if got := test.license.IsCustomId(); got != test.wantCustomID {
				t.Fatalf("IsCustomId mismatch: got %v want %v", got, test.wantCustomID)
			}
			if got := test.license.IsOrganizationSource(); got != test.wantOrganization {
				t.Fatalf("IsOrganizationSource mismatch: got %v want %v", got, test.wantOrganization)
			}
			if got := test.license.IsOrganizationSourceOf(test.organization); got != test.wantOrganizationOf {
				t.Fatalf("IsOrganizationSourceOf mismatch: got %v want %v", got, test.wantOrganizationOf)
			}
		})
	}
}
