// SPDX-FileCopyrightText: 2025 Chayan Das <01chayandas@gmail.com>
// SPDX-License-Identifier: GPL-2.0-only

package email

import (
	"time"

	templates "github.com/fossology/LicenseDb/pkg/email/templetes"
)

func NotifyLicenseCreated(to, userName, shortName string) {
	admins, err := FetchAdminEmails()
	if err != nil {
		return
	}

	subject, html := templates.SingleLicenseEmailTemplate(
		userName, "Created", time.Now(), shortName,
	)
	Email.enqueueAsync(EmailData{To: []string{to}, Subject: subject, HTML: html})

	adminSubject, adminHTML := templates.SingleLicenseEmailTemplate(
		"Admins", "Created", time.Now(), shortName,
	)
	Email.enqueueAsync(EmailData{To: admins, Subject: adminSubject, HTML: adminHTML})
}

func NotifyLicenseUpdated(to, userName, license string) {
	admins, err := FetchAdminEmails()
	if err != nil {
		return
	}

	subject, html := templates.SingleLicenseEmailTemplate(
		userName, "Updated", time.Now(), license,
	)
	Email.enqueueAsync(EmailData{To: []string{to}, Subject: subject, HTML: html})

	adminSubject, adminHTML := templates.SingleLicenseEmailTemplate(
		"Admins", "Updated", time.Now(), license,
	)
	Email.enqueueAsync(EmailData{To: admins, Subject: adminSubject, HTML: adminHTML})
}

func NotifyImportSummary(to, userName, importType string, total, success, failed int) {
	admins, err := FetchAdminEmails()
	if err != nil {
		return
	}

	subject, html := templates.ImportSummaryEmailTemplate(
		userName, importType, total, success, failed, time.Now(),
	)
	Email.enqueueAsync(EmailData{To: []string{to}, Subject: subject, HTML: html})

	adminSubject, adminHTML := templates.ImportSummaryEmailTemplate(
		"Admins", importType, total, success, failed, time.Now(),
	)
	Email.enqueueAsync(EmailData{To: admins, Subject: adminSubject, HTML: adminHTML})
}
