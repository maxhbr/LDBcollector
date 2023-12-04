// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-License-Identifier: GPL-2.0-only

package utils

import "github.com/fossology/LicenseDb/pkg/models"

func Converter(input models.LicenseJson) models.LicenseDB {
	if input.SpdxCompatible == "t" {
		input.SpdxCompatible = input.Shortname
	} else {
		input.SpdxCompatible = "LicenseRef-fossology-" + input.Shortname
	}
	result := models.LicenseDB{
		Shortname:       input.Shortname,
		Fullname:        input.Fullname,
		Text:            input.Text,
		Url:             input.Url,
		Copyleft:        input.Copyleft,
		AddDate:         input.AddDate,
		FSFfree:         input.FSFfree,
		OSIapproved:     input.OSIapproved,
		GPLv2compatible: input.GPLv2compatible,
		GPLv3compatible: input.GPLv3compatible,
		Notes:           input.Notes,
		Fedora:          input.Fedora,
		TextUpdatable:   input.TextUpdatable,
		DetectorType:    input.DetectorType,
		Active:          input.Active,
		Source:          input.Source,
		SpdxId:          input.SpdxCompatible,
		Risk:            input.Risk,
		Flag:            input.Flag,
		Marydone:        input.Marydone,
	}
	return result
}
