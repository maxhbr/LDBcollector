// SPDX-FileCopyrightText: Copyright 2026 Siemens AG
// SPDX-License-Identifier: BSD-3-Clause

package licenselynx

//go:generate go run ./internal/codegen -input ../_support/merged_data.build.json -output .

type options struct {
	risky bool
	org   *Organization
}

// Option customizes Map behavior.
type Option func(*options)

// WithRisky enables lookup in the risky mappings.
func WithRisky() Option {
	return func(o *options) {
		o.risky = true
	}
}

// WithOrganization enables lookup in the organization-specific mappings.
func WithOrganization(org Organization) Option {
	return func(o *options) {
		o.org = &org
	}
}

// Map resolves a license name or identifier to its canonical representation.
// The lookup is performed in the following order:
// 1. Stable mappings (always)
// 2. Risky mappings (if WithRisky() is provided)
// 3. Organization-specific mappings (if WithOrganization(org) is provided)
//
// The function returns the resolved LicenseObject and a boolean indicating whether the mapping was successful.
// If the boolean is false, no suitable mapping was found and the returned LicenseObject will be empty.
func Map(licenseName string, opts ...Option) (LicenseObject, bool) {
	return mapWithLicenseMaps(licenseName, defaultLicenseMaps(), opts...)
}

// mapWithLicenseMaps is an internal helper that evaluates the provided options and performs the lookup in the provided license maps.
func mapWithLicenseMaps(licenseName string, maps licenseMaps, opts ...Option) (LicenseObject, bool) {
	resolvedOptions := options{}
	for _, opt := range opts {
		if opt != nil {
			opt(&resolvedOptions)
		}
	}

	normalizedLicenseName := normalizeQuotes(licenseName)

	if licenseObject, ok := maps.stable[normalizedLicenseName]; ok {
		return licenseObject, true
	}

	if resolvedOptions.risky {
		if licenseObject, ok := maps.risky[normalizedLicenseName]; ok {
			return licenseObject, true
		}
	}

	if resolvedOptions.org != nil {
		if licenseObject, ok := maps.organizationMap(*resolvedOptions.org)[normalizedLicenseName]; ok {
			return licenseObject, true
		}
	}

	return LicenseObject{}, false
}
