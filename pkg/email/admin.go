// SPDX-FileCopyrightText: 2025 Chayan Das <01chayandas@gmail.com>
// SPDX-License-Identifier: GPL-2.0-only

package email

import (
	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
)

func FetchAdminEmails() ([]string, error) {
	var emails []string
	admin := "ADMIN"
	active := true
	err := db.DB.
		Model(&models.User{}).
		Where(&models.User{UserLevel: &admin, Active: &active}). // can add super_admin too
		Pluck("user_email", &emails).Error
	if err != nil {
		return nil, err
	}
	return emails, nil
}
