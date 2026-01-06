// SPDX-FileCopyrightText: 2025 Chayan Das <01chayandas@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package templates

import (
	"fmt"
	"strings"
	"time"

	"golang.org/x/text/cases"
	"golang.org/x/text/language"
)

func formatImportType(importType string) string {
	caser := cases.Title(language.English)
	return caser.String(strings.ToLower(importType))
}
func ImportSummaryEmailTemplate(userName, importType string, total, success, failed int, timestamp time.Time) (string, string) {
	// Normalize importType (License or Obligation)
	importType = formatImportType(importType) // e.g. "license" → "License"

	subject := fmt.Sprintf("%s Import Summary – %s", importType, timestamp.Format("Jan 2, 2006"))

	body := fmt.Sprintf(`
		<!DOCTYPE html>
		<html lang="en">
		<head>
			<meta charset="UTF-8">
			<title>%s Import Summary</title>
			<style>
				body {
					font-family: Arial, sans-serif;
					line-height: 1.6;
					color: #333;
					background-color: #f7f7f7;
					padding: 20px;
				}
				.container {
					max-width: 600px;
					margin: auto;
					background: #ffffff;
					padding: 20px;
					border-radius: 8px;
					box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
				}
				h2 {
					color: #673AB7;
				}
				.footer {
					margin-top: 30px;
					font-size: 12px;
					color: #888;
				}
				.stats {
					background-color: #f1f1f1;
					padding: 10px;
					border-radius: 5px;
					margin-top: 10px;
				}
			</style>
		</head>
		<body>
			<div class="container">
				<h2>%s Import Summary</h2>
				<p>Dear %s,</p>

				<p>The bulk import process for <strong>%s</strong>s was initiated on <em>%s</em>.</p>

				<div class="stats">
					<p><strong>Total Records Attempted:</strong> %d</p>
					<p><strong>Successfully Imported:</strong> %d</p>
					<p><strong>Failed:</strong> %d</p>
				</div>

				<p>If any of these results seem unexpected, please verify the uploaded data or contact support.</p>

				<p>Regards,<br><strong>LicenseDB Team</strong></p>

				<div class="footer">
					This is an automated message. Please do not reply directly to this email.<br>
					Need help? Contact <a href="mailto:support@licensedb.org">support@licensedb.org</a>
				</div>
			</div>
		</body>
		</html>
	`, importType, importType, userName, importType, timestamp.Format("Monday, Jan 2, 2006 at 15:04 MST"), total, success, failed)

	return subject, body
}
