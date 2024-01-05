// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package models

import "time"

// The LicenseDB struct represents a license entity with various attributes and
// properties associated with it.
// It provides structured storage for license-related information.
type LicenseDB struct {
	Id              int64     `json:"rf_id" gorm:"primary_key;column:rf_id" example:"123"`
	Shortname       string    `json:"rf_shortname" gorm:"unique;not null;column:rf_shortname" binding:"required" example:"MIT"`
	Fullname        string    `json:"rf_fullname" gorm:"column:rf_fullname" example:"MIT License"`
	Text            string    `json:"rf_text" gorm:"column:rf_text" example:"MIT License Text here"`
	Url             string    `json:"rf_url" gorm:"column:rf_url" example:"https://opensource.org/licenses/MIT"`
	AddDate         time.Time `json:"rf_add_date" gorm:"default:CURRENT_TIMESTAMP;column:rf_add_date" example:"2023-12-01T18:10:25.00+05:30"`
	Copyleft        bool      `json:"rf_copyleft" gorm:"column:rf_copyleft"`
	FSFfree         bool      `json:"rf_FSFfree" gorm:"column:rf_FSFfree"`
	OSIapproved     bool      `json:"rf_OSIapproved" gorm:"column:rf_OSIapproved"`
	GPLv2compatible bool      `json:"rf_GPLv2compatible" gorm:"column:rf_GPLv2compatible"`
	GPLv3compatible bool      `json:"rf_GPLv3compatible" gorm:"column:rf_GPLv3compatible"`
	Notes           string    `json:"rf_notes" gorm:"column:rf_notes" example:"This license has been superseded."`
	Fedora          string    `json:"rf_Fedora" gorm:"column:rf_Fedora"`
	TextUpdatable   bool      `json:"rf_text_updatable" gorm:"column:rf_text_updatable"`
	DetectorType    int64     `json:"rf_detector_type" gorm:"column:rf_detector_type" example:"1"`
	Active          bool      `json:"rf_active" gorm:"column:rf_active"`
	Source          string    `json:"rf_source" gorm:"column:rf_source"`
	SpdxId          string    `json:"rf_spdx_id" gorm:"column:rf_spdx_id" example:"MIT"`
	Risk            int64     `json:"rf_risk" gorm:"column:rf_risk"`
	Flag            int64     `json:"rf_flag" gorm:"default:1;column:rf_flag" example:"1"`
	Marydone        bool      `json:"marydone" gorm:"column:marydone"`
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
	DetectorType    int64  `json:"rf_detector_type"`
	Active          string `json:"rf_active"`
	Source          string `json:"rf_source"`
	SpdxCompatible  string `json:"rf_spdx_compatible"`
	Risk            string `json:"rf_risk"`
	Flag            string `json:"rf_flag"`
	Marydone        string `json:"marydone"`
}

// LicenseUpdate struct represents the input format for updating an existing license.
// Note that the license ID and shortname cannot be updated.
type LicenseUpdate struct {
	Fullname        string    `json:"rf_fullname" gorm:"column:rf_fullname" example:"MIT License"`
	Text            string    `json:"rf_text" gorm:"column:rf_text" example:"MIT License Text here"`
	Url             string    `json:"rf_url" gorm:"column:rf_url" example:"https://opensource.org/licenses/MIT"`
	AddDate         time.Time `json:"rf_add_date" gorm:"default:CURRENT_TIMESTAMP;column:rf_add_date" example:"2023-12-01T18:10:25.00+05:30"`
	Copyleft        bool      `json:"rf_copyleft" gorm:"column:rf_copyleft"`
	FSFfree         bool      `json:"rf_FSFfree" gorm:"column:rf_FSFfree"`
	OSIapproved     bool      `json:"rf_OSIapproved" gorm:"column:rf_OSIapproved"`
	GPLv2compatible bool      `json:"rf_GPLv2compatible" gorm:"column:rf_GPLv2compatible"`
	GPLv3compatible bool      `json:"rf_GPLv3compatible" gorm:"column:rf_GPLv3compatible"`
	Notes           string    `json:"rf_notes" gorm:"column:rf_notes" example:"This license has been superseded."`
	Fedora          string    `json:"rf_Fedora" gorm:"column:rf_Fedora"`
	TextUpdatable   bool      `json:"rf_text_updatable" gorm:"column:rf_text_updatable"`
	DetectorType    int64     `json:"rf_detector_type" gorm:"column:rf_detector_type" example:"1"`
	Active          bool      `json:"rf_active" gorm:"column:rf_active"`
	Source          string    `json:"rf_source" gorm:"column:rf_source"`
	SpdxId          string    `json:"rf_spdx_id" gorm:"column:rf_spdx_id" example:"MIT"`
	Risk            int64     `json:"rf_risk" gorm:"column:rf_risk"`
	Flag            int64     `json:"rf_flag" gorm:"default:1;column:rf_flag" example:"1"`
	Marydone        bool      `json:"marydone" gorm:"column:marydone"`
}

// The PaginationMeta struct represents additional metadata associated with a
// license retrieval operation.
// It contains information that provides context and supplementary details
// about the retrieved license data.
type PaginationMeta struct {
	ResourceCount int `json:"resource_count" example:"20"`
	Page          int `json:"page,omitempty" example:"1"`
	PerPage       int `json:"per_page,omitempty" example:"10"`
}

// LicenseResponse struct is representation of design API response of license.
// The LicenseResponse struct represents the response data structure for
// retrieving license information.
// It is used to encapsulate license-related data in an organized manner.
type LicenseResponse struct {
	Status int            `json:"status" example:"200"`
	Data   []LicenseDB    `json:"data"`
	Meta   PaginationMeta `json:"paginationmeta"`
}

// The LicenseError struct represents an error response related to license operations.
// It provides information about the encountered error, including details such as
// status, error message, error type, path, and timestamp.
type LicenseError struct {
	Status    int    `json:"status" example:"400"`
	Message   string `json:"message" example:"invalid request body"`
	Error     string `json:"error" example:"invalid request body"`
	Path      string `json:"path" example:"/api/v1/licenses"`
	Timestamp string `json:"timestamp" example:"2023-12-01T10:00:51+05:30"`
}

// The LicenseInput struct represents the input or payload required for creating a license.
// It contains various fields that capture the necessary information for defining a license entity.
type LicenseInput struct {
	Shortname       string    `json:"rf_shortname" example:"MIT"`
	Fullname        string    `json:"rf_fullname" example:"MIT License"`
	Text            string    `json:"rf_text" example:"MIT License Text here"`
	Url             string    `json:"rf_url" example:"https://opensource.org/licenses/MIT"`
	AddDate         time.Time `json:"rf_add_date" example:"2023-12-01T18:10:25.00+05:30"`
	Copyleft        bool      `json:"rf_copyleft"`
	FSFfree         bool      `json:"rf_FSFfree"`
	OSIapproved     bool      `json:"rf_OSIapproved"`
	GPLv2compatible bool      `json:"rf_GPLv2compatible"`
	GPLv3compatible bool      `json:"rf_GPLv3compatible"`
	Notes           string    `json:"rf_notes" example:"This license has been superseded."`
	Fedora          string    `json:"rf_Fedora"`
	TextUpdatable   bool      `json:"rf_text_updatable"`
	DetectorType    int64     `json:"rf_detector_type" example:"1"`
	Active          bool      `json:"rf_active"`
	Source          string    `json:"rf_source"`
	SpdxId          string    `json:"rf_spdx_id" example:"MIT"`
	Risk            int64     `json:"rf_risk"`
	Flag            int64     `json:"rf_flag" example:"1"`
	Marydone        bool      `json:"marydone"`
}

// User struct is representation of user information.
type User struct {
	Id           int64   `json:"id" gorm:"primary_key" example:"123"`
	Username     string  `json:"username" gorm:"unique;not null" binding:"required" example:"fossy"`
	Userlevel    string  `json:"userlevel" binding:"required" example:"admin"`
	Userpassword *string `json:"password,omitempty" binding:"required"`
}

type UserInput struct {
	Username     string  `json:"username" gorm:"unique;not null" binding:"required" example:"fossy"`
	Userlevel    string  `json:"userlevel" binding:"required" example:"admin"`
	Userpassword *string `json:"password,omitempty" binding:"required"`
}

type UserLogin struct {
	Username     string `json:"username" binding:"required" example:"fossy"`
	Userpassword string `json:"password" binding:"required"`
}

// UserResponse struct is representation of design API response of user.
type UserResponse struct {
	Status int            `json:"status" example:"200"`
	Data   []User         `json:"data"`
	Meta   PaginationMeta `json:"paginationmeta"`
}

// SearchLicense struct represents the input needed to search in a license.
type SearchLicense struct {
	Field      string `json:"field" binding:"required" example:"rf_text"`
	SearchTerm string `json:"search_term" binding:"required" example:"MIT License"`
	Search     string `json:"search" enums:"fuzzy,full_text_search"`
}

// Audit struct represents an audit entity with certain attributes and properties
// It has user id as a foreign key
type Audit struct {
	Id        int64     `json:"id" gorm:"primary_key" example:"456"`
	UserId    int64     `json:"user_id" example:"123"`
	User      User      `gorm:"foreignKey:UserId;references:Id" json:"-"`
	TypeId    int64     `json:"type_id" example:"34"`
	Timestamp time.Time `json:"timestamp" example:"2023-12-01T18:10:25.00+05:30"`
	Type      string    `json:"type" example:"license"`
}

// ChangeLog struct represents a change entity with certain attributes and properties
type ChangeLog struct {
	Id           int64  `json:"id" gorm:"primary_key" example:"789"`
	Field        string `json:"field" example:"rf_text"`
	UpdatedValue string `json:"updated_value" example:"New license text"`
	OldValue     string `json:"old_value" example:"Old license text"`
	AuditId      int64  `json:"audit_id" example:"456"`
	Audit        Audit  `gorm:"foreignKey:AuditId;references:Id" json:"-"`
}

// ChangeLogResponse represents the design of API response of change log
type ChangeLogResponse struct {
	Status int            `json:"status" example:"200"`
	Data   []ChangeLog    `json:"data"`
	Meta   PaginationMeta `json:"paginationmeta"`
}

// AuditResponse represents the response format for audit data.
type AuditResponse struct {
	Status int            `json:"status" example:"200"`
	Data   []Audit        `json:"data"`
	Meta   PaginationMeta `json:"paginationmeta"`
}

// Obligation represents an obligation record in the database.
type Obligation struct {
	Id             int64  `json:"id" gorm:"primary_key" example:"147"`
	Topic          string `json:"topic" gorm:"unique" example:"copyleft"`
	Type           string `json:"type" enums:"obligation,restriction,risk,right"`
	Text           string `json:"text" example:"Source code be made available when distributing the software."`
	Classification string `json:"classification" enums:"green,white,yellow,red"`
	Modifications  bool   `json:"modifications"`
	Comment        string `json:"comment" example:"This is a comment."`
	Active         bool   `json:"active" gorm:"column:active"`
	TextUpdatable  bool   `json:"text_updatable"`
	Md5            string `json:"md5" gorm:"unique" example:"deadbeef"`
}

// ObligationInput represents the input format for creating a new obligation.
type ObligationInput struct {
	Topic          string   `json:"topic" binding:"required" example:"copyleft"`
	Type           string   `json:"type" binding:"required" enums:"obligation,restriction,risk,right"`
	Text           string   `json:"text" binding:"required" example:"Source code be made available when distributing the software."`
	Classification string   `json:"classification" enums:"green,white,yellow,red"`
	Modifications  bool     `json:"modifications"`
	Comment        string   `json:"comment" example:"This is a comment."`
	Active         bool     `json:"active" example:"true"`
	TextUpdatable  bool     `json:"text_updatable"`
	Shortnames     []string `json:"shortnames" example:"GPL-2.0-only,GPL-2.0-or-later"`
}

// UpdateObligation represents the input format for updating an existing obligation.
type UpdateObligation struct {
	Topic          string `json:"topic" binding:"required" example:"copyleft"`
	Type           string `json:"type" binding:"required" enums:"obligation,restriction,risk,right"`
	Text           string `json:"text" binding:"required" example:"Source code be made available when distributing the software."`
	Classification string `json:"classification" enums:"green,white,yellow,red"`
	Modifications  bool   `json:"modifications"`
	Comment        string `json:"comment" example:"This is a comment."`
	Active         bool   `json:"active" example:"true"`
	TextUpdatable  bool   `json:"text_updatable"`
}

// ObligationResponse represents the response format for obligation data.
type ObligationResponse struct {
	Status int            `json:"status" example:"200"`
	Data   []Obligation   `json:"data"`
	Meta   PaginationMeta `json:"paginationmeta"`
}

// ObligationMap represents the mapping between an obligation and a license.
type ObligationMap struct {
	ObligationPk int64      `json:"obligation_pk"`
	Obligation   Obligation `gorm:"foreignKey:ObligationPk;references:Id" json:"-"`
	OmPk         int64      `json:"om_pk" gorm:"primary_key"`
	RfPk         int64      `json:"rf_pk"`
	LicenseDB    LicenseDB  `gorm:"foreignKey:RfPk;references:Id" json:"-"`
}

// ObligationMapUser Structure with obligation topic and license shortname list, a simple representation for user.
type ObligationMapUser struct {
	Topic      string   `json:"topic" example:"copyleft"`
	Shortnames []string `json:"shortnames" example:"GPL-2.0-only,GPL-2.0-or-later"`
}

// LicenseShortnamesInput represents the input format for adding/removing licenses from obligation map.
type LicenseShortnamesInput struct {
	Shortnames []string `json:"shortnames" example:"GPL-2.0-only,GPL-2.0-or-later"`
}

// LicenseMapShortnamesElement Element to hold license shortname and action
type LicenseMapShortnamesElement struct {
	Shortname string `json:"shortname" example:"GPL-2.0-only"`
	Add       bool   `json:"add" example:"true"`
}

// LicenseMapShortnamesInput List of elements to be read as input by API
type LicenseMapShortnamesInput struct {
	MapInput []LicenseMapShortnamesElement `json:"map"`
}

// ObligationMapResponse response format for obligation map data.
type ObligationMapResponse struct {
	Status int                 `json:"status" example:"200"`
	Data   []ObligationMapUser `json:"data"`
	Meta   PaginationMeta      `json:"paginationmeta"`
}
