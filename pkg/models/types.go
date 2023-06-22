// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-License-Identifier: GPL-2.0-only

package models

// The License struct represents a license entity with various attributes and
// properties associated with it.
// It provides structured storage for license-related information.
type LicenseDB struct {
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

type LicenseJson struct {
	Shortname       string `json:"rf_shortname"`
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
	SpdxCompatible  string `json:"rf_spdx_compatible"`
	Risk            string `json:"rf_risk"`
	Flag            string `json:"rf_flag"`
	Marydone        string `json:"marydone"`
}

// The Meta struct represents additional metadata associated with a
// license retrieval operation.
// It contains information that provides context and supplementary details
// about the retrieved license data.
type Meta struct {
	ResourceCount int `json:"resource_count"`
	Page          int `json:"page,omitempty"`
	PerPage       int `json:"per_page,omitempty"`
}

// LicenseResponse struct is representation of design API response of license.
// The LicenseResponse struct represents the response data structure for
// retrieving license information.
// It is used to encapsulate license-related data in an organized manner.
type LicenseResponse struct {
	Status int         `json:"status"`
	Data   []LicenseDB `json:"data"`
	Meta   Meta        `json:"meta"`
}

// The LicenseError struct represents an error response related to license operations.
// It provides information about the encountered error, including details such as
// status, error message, error type, path, and timestamp.
type LicenseError struct {
	Status    int    `json:"status"`
	Message   string `json:"message"`
	Error     string `json:"error"`
	Path      string `json:"path"`
	Timestamp string `json:"timestamp"`
}

// The LicenseInput struct represents the input or payload required for creating a license.
// It contains various fields that capture the necessary information for defining a license entity.
type LicenseInput struct {
	Shortname       string `json:"rf_shortname" binding:"required"`
	Fullname        string `json:"rf_fullname" binding:"required"`
	Text            string `json:"rf_text" binding:"required"`
	Url             string `json:"rf_url" binding:"required"`
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
	SpdxId          string `json:"rf_spdx_id" binding:"required"`
	Risk            string `json:"rf_risk"`
	Flag            string `json:"rf_flag"`
	Marydone        string `json:"marydone"`
}
