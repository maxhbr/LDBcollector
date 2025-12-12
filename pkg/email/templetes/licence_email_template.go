// SPDX-FileCopyrightText: 2025 Chayan Das <01chayandas@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package templates

import (
	"fmt"
	"time"
)

func SingleLicenseEmailTemplate(userName, action string, timestamp time.Time, licenseName string) (string, string) {
	subject := fmt.Sprintf("License %s Notification – %s", action, licenseName)

	body := fmt.Sprintf(`
		<!DOCTYPE html>
		<html lang="en">
		<head>
			<meta charset="UTF-8">
			<title>License %s Notification – %s</title>
			<style>
				body {
					font-family: Arial, sans-serif;
					line-height: 1.6;
					color: #333;
					background-color: #f4f4f4;
					padding: 30px;
				}
				.container {
					max-width: 600px;
					margin: auto;
					background-color: #fff;
					padding: 20px;
					border-radius: 8px;
					box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
				}
				h2 {
					color: #2c3e50;
				}
				.footer {
					margin-top: 30px;
					font-size: 12px;
					color: #888;
					text-align: center;
				}
				a {
					color: #1e88e5;
					text-decoration: none;
				}
			</style>
		</head>
		<body>
			<div class="container">
				<h2>License %s</h2>
				<p>Dear %s,</p>
				<p>This is to inform you that the license <strong>%s</strong> has been <strong>%s</strong> on <em>%s</em>.</p>
				<p>If this action was not performed by you, please contact our support team immediately at 
				<a href="mailto:support@licensedb.org">support@licensedb.org</a>.</p>
				<p>Best regards,<br><strong>LicenseDB Team</strong></p>
				<div class="footer">
					This is an automated message. Please do not reply directly to this email.
				</div>
			</div>
		</body>
		</html>
	`, action, licenseName, action, userName, licenseName, action, timestamp.Format("Monday, Jan 2, 2006 at 15:04 MST"))

	return subject, body
}
