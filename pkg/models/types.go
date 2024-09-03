// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package models

import (
	"errors"
	"time"

	"gorm.io/datatypes"
	"gorm.io/gorm"
)

// The LicenseDB struct represents a license entity with various attributes and
// properties associated with it.
// It provides structured storage for license-related information.
type LicenseDB struct {
	Id              int64                                        `json:"-" gorm:"primary_key;column:rf_id" example:"123"`
	Shortname       *string                                      `json:"rf_shortname" gorm:"unique;not null;column:rf_shortname" validate:"required" example:"MIT"`
	Fullname        *string                                      `json:"rf_fullname" gorm:"column:rf_fullname;not null" validate:"required" example:"MIT License"`
	Text            *string                                      `json:"rf_text" gorm:"column:rf_text;not null" validate:"required" example:"MIT License Text here"`
	Url             *string                                      `json:"rf_url" gorm:"column:rf_url;default:'';not null" example:"https://opensource.org/licenses/MIT"`
	AddDate         time.Time                                    `json:"rf_add_date" gorm:"default:CURRENT_TIMESTAMP;column:rf_add_date" example:"2023-12-01T18:10:25.00+05:30"`
	Copyleft        *bool                                        `json:"rf_copyleft" gorm:"column:rf_copyleft;not null;default:false"`
	FSFfree         *bool                                        `json:"rf_FSFfree" gorm:"column:rf_FSFfree;not null;default:false"`
	OSIapproved     *bool                                        `json:"rf_OSIapproved" gorm:"column:rf_OSIapproved;not null;default:false"`
	GPLv2compatible *bool                                        `json:"rf_GPLv2compatible" gorm:"column:rf_GPLv2compatible;not null;default:false"`
	GPLv3compatible *bool                                        `json:"rf_GPLv3compatible" gorm:"column:rf_GPLv3compatible;not null;default:false"`
	Notes           *string                                      `json:"rf_notes" gorm:"column:rf_notes;not null;default:''" example:"This license has been superseded."`
	Fedora          *string                                      `json:"rf_Fedora" gorm:"column:rf_Fedora;not null;default:''"`
	TextUpdatable   *bool                                        `json:"rf_text_updatable" gorm:"column:rf_text_updatable;not null;default:false"`
	DetectorType    *int64                                       `json:"rf_detector_type" gorm:"column:rf_detector_type;not null;default:1" validate:"omitempty,min=0,max=2" example:"1"`
	Active          *bool                                        `json:"rf_active" gorm:"column:rf_active;not null;default:true"`
	Source          *string                                      `json:"rf_source" gorm:"column:rf_source;not null;default:''"`
	SpdxId          *string                                      `json:"rf_spdx_id" gorm:"column:rf_spdx_id;not null" validate:"required" example:"MIT"`
	Risk            *int64                                       `json:"rf_risk" gorm:"column:rf_risk;not null;default:0" validate:"omitempty,min=0,max=5"`
	Flag            *int64                                       `json:"rf_flag" gorm:"default:1;column:rf_flag;not null;default:0" validate:"omitempty,min=0,max=2" example:"1"`
	Marydone        *bool                                        `json:"marydone" gorm:"column:marydone;not null;default:false"`
	ExternalRef     datatypes.JSONType[LicenseDBSchemaExtension] `json:"external_ref"`
}

func (l *LicenseDB) BeforeSave(tx *gorm.DB) (err error) {
	if l.Shortname != nil && *l.Shortname == "" {
		return errors.New("rf_shortname cannot be an empty string")
	}
	if l.Fullname != nil && *l.Fullname == "" {
		return errors.New("rf_fullname cannot be an empty string")
	}
	if l.Text != nil && *l.Text == "" {
		return errors.New("rf_text cannot be an empty string")
	}
	if l.SpdxId != nil && *l.SpdxId == "" {
		return errors.New("rf_spdx_id cannot be an empty string")
	}
	if l.Risk != nil && (*l.Risk < 0 && *l.Risk > 5) {
		return errors.New("rf_risk can have values from 0 to 5 only")
	}
	if l.Flag != nil && (*l.Flag < 0 || *l.Flag > 2) {
		return errors.New("rf_flag can have values from 0 to 2 only")
	}
	if l.DetectorType != nil && (*l.DetectorType < 0 || *l.DetectorType > 2) {
		return errors.New("rf_detector_type can have values from 0 to 2 only")
	}
	return
}

// LicenseUpdateJSONSchema struct represents the input format for updating an existing license.
type LicenseUpdateJSONSchema struct {
	Id              int64                                        `json:"-" example:"123"`
	Shortname       *string                                      `json:"-" example:"MIT"`
	Fullname        *string                                      `json:"rf_fullname" example:"MIT License"`
	Text            *string                                      `json:"rf_text" example:"MIT License Text here"`
	Url             *string                                      `json:"rf_url" example:"https://opensource.org/licenses/MIT"`
	AddDate         time.Time                                    `json:"-" example:"2023-12-01T18:10:25.00+05:30"`
	Copyleft        *bool                                        `json:"rf_copyleft" example:"false"`
	FSFfree         *bool                                        `json:"rf_FSFfree" example:"false"`
	OSIapproved     *bool                                        `json:"rf_OSIapproved" example:"false"`
	GPLv2compatible *bool                                        `json:"rf_GPLv2compatible" example:"false"`
	GPLv3compatible *bool                                        `json:"rf_GPLv3compatible" example:"false"`
	Notes           *string                                      `json:"rf_notes" example:"This license has been superseded."`
	Fedora          *string                                      `json:"rf_Fedora" example:"Fedora"`
	TextUpdatable   *bool                                        `json:"rf_text_updatable" example:"false"`
	DetectorType    *int64                                       `json:"rf_detector_type" validate:"omitempty,min=0,max=2" example:"1"`
	Active          *bool                                        `json:"rf_active" example:"true"`
	Source          *string                                      `json:"rf_source" example:"Source"`
	SpdxId          *string                                      `json:"rf_spdx_id" example:"MIT"`
	Risk            *int64                                       `json:"rf_risk" validate:"omitempty,min=0,max=5" example:"1"`
	Flag            *int64                                       `json:"rf_flag" validate:"omitempty,min=0,max=2" example:"1"`
	Marydone        *bool                                        `json:"marydone" example:"false"`
	ExternalRef     datatypes.JSONType[LicenseDBSchemaExtension] `json:"external_ref"`
}

// UpdateExternalRefsJSONPayload struct represents the external ref key value pairs for update
type UpdateExternalRefsJSONPayload struct {
	ExternalRef map[string]interface{} `json:"external_ref"`
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

// LicensePreviewResponse gets us the list of all license shortnames
type LicensePreviewResponse struct {
	Status     int      `json:"status" example:"200"`
	Shortnames []string `json:"shortnames" example:"GPL-2.0-only,GPL-2.0-or-later"`
}

// LicenseId is the id of successfully imported license
type LicenseId struct {
	Id        int64  `json:"id" example:"31"`
	Shortname string `json:"shortname" example:"MIT"`
}

// LicenseImportStatus is the status of license records successfully inserted in the database during import
type LicenseImportStatus struct {
	Status int       `json:"status" example:"200"`
	Data   LicenseId `json:"data"`
}

// ImportObligationsResponse is the response structure for import obligation response
type ImportLicensesResponse struct {
	Status int           `json:"status" example:"200"`
	Data   []interface{} `json:"data"` // can be of type models.LicenseError or models.LicenseImportStatus
}

// The PaginationMeta struct represents additional metadata associated with a
// license retrieval operation.
// It contains information that provides context and supplementary details
// about the retrieved license data.
type PaginationMeta struct {
	ResourceCount int    `json:"resource_count" example:"200"`
	TotalPages    int64  `json:"total_pages,omitempty" example:"20"`
	Page          int64  `json:"page,omitempty" example:"10"`
	Limit         int64  `json:"limit,omitempty" example:"10"`
	Next          string `json:"next,omitempty" example:"/api/v1/licenses?limit=10&page=11"`
	Previous      string `json:"previous,omitempty" example:"/api/v1/licenses?limit=10&page=9"`
}

// The PaginationInput struct represents the input required for pagination.
type PaginationInput struct {
	Page  int64 `json:"page" example:"10"`
	Limit int64 `json:"limit" example:"10"`
}

// PaginationParse interface processes the pagination input.
type PaginationParse interface {
	GetOffset() int
	GetLimit() int
}

// GetOffset returns the offset value for gorm.
func (p PaginationInput) GetOffset() int64 {
	return (p.Page - 1) * p.Limit
}

// GetLimit returns the limit value for gorm.
func (p PaginationInput) GetLimit() int64 {
	return p.Limit
}

// LicenseResponse struct is representation of design API response of license.
// The LicenseResponse struct represents the response data structure for
// retrieving license information.
// It is used to encapsulate license-related data in an organized manner.
type LicenseResponse struct {
	Status int             `json:"status" example:"200"`
	Data   []LicenseDB     `json:"data"`
	Meta   *PaginationMeta `json:"paginationmeta"`
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

// User struct is representation of user information.
type User struct {
	Id           int64   `json:"id" gorm:"primary_key" example:"123"`
	Username     string  `json:"username" gorm:"unique;not null" binding:"required" example:"fossy"`
	Userlevel    string  `json:"userlevel" binding:"required" example:"admin"`
	Userpassword *string `json:"-"`
}

type UserInput struct {
	Username     string  `json:"username" gorm:"unique;not null" binding:"required" example:"fossy"`
	Userlevel    string  `json:"userlevel" binding:"required" example:"admin"`
	Userpassword *string `json:"password,omitempty" binding:"required" example:"fossy"`
}

type UserLogin struct {
	Username     string `json:"username" binding:"required" example:"fossy"`
	Userpassword string `json:"password" binding:"required" example:"fossy"`
}

// UserResponse struct is representation of design API response of user.
type UserResponse struct {
	Status int             `json:"status" example:"200"`
	Data   []User          `json:"data"`
	Meta   *PaginationMeta `json:"paginationmeta"`
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
	Id         int64       `json:"id" gorm:"primary_key" example:"456"`
	UserId     int64       `json:"user_id" example:"123"`
	User       User        `gorm:"foreignKey:UserId;references:Id" json:"user"`
	Timestamp  time.Time   `json:"timestamp" example:"2023-12-01T18:10:25.00+05:30"`
	Type       string      `json:"type" enums:"obligation,license" example:"license"`
	TypeId     int64       `json:"type_id" example:"34"`
	Entity     interface{} `json:"entity" gorm:"-" swaggertype:"object"`
	ChangeLogs []ChangeLog `json:"-"`
}

// ChangeLog struct represents a change entity with certain attributes and properties
type ChangeLog struct {
	Id           int64   `json:"id" gorm:"primary_key" example:"789"`
	Field        string  `json:"field" example:"rf_text"`
	UpdatedValue *string `json:"updated_value" example:"New license text"`
	OldValue     *string `json:"old_value" example:"Old license text"`
	AuditId      int64   `json:"audit_id" example:"456"`
	Audit        Audit   `gorm:"foreignKey:AuditId;references:Id" json:"-"`
}

// ChangeLogResponse represents the design of API response of change log
type ChangeLogResponse struct {
	Status int            `json:"status" example:"200"`
	Data   []ChangeLog    `json:"data"`
	Meta   PaginationMeta `json:"paginationmeta"`
}

// AuditResponse represents the response format for audit data.
type AuditResponse struct {
	Status int             `json:"status" example:"200"`
	Data   []Audit         `json:"data"`
	Meta   *PaginationMeta `json:"paginationmeta"`
}

// Obligation represents an obligation record in the database.
type Obligation struct {
	Id             int64  `gorm:"primary_key" json:"id" example:"147"`
	Topic          string `gorm:"unique" json:"topic" example:"copyleft"`
	Type           string `json:"type" enums:"obligation,restriction,risk,right" example:"risk"`
	Text           string `json:"text" example:"Source code be made available when distributing the software."`
	Classification string `json:"classification" enums:"green,white,yellow,red" example:"green"`
	Modifications  bool   `json:"modifications" example:"true"`
	Comment        string `json:"comment"`
	Active         bool   `json:"active"`
	TextUpdatable  bool   `json:"text_updatable" example:"true"`
	Md5            string `gorm:"unique" json:"-"`
}

// ObligationPreview is just the Type and Topic of Obligation
type ObligationPreview struct {
	Topic string `json:"topic" example:"Provide Copyright Notices"`
	Type  string `json:"type" enums:"obligation,restriction,risk,right"`
}

// ObligationResponse represents the response format for obligation data.
type ObligationPreviewResponse struct {
	Status int                 `json:"status" example:"200"`
	Data   []ObligationPreview `json:"data"`
}

// ObligationPOSTRequestJSONSchema represents the data format of POST request for obligation
type ObligationPOSTRequestJSONSchema struct {
	Topic          string   `json:"topic" binding:"required" example:"copyleft"`
	Type           string   `json:"type" enums:"obligation,restriction,risk,right" binding:"required"`
	Text           string   `json:"text" binding:"required" example:"Source code be made available when distributing the software."`
	Classification string   `json:"classification" enums:"green,white,yellow,red" binding:"required"`
	Modifications  bool     `json:"modifications" binding:"required"`
	Comment        string   `json:"comment" binding:"required"`
	Shortnames     []string `json:"shortnames" binding:"required" example:"GPL-2.0-only,GPL-2.0-or-later"`
	Active         bool     `json:"active" binding:"required" example:"true"`
}

// ObligationPATCHRequestJSONSchema represents the data format of PATCH request for obligation
type ObligationPATCHRequestJSONSchema struct {
	Type           OptionalData[string] `json:"type" swaggertype:"string" enums:"obligation,restriction,risk,right"`
	Text           OptionalData[string] `json:"text" swaggertype:"string" example:"Source code be made available when distributing the software."`
	Classification OptionalData[string] `json:"classification" swaggertype:"string" enums:"green,white,yellow,red"`
	Modifications  OptionalData[bool]   `json:"modifications" swaggertype:"boolean"`
	Comment        OptionalData[string] `json:"comment" swaggertype:"string" example:"This is a comment."`
	Active         OptionalData[bool]   `json:"active" swaggertype:"boolean" example:"true"`
	TextUpdatable  OptionalData[bool]   `json:"text_updatable" swaggertype:"boolean"`
}

// ObligationResponse represents the response format for obligation data.
type ObligationResponse struct {
	Status int             `json:"status" example:"200"`
	Data   []Obligation    `json:"data"`
	Meta   *PaginationMeta `json:"paginationmeta"`
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
	Type       string   `json:"type" example:"obligation" enums:"obligation,restriction,risk,right"`
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

// ObligationImportRequest represents the request body structure for import obligation
type ObligationImportRequest struct {
	ObligationFile string `form:"file"`
}

// ObligationJSONFileFormat represents an obligation record in the import/export json file.
type ObligationJSONFileFormat struct {
	Topic          string   `json:"topic" example:"copyleft" validate:"required"` // binding:"required" tag cannot be used as is works only for request body
	Type           string   `json:"type" enums:"obligation,restriction,risk,right" validate:"required"`
	Text           string   `json:"text" example:"Source code be made available when distributing the software." validate:"required"`
	Classification string   `json:"classification" enums:"green,white,yellow,red" validate:"required"`
	Modifications  bool     `json:"modifications" validate:"required"`
	Comment        string   `json:"comment" example:"This is a comment." validate:"required"`
	Active         bool     `json:"active" validate:"required"`
	TextUpdatable  bool     `json:"text_updatable" validate:"required"`
	Shortnames     []string `json:"shortnames" example:"GPL-2.0-only,GPL-2.0-or-later" validate:"required"`
}

// ObligationId is the id of successfully imported obligation
type ObligationId struct {
	Id    int64  `json:"id" example:"31"`
	Topic string `json:"topic" example:"copyleft"`
}

// ObligationImportStatus is the status of obligation records successfully inserted in the database during import
type ObligationImportStatus struct {
	Status int          `json:"status" example:"200"`
	Data   ObligationId `json:"data"`
}

// ImportObligationsResponse is the response structure for import obligation response
type ImportObligationsResponse struct {
	Status int           `json:"status" example:"200"`
	Data   []interface{} `json:"data"` // can be of type models.LicenseError or models.ObligationImportStatus
}

// Api contains the information about an endpoint
type Api struct {
	Href          string `json:"href" example:"/api/v1/licenses"`
	RequestMethod string `json:"request_method" enums:"POST,PATCH,DELETE,PUT,GET" example:"POST"`
}

// LinksCollection is a collection of links
type LinksCollection struct {
	Links map[string]Api `json:"_links" swaggertype:"object,string" example:"licenses:{}"`
}

// APICollection is the object that lists which apis require authentication and which do not
type APICollection struct {
	Authenticated   LinksCollection `json:"authenticated" swaggertype:"object"`
	UnAuthenticated LinksCollection `json:"unAuthenticated" swaggertype:"object"`
}

// APICollectionResponse represents the response format for api collection data.
type APICollectionResponse struct {
	Status int           `json:"status" example:"200"`
	Data   APICollection `json:"data"`
}

// SwaggerDocAPISecurityScheme is the json schema describing info about various apis
type SwaggerDocAPISecurityScheme struct {
	BasePath string `json:"basePath" example:"/api/v1"`
	Paths    map[string]map[string]struct {
		Security    []map[string]interface{} `json:"security" swaggertype:"array,object"`
		OperationId string                   `json:"operationId" example:"GetLicense"`
	} `json:"paths"`
}
