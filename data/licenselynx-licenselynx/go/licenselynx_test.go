// SPDX-FileCopyrightText: Copyright 2026 Siemens AG
// SPDX-License-Identifier: BSD-3-Clause

package licenselynx

import "testing"

func TestMapWithLicenseMaps(t *testing.T) {
	t.Parallel()

	org := Organization("test-org")
	testMaps := licenseMaps{
		stable: map[string]LicenseObject{
			"MIT":         {ID: "MIT", Src: string(SourceSPDX)},
			"'quoted-id'": {ID: "QUOTED", Src: string(SourceCustom)},
		},
		risky: map[string]LicenseObject{
			"LGPLv3": {ID: "LGPL-3.0-only", Src: string(SourceSPDX)},
		},
		organizations: map[Organization]map[string]LicenseObject{
			org: {
				"ORG-LIC": {ID: "ORG-LIC", Src: string(org)},
			},
		},
	}

	tests := []struct {
		name        string
		licenseName string
		opts        []Option
		want        LicenseObject
		wantOK      bool
	}{
		{
			name:        "stable hit",
			licenseName: "MIT",
			want:        LicenseObject{ID: "MIT", Src: string(SourceSPDX)},
			wantOK:      true,
		},
		{
			name:        "stable hit with risky enabled",
			licenseName: "MIT",
			opts:        []Option{WithRisky()},
			want:        LicenseObject{ID: "MIT", Src: string(SourceSPDX)},
			wantOK:      true,
		},
		{
			name:        "risky hit when enabled",
			licenseName: "LGPLv3",
			opts:        []Option{WithRisky()},
			want:        LicenseObject{ID: "LGPL-3.0-only", Src: string(SourceSPDX)},
			wantOK:      true,
		},
		{
			name:        "risky miss when disabled",
			licenseName: "LGPLv3",
			want:        LicenseObject{},
			wantOK:      false,
		},
		{
			name:        "organization hit when enabled",
			licenseName: "ORG-LIC",
			opts:        []Option{WithOrganization(org)},
			want:        LicenseObject{ID: "ORG-LIC", Src: string(org)},
			wantOK:      true,
		},
		{
			name:        "organization miss without option",
			licenseName: "ORG-LIC",
			want:        LicenseObject{},
			wantOK:      false,
		},
		{
			name:        "organization miss with different org",
			licenseName: "ORG-LIC",
			opts:        []Option{WithOrganization(Organization("other-org"))},
			want:        LicenseObject{},
			wantOK:      false,
		},
		{
			name:        "quote normalization before lookup",
			licenseName: "‘quoted-id’",
			want:        LicenseObject{ID: "QUOTED", Src: string(SourceCustom)},
			wantOK:      true,
		},
		{
			name:        "missing license",
			licenseName: "does-not-exist",
			want:        LicenseObject{},
			wantOK:      false,
		},
		{
			name:        "nil option is ignored",
			licenseName: "MIT",
			opts:        []Option{nil},
			want:        LicenseObject{ID: "MIT", Src: string(SourceSPDX)},
			wantOK:      true,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()

			got, gotOK := mapWithLicenseMaps(test.licenseName, testMaps, test.opts...)
			if gotOK != test.wantOK {
				t.Fatalf("ok mismatch: got %v want %v", gotOK, test.wantOK)
			}

			if got != test.want {
				t.Fatalf("result mismatch: got %+v want %+v", got, test.want)
			}
		})
	}
}

func TestOrganizationMapFallsBackToEmptyMap(t *testing.T) {
	t.Parallel()

	maps := licenseMaps{}
	got := maps.organizationMap(Organization("missing-org"))
	if got == nil {
		t.Fatal("expected non-nil empty map")
	}
	if len(got) != 0 {
		t.Fatalf("expected empty map, got %d entries", len(got))
	}
}
