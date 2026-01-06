// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
// SPDX-FileContributor: 2025 Chayan Das <01chayandas@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package models

import (
	"errors"
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

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
	Id           uuid.UUID `json:"id" gorm:"primary_key;type:uuid;column:id;default:uuid_generate_v4()" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
	UserName     *string   `json:"user_name" gorm:"column:user_name" example:"fossy"`
	DisplayName  *string   `json:"display_name" gorm:"column:display_name" example:"fossy"`
	UserEmail    *string   `json:"user_email" gorm:"column:user_email" example:"fossy@org.com"`
	UserLevel    *string   `json:"user_level" gorm:"column:user_level" example:"USER"`
	UserPassword *string   `json:"-" gorm:"column:user_password"`
	Active       *bool     `json:"-" gorm:"column:active;default:true"`
}

func (User) TableName() string {
	return "users"
}

// UserClaim struct represents the claims present in the JWT token.
type UserClaim struct {
	Id          uuid.UUID `json:"id" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
	UserName    *string   `json:"user_name" example:"fossy"`
	DisplayName *string   `json:"display_name" example:"fossy"`
	UserEmail   *string   `json:"user_email" example:"fossy@example.com"`
	UserLevel   *string   `json:"user_level" example:"ADMIN"`
}

func (u *User) BeforeCreate(tx *gorm.DB) (err error) {
	if u.UserName != nil && *u.UserName == "" {
		return errors.New("username cannot be an empty string")
	}
	if u.DisplayName != nil && *u.DisplayName == "" {
		return errors.New("display_name cannot be an empty string")
	}
	if u.UserEmail != nil && *u.UserEmail == "" {
		return errors.New("user email cannot be an empty string")
	}
	if u.UserLevel != nil && *u.UserLevel == "" {
		return errors.New("user level cannot be an empty string")
	}
	return
}

func (u *User) BeforeUpdate(tx *gorm.DB) (err error) {
	if u.UserName != nil && *u.UserName == "" {
		return errors.New("username cannot be an empty string")
	}
	if u.DisplayName != nil && *u.DisplayName == "" {
		return errors.New("display_name cannot be an empty string")
	}
	if u.UserEmail != nil && *u.UserEmail == "" {
		return errors.New("user email cannot be an empty string")
	}
	if u.UserLevel != nil && *u.UserLevel == "" {
		return errors.New("user level cannot be an empty string")
	}
	if u.UserPassword != nil && *u.UserPassword == "" {
		return errors.New("user password cannot be an empty string")
	}
	return
}

type UserCreate struct {
	Id           uuid.UUID `json:"-"`
	UserName     *string   `json:"user_name" validate:"required" example:"fossy"`
	DisplayName  *string   `json:"display_name" validate:"required" example:"fossy"`
	UserEmail    *string   `json:"user_email" validate:"required,email" example:"fossy@org.com"`
	UserLevel    *string   `json:"user_level" validate:"required,oneof=USER ADMIN" example:"ADMIN"`
	UserPassword *string   `json:"user_password" example:"fossy"`
	Active       *bool     `json:"-"`
}

type UserUpdate struct {
	Id           uuid.UUID `json:"-"`
	UserName     *string   `json:"user_name" example:"fossy"`
	DisplayName  *string   `json:"display_name" example:"fossy"`
	UserEmail    *string   `json:"user_email" validate:"omitempty,email"`
	UserLevel    *string   `json:"user_level" validate:"omitempty,oneof=USER ADMIN" example:"ADMIN"`
	UserPassword *string   `json:"user_password"`
	Active       *bool     `json:"active"`
}

type ProfileUpdate struct {
	Id           uuid.UUID `json:"-"`
	UserName     *string   `json:"-"`
	DisplayName  *string   `json:"display_name" example:"fossy"`
	UserEmail    *string   `json:"user_email" validate:"omitempty,email"`
	UserLevel    *string   `json:"-"`
	UserPassword *string   `json:"user_password"`
	Active       *bool     `json:"-"`
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
	Field      string `json:"field" binding:"required" example:"text"`
	SearchTerm string `json:"search_term" binding:"required" example:"MIT License"`
	Search     string `json:"search" enums:"fuzzy,full_text_search"`
}

// Audit struct represents an audit entity with certain attributes and properties
// It has user id as a foreign key
type Audit struct {
	Id         uuid.UUID   `json:"id" gorm:"primary_key;type:uuid;column:id;default:uuid_generate_v4()" swaggertype:"string" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6"`
	UserId     uuid.UUID   `json:"user_id" gorm:"type:uuid;column:user_id" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
	User       User        `gorm:"foreignKey:UserId;references:Id" json:"user"`
	Timestamp  time.Time   `json:"timestamp" gorm:"column:timestamp" example:"2023-12-01T18:10:25.00+05:30"`
	Type       string      `json:"type" gorm:"column:type" enums:"OBLIGATION,LICENSE,USER" example:"LICENSE"`
	TypeId     uuid.UUID   `json:"type_id" gorm:"type:uuid;column:type_id" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
	Entity     interface{} `json:"entity" gorm:"-" swaggertype:"object"`
	ChangeLogs []ChangeLog `json:"-"`
}

func (Audit) TableName() string {
	return "audits"
}

// ChangeLog struct represents a change entity with certain attributes and properties
type ChangeLog struct {
	Id           uuid.UUID `json:"id" gorm:"type:uuid;primary_key;default:uuid_generate_v4()" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
	Field        string    `json:"field" example:"text"`
	UpdatedValue *string   `json:"updated_value" example:"New license text"`
	OldValue     *string   `json:"old_value" example:"Old license text"`
	AuditId      uuid.UUID `json:"audit_id" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
	Audit        Audit     `gorm:"foreignKey:AuditId;references:Id" json:"-"`
}

func (ChangeLog) TableName() string {
	return "change_logs"
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

// ObligationType represents one of the possible of obligation type values
type ObligationType struct {
	Id     uuid.UUID `gorm:"type:uuid;primary_key;column:id;default:uuid_generate_v4()" json:"-"`
	Type   string    `gorm:"column:type" validate:"required,uppercase" example:"PERMISSION" json:"type"`
	Active *bool     `gorm:"column:active;default:true" json:"-"`
}

func (ObligationType) TableName() string {
	return "obligation_types"
}

// ObligationTypeResponse represents the response format for obligation type data.
type ObligationTypeResponse struct {
	Status int              `json:"status" example:"200"`
	Data   []ObligationType `json:"data"`
	Meta   *PaginationMeta  `json:"paginationmeta"`
}

// ObligationClassification represents one of the possible of obligation classification values
type ObligationClassification struct {
	Id             uuid.UUID `gorm:"type:uuid;primary_key;column:id;default:uuid_generate_v4()" json:"-"`
	Classification string    `gorm:"column:classification" validate:"required,uppercase" example:"GREEN" json:"classification"`
	Color          string    `gorm:"column:color" validate:"required,hexcolor" example:"#00FF00" json:"color"`
	Active         *bool     `gorm:"column:active;default:true" json:"-"`
}

func (ObligationClassification) TableName() string {
	return "obligation_classifications"
}

// ObligationClassificationResponse represents the response format for obligation classification data.
type ObligationClassificationResponse struct {
	Status int                        `json:"status" example:"200"`
	Data   []ObligationClassification `json:"data"`
	Meta   *PaginationMeta            `json:"paginationmeta"`
}

type ObligationMapLicenseFormat struct {
	Id        uuid.UUID `json:"id" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
	Shortname string    `json:"shortname" example:"MIT"`
}

// ObligationMapUser Structure with obligation topic and license shortname list, a simple representation for user.
type ObligationMapUser struct {
	Id       uuid.UUID                    `json:"id" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
	Topic    string                       `json:"topic" example:"copyleft"`
	Type     string                       `json:"type" example:"obligation" enums:"obligation,restriction,risk,right"`
	Licenses []ObligationMapLicenseFormat `json:"licenses"`
}

// LicenseShortnamesInput represents the input format for adding/removing licenses from obligation map.
type LicenseListInput struct {
	LicenseIds []uuid.UUID `json:"ids" swaggertype:"array,object"`
}

// LicenseMapElement Element to hold license
type LicenseMapElement struct {
	Id  uuid.UUID `json:"id" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
	Add bool      `json:"add" example:"true"`
}

// LicenseMapInput List of elements to be read as input by API
type LicenseMapInput struct {
	MapInput []LicenseMapElement `json:"map"`
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

// ObligationId is the id of successfully imported obligation
type ObligationId struct {
	Id    uuid.UUID `json:"id" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
	Topic string    `json:"topic" example:"copyleft"`
}

// ObligationImportStatus is the status of obligation records successfully inserted in the database during import
type ObligationImportStatus struct {
	Status  int          `json:"status" example:"200"`
	Data    ObligationId `json:"data"`
	Message string       `json:"message"`
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

type RiskLicenseCount struct {
	Risk  int64 `json:"risk" example:"2"`
	Count int64 `json:"count" example:"6"`
}

type CategoryObligationCount struct {
	Category string `json:"category" example:"GENERAL"`
	Count    int64  `json:"count" example:"6"`
}

type Dashboard struct {
	LicensesCount                int64                     `json:"licenses_count" example:"2"`
	ObligationsCount             int64                     `json:"obligations_count" example:"7"`
	UsersCount                   int64                     `json:"users_count" example:"5"`
	LicenseChangesSinceLastMonth int64                     `json:"monthly_license_changes_count" example:"6"`
	RiskLicenseFrequency         []RiskLicenseCount        `json:"risk_license_frequency"`
	CategoryObligationFrequency  []CategoryObligationCount `json:"category_obligation_frequency"`
}

type DashboardResponse struct {
	Status int       `json:"status" example:"200"`
	Data   Dashboard `json:"data"`
}

// ApiResponse is a generic response structure for API responses.
type ApiResponse[T any] struct {
	Status int `json:"status"`
	Data   T   `json:"data,omitempty"`
	Meta   any `json:"meta,omitempty"`
}

type Tokens struct {
	AccessToken          string `json:"access_token" example:"your_access_token_here"`
	RefreshToken         string `json:"refresh_token,omitempty" example:"your_refresh_token_here"`
	AccessTokenExpiresIn int64  `json:"expires_in" example:"3600"`
}

type RefreshToken struct {
	RefreshToken string `json:"refresh_token" example:"your_refresh_token_here"`
}

// TokenResonse represents the response structure for token generation API.
type TokenResonse ApiResponse[Tokens]

// can add all other response structures in similar manner
