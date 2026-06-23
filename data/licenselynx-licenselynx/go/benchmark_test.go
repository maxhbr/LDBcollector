// SPDX-FileCopyrightText: Copyright 2026 Siemens AG
// SPDX-License-Identifier: BSD-3-Clause

package licenselynx

import "testing"

func BenchmarkMap(b *testing.B) {
	b.ReportAllocs()

	benchmarks := []struct {
		name        string
		licenseName string
		opts        []Option
	}{
		{
			name:        "stable",
			licenseName: "MIT",
		},
		{
			name:        "stable_quote_normalized",
			licenseName: "“MIT”",
		},
		{
			name:        "risky",
			licenseName: "License :: LGPLv3",
			opts:        []Option{WithRisky()},
		},
		{
			name:        "organization",
			licenseName: "SISL 1.5",
			opts:        []Option{WithOrganization(OrgSiemens)},
		},
		{
			name:        "miss",
			licenseName: "license-that-does-not-exist",
		},
	}

	for _, benchmark := range benchmarks {
		b.Run(benchmark.name, func(b *testing.B) {
			var (
				result LicenseObject
				ok     bool
			)

			for b.Loop() {
				result, ok = Map(benchmark.licenseName, benchmark.opts...)
			}

			_ = result
			_ = ok
		})
	}
}
