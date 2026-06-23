// SPDX-FileCopyrightText: Copyright 2026 Siemens AG
// SPDX-License-Identifier: BSD-3-Clause

package licenselynx

type licenseMaps struct {
	stable        map[string]LicenseObject
	risky         map[string]LicenseObject
	organizations map[Organization]map[string]LicenseObject
}

func defaultLicenseMaps() licenseMaps {
	return licenseMaps{
		stable:        generatedStableMap,
		risky:         generatedRiskyMap,
		organizations: generatedOrgMaps,
	}
}

func (m licenseMaps) organizationMap(org Organization) map[string]LicenseObject {
	if orgMap, ok := m.organizations[org]; ok {
		return orgMap
	}

	return emptyLicenseMap
}

var emptyLicenseMap = map[string]LicenseObject{}
