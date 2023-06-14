// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-License-Identifier: GPL-2.0-only

package models

type License struct {
	Shortname       string `json:"rf_shortname" gorm:"primary_key"`
	Fullname        string `json:"rf_fullname"`
	Text            string `json:"rf_text"`
	Url             string `json:"rf_url"`
	AddDate         string `json:"rf_add_date"`
	Copyleft        string `json:"rf_copyleft"`
	FSFfree         string `json:"rf_FSFfree"`
	OSIapproved     string `json:"rf_OSIapproved"`
	GPLv2compatible string `json:"rf_GPLv2compatible"`
	GPLv3compatible string `json:"rf_GPLv3compatible"`
	Notes           string `json:"rf_notes"`
	Fedora          string `json:"rf_Fedora"`
	TextUpdatable   string `json:"rf_text_updatable"`
	DetectorType    string `json:"rf_detector_type"`
	Active          string `json:"rf_active"`
	Source          string `json:"rf_source"`
	SpdxId          string `json:"rf_spdx_id"`
	Risk            string `json:"rf_risk"`
	Flag            string `json:"rf_flag"`
	Marydone        string `json:"marydone"`
}

type Meta struct {
	ResourceCount int `json:"resource_count"`
	Page          int `json:"page,omitempty"`
	PerPage       int `json:"per_page,omitempty"`
}

type LicenseResponse struct {
	Status int       `json:"status"`
	Data   []License `json:"data"`
	Meta   Meta      `json:"meta,omitempty"`
}

type LicenseError struct {
	Status    int    `json:"status"`
	Message   string `json:"message"`
	Error     string `json:"error"`
	Path      string `json:"path"`
	Timestamp string `json:"timestamp"`
}
