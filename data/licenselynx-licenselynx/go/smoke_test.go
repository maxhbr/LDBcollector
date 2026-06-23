// SPDX-FileCopyrightText: Copyright 2026 Siemens AG
// SPDX-License-Identifier: BSD-3-Clause

package licenselynx

import "testing"

func TestSmokeStableMap(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name        string
		licenseName string
		wantID      string
		wantSrc     string
	}{
		{name: "mit canonical id", licenseName: "MIT", wantID: "MIT", wantSrc: string(SourceSPDX)},
		{name: "apache alias", licenseName: "Apache 2.0", wantID: "Apache-2.0", wantSrc: string(SourceSPDX)},
		{name: "quote normalized stable alias", licenseName: "“MIT”", wantID: "MIT", wantSrc: string(SourceSPDX)},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()

			got, ok := Map(test.licenseName)
			if !ok {
				t.Fatalf("expected lookup success for %q", test.licenseName)
			}
			if got.ID != test.wantID || got.Src != test.wantSrc {
				t.Fatalf("unexpected result: got %+v want ID=%q Src=%q", got, test.wantID, test.wantSrc)
			}
		})
	}
}

func TestSmokeRiskyMap(t *testing.T) {
	t.Parallel()

	if _, ok := Map("License :: LGPLv3"); ok {
		t.Fatal("expected risky-only entry to miss without risky option")
	}

	got, ok := Map("License :: LGPLv3", WithRisky())
	if !ok {
		t.Fatal("expected risky-only entry to resolve with risky option")
	}
	if got.ID == "" || got.Src == "" {
		t.Fatalf("expected populated risky result, got %+v", got)
	}
}

func TestSmokeOrganizationMap(t *testing.T) {
	t.Parallel()

	if _, ok := Map("SISL 1.5"); ok {
		t.Fatal("expected organization entry to miss without organization option")
	}

	got, ok := Map("SISL 1.5", WithOrganization(OrgSiemens))
	if !ok {
		t.Fatal("expected organization entry to resolve with organization option")
	}
	if got.ID != "SISL-1.5" || got.Src != string(OrgSiemens) {
		t.Fatalf("unexpected organization result: got %+v", got)
	}
	if !got.IsOrganizationSource() || !got.IsOrganizationSourceOf(OrgSiemens) {
		t.Fatalf("expected organization helper methods to report true, got %+v", got)
	}
}
