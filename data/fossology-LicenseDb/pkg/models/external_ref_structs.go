// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Dearsh Oberoi <oberoidearsh@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package models

type LicenseDBSchemaExtension struct {
	InternalComment    *string `json:"internal_comment,omitempty" example:"comment"`
	LicenseExplanation *string `json:"license_explanation,omitempty" example:"explanation of license"`
	LicenseSuffix      *string `json:"license_suffix,omitempty" example:"license suffix"`
	LicenseVersion     *string `json:"license_version,omitempty"`
}
