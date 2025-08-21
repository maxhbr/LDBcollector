// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
// SPDX-FileContributor: 2025 Chayan Das <01chayandas@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package models

import (
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"time"

	"github.com/fossology/LicenseDb/pkg/validations"
	"github.com/go-playground/validator/v10"
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
	Id           int64   `json:"id" gorm:"primary_key;column:id" example:"123"`
	UserName     *string `json:"user_name" gorm:"column:user_name" example:"fossy"`
	DisplayName  *string `json:"display_name" gorm:"column:display_name" example:"fossy"`
	UserEmail    *string `json:"user_email" gorm:"column:user_email" example:"fossy@org.com"`
	UserLevel    *string `json:"user_level" gorm:"column:user_level" example:"USER"`
	UserPassword *string `json:"-" gorm:"column:user_password"`
	Active       *bool   `json:"-" gorm:"column:active;default:true"`
}

func (User) TableName() string {
	return "users"
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
	Id           int64   `json:"-"`
	UserName     *string `json:"user_name" validate:"required" example:"fossy"`
	DisplayName  *string `json:"display_name" validate:"required" example:"fossy"`
	UserEmail    *string `json:"user_email" validate:"required,email" example:"fossy@org.com"`
	UserLevel    *string `json:"user_level" validate:"required,oneof=USER ADMIN" example:"ADMIN"`
	UserPassword *string `json:"user_password" example:"fossy"`
	Active       *bool   `json:"-"`
}

type UserUpdate struct {
	Id           int64   `json:"-"`
	UserName     *string `json:"user_name" example:"fossy"`
	DisplayName  *string `json:"display_name" example:"fossy"`
	UserEmail    *string `json:"user_email" validate:"omitempty,email"`
	UserLevel    *string `json:"user_level" validate:"omitempty,oneof=USER ADMIN" example:"ADMIN"`
	UserPassword *string `json:"user_password"`
	Active       *bool   `json:"active"`
}

type ProfileUpdate struct {
	Id           int64   `json:"-"`
	UserName     *string `json:"-"`
	DisplayName  *string `json:"display_name" example:"fossy"`
	UserEmail    *string `json:"user_email" validate:"omitempty,email"`
	UserLevel    *string `json:"-"`
	UserPassword *string `json:"user_password"`
	Active       *bool   `json:"-"`
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
	Id         int64       `json:"id" gorm:"primary_key;column:id" example:"456"`
	UserId     int64       `json:"user_id" gorm:"column:user_id" example:"123"`
	User       User        `gorm:"foreignKey:UserId;references:Id" json:"user"`
	Timestamp  time.Time   `json:"timestamp" gorm:"column:timestamp" example:"2023-12-01T18:10:25.00+05:30"`
	Type       string      `json:"type" gorm:"column:type" enums:"OBLIGATION,LICENSE,USER" example:"LICENSE"`
	TypeId     int64       `json:"type_id" gorm:"column:type_id" example:"34"`
	Entity     interface{} `json:"entity" gorm:"-" swaggertype:"object"`
	ChangeLogs []ChangeLog `json:"-"`
}

func (Audit) TableName() string {
	return "audits"
}

// ChangeLog struct represents a change entity with certain attributes and properties
type ChangeLog struct {
	Id           int64   `json:"id" gorm:"primary_key" example:"789"`
	Field        string  `json:"field" example:"text"`
	UpdatedValue *string `json:"updated_value" example:"New license text"`
	OldValue     *string `json:"old_value" example:"Old license text"`
	AuditId      int64   `json:"audit_id" example:"456"`
	Audit        Audit   `gorm:"foreignKey:AuditId;references:Id" json:"-"`
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
	Id     int64  `gorm:"primary_key column:id" json:"-"`
	Type   string `gorm:"column:type" validate:"required,uppercase" example:"PERMISSION" json:"type"`
	Active *bool  `gorm:"column:active;default:true" json:"-"`
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
	Id             int64  `gorm:"primary_key column:id" json:"-"`
	Classification string `gorm:"column:classification" validate:"required,uppercase" example:"GREEN" json:"classification"`
	Color          string `gorm:"column:color" validate:"required,hexcolor" example:"#00FF00" json:"color"`
	Active         *bool  `gorm:"column:active;default:true" json:"-"`
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

// Obligation represents an obligation record in the database.
type Obligation struct {
	Id                         int64                     `gorm:"primary_key;column:id" `
	Topic                      *string                   `gorm:"column:topic"`
	Text                       *string                   `gorm:"column:text"`
	Modifications              *bool                     `gorm:"column:modifications;default:false"`
	Comment                    *string                   `gorm:"column:comment"`
	Active                     *bool                     `gorm:"column:active;default:true"`
	TextUpdatable              *bool                     `gorm:"column:text_updatable;default:false" `
	Md5                        string                    `gorm:"column:md5"`
	ObligationClassificationId int64                     `gorm:"column:obligation_classification_id"`
	ObligationTypeId           int64                     `gorm:"column:obligation_type_id"`
	Licenses                   []*LicenseDB              `gorm:"many2many:obligation_licenses; joinForeignKey:obligation_id;joinReferences: license_db_id "`
	Type                       *ObligationType           `gorm:"foreignKey:ObligationTypeId; references:Id"`
	Classification             *ObligationClassification `gorm:"foreignKey:ObligationClassificationId ;references:Id"`
	Category                   *string                   `json:"category" gorm:"default:GENERAL" enums:"DISTRIBUTION,PATENT,INTERNAL,CONTRACTUAL,EXPORT_CONTROL,GENERAL" example:"DISTRIBUTION"`
}

func (Obligation) TableName() string {
	return "obligations"
}

var validCategories = []string{"DISTRIBUTION", "PATENT", "INTERNAL", "CONTRACTUAL", "EXPORT_CONTROL", "GENERAL"}

func validateCategory(o *Obligation) error {
	allCategories := strings.Join(validCategories, ", ")
	// Check if the provided category is in the list of valid categories
	categoryValid := false
	for _, cat := range validCategories {
		if *o.Category == cat {
			categoryValid = true
			break
		}
	}
	if !categoryValid {
		return fmt.Errorf("category must be one of the following values: %s", allCategories)
	}
	return nil
}

func (o *Obligation) BeforeCreate(tx *gorm.DB) (err error) {
	if o.Topic != nil && *o.Topic == "" {
		return errors.New("topic cannot be an empty string")
	}
	// Checks whether the obligation type value passed on by the user is a valid value or not
	// i.e. it should be already present in the obligation_type table. Then the object queried
	// from the database is assigned to the Type field because it has primary key. Objects passed
	// on without primary key are first saved into db and then foreignkey references are saved.
	if o.Type != nil {
		var obTypes []ObligationType
		if err := tx.Find(&obTypes).Error; err != nil {
			return err
		}
		allTypes := ""
		for i := 0; i < len(obTypes); i++ {
			if obTypes[i].Active != nil && *obTypes[i].Active {
				allTypes += fmt.Sprintf(" %s", obTypes[i].Type)
				if o.Type.Type == obTypes[i].Type {
					o.Type = &obTypes[i]
				}
			}
		}
		if o.Type.Id == 0 {
			return fmt.Errorf("obligation type must be one of the following values:%s", allTypes)
		}
	}
	if o.Text != nil {
		if *o.Text == "" {
			return errors.New("text cannot be an empty string")
		} else {
			s := *o.Text
			hash := md5.Sum([]byte(s))
			md5hash := hex.EncodeToString(hash[:])
			o.Md5 = md5hash
		}
	}
	if o.Classification != nil {
		var obClassifications []ObligationClassification
		if err := tx.Find(&obClassifications).Error; err != nil {
			return err
		}
		allClassifications := ""
		for i := 0; i < len(obClassifications); i++ {
			if *obClassifications[i].Active {
				allClassifications += fmt.Sprintf(" %s", obClassifications[i].Classification)
				if o.Classification.Classification == obClassifications[i].Classification {
					o.Classification = &obClassifications[i]
				}
			}
		}
		if o.Classification.Id == 0 {
			return fmt.Errorf("obligation classification must be one of the following values:%s", allClassifications)
		}
	}

	if err := validateCategory(o); err != nil {
		return err
	}

	for i := 0; i < len(o.Licenses); i++ {
		var license LicenseDB
		if err := tx.Where(LicenseDB{Shortname: o.Licenses[i].Shortname}).First(&license).Error; err != nil {
			return fmt.Errorf("license with shortname %s not found", *o.Licenses[i].Shortname)
		}
		o.Licenses[i] = &license
	}

	return nil
}

type ContextKey string

func (o *Obligation) BeforeUpdate(tx *gorm.DB) (err error) {
	oldObligation, ok := tx.Statement.Context.Value(ContextKey("oldObligation")).(*Obligation)
	if !ok {
		return errors.New("something went wrong")
	}

	if o.Topic != nil && *o.Topic == "" {
		return errors.New("topic cannot be an empty string")
	}

	if o.Type != nil {
		var obTypes []ObligationType
		if err := tx.Find(&obTypes).Error; err != nil {
			return err
		}
		allTypes := ""
		for i := 0; i < len(obTypes); i++ {
			if obTypes[i].Active != nil && *obTypes[i].Active {
				allTypes += fmt.Sprintf(" %s", obTypes[i].Type)
				if o.Type.Type == obTypes[i].Type {
					o.Type = &obTypes[i]
				}
			}
		}
		if o.Type.Id == 0 {
			return fmt.Errorf("obligation type must be one of the following values:%s", allTypes)
		}
	}
	if o.Text != nil {
		if *o.Text == "" {
			return errors.New("text cannot be an empty string")
		} else {
			hash := md5.Sum([]byte(*o.Text))
			o.Md5 = hex.EncodeToString(hash[:])
			if !*oldObligation.TextUpdatable {
				if o.Md5 != oldObligation.Md5 {
					return errors.New("can not update obligation text")
				}
			}
		}
	}
	if o.Classification != nil {
		var obClassifications []ObligationClassification
		if err := tx.Find(&obClassifications).Error; err != nil {
			return err
		}
		allClassifications := ""
		for i := 0; i < len(obClassifications); i++ {
			if *obClassifications[i].Active {
				allClassifications += fmt.Sprintf(" %s", obClassifications[i].Classification)
				if o.Classification.Classification == obClassifications[i].Classification {
					o.Classification = &obClassifications[i]
				}
			}
		}
		if o.Classification.Id == 0 {
			return fmt.Errorf("obligation classification must be one of the following values:%s", allClassifications)
		}
	}

	if o.Category != nil {
		if err := validateCategory(o); err != nil {
			return err
		}
	}

	return
}

// Custom json marshaller and unmarshaller for Obligation
func (o *Obligation) MarshalJSON() ([]byte, error) {
	ob := ObligationDTO{
		Topic:         o.Topic,
		Text:          o.Text,
		Modifications: o.Modifications,
		Comment:       o.Comment,
		Active:        o.Active,
		TextUpdatable: o.TextUpdatable,
		Shortnames:    []string{},
		Category:      o.Category,
	}

	if o.Type != nil {
		ob.Type = &o.Type.Type
	}

	if o.Classification != nil {
		ob.Classification = &o.Classification.Classification
	}

	if o.Category != nil && *o.Category != "" {
		ob.Category = o.Category
	} else {
		defaultCategory := "GENERAL"
		ob.Category = &defaultCategory
	}

	for i := 0; i < len(o.Licenses); i++ {
		ob.Shortnames = append(ob.Shortnames, *o.Licenses[i].Shortname)
	}
	return json.Marshal(ob)
}

// Custom JSON unmarshaller for Obligation
func (o *Obligation) UnmarshalJSON(data []byte) error {
	var dto ObligationDTO

	if err := json.Unmarshal(data, &dto); err != nil {
		return err
	}

	if err := validations.Validate.Struct(&dto); err != nil {
		return fmt.Errorf("field '%s' failed validation: %s", err.(validator.ValidationErrors)[0].Field(), err.(validator.ValidationErrors)[0].Tag())
	}

	o.Topic = dto.Topic
	o.Text = dto.Text
	o.Modifications = dto.Modifications
	o.Comment = dto.Comment
	o.Active = dto.Active
	o.TextUpdatable = dto.TextUpdatable
	o.Category = dto.Category

	if dto.Type != nil {
		o.Type = &ObligationType{
			Type: *dto.Type,
		}
	}

	if dto.Classification != nil {
		o.Classification = &ObligationClassification{
			Classification: *dto.Classification,
		}
	}

	o.Licenses = []*LicenseDB{}
	for i := 0; i < len(dto.Shortnames); i++ {
		o.Licenses = append(o.Licenses, &LicenseDB{
			Shortname: &dto.Shortnames[i],
		})
	}

	return nil
}

// ObligationDTO represents an obligation json object.
type ObligationDTO struct {
	Topic          *string  `json:"topic" example:"copyleft" validate:"required"`
	Type           *string  `json:"type" example:"RISK" validate:"required"`
	Text           *string  `json:"text" example:"Source code be made available when distributing the software." validate:"required"`
	Classification *string  `json:"classification" example:"GREEN" validate:"required"`
	Modifications  *bool    `json:"modifications" example:"true"`
	Comment        *string  `json:"comment"`
	Active         *bool    `json:"active"`
	TextUpdatable  *bool    `json:"text_updatable" example:"true"`
	Shortnames     []string `json:"shortnames" validate:"required" example:"GPL-2.0-only,GPL-2.0-or-later"`
	Category       *string  `json:"category" example:"DISTRIBUTION" validate:"required"`
}

// ObligationUpdateDTO represents an obligation json object.
type ObligationUpdateDTO struct {
	Topic          *string `json:"-" example:"copyleft"`
	Type           *string `json:"type" example:"RISK"`
	Text           *string `json:"text" example:"Source code be made available when distributing the software."`
	Classification *string `json:"classification" example:"GREEN"`
	Modifications  *bool   `json:"modifications" example:"true"`
	Comment        *string `json:"comment"`
	Active         *bool   `json:"active"`
	TextUpdatable  *bool   `json:"text_updatable" example:"true"`
	Category       *string `json:"category" example:"DISTRIBUTION"`
}

func (obDto *ObligationUpdateDTO) Converter() *Obligation {
	var o Obligation

	o.Topic = obDto.Topic
	if obDto.Type != nil {
		o.Type = &ObligationType{Type: *obDto.Type}
	}
	o.Text = obDto.Text
	if obDto.Classification != nil {
		o.Classification = &ObligationClassification{Classification: *obDto.Classification}
	}
	o.Modifications = obDto.Modifications
	o.Comment = obDto.Comment
	o.Active = obDto.Active
	o.TextUpdatable = obDto.TextUpdatable
	o.Category = obDto.Category

	return &o
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

// ObligationResponse represents the response format for obligation data.
type ObligationResponse struct {
	Status int             `json:"status" example:"200"`
	Data   []Obligation    `json:"data"`
	Meta   *PaginationMeta `json:"paginationmeta"`
}

// SwaggerObligationResponse represents the response format for obligation data.
type SwaggerObligationResponse struct {
	Status int             `json:"status" example:"200"`
	Data   []ObligationDTO `json:"data"`
	Meta   *PaginationMeta `json:"paginationmeta"`
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

// ObligationId is the id of successfully imported obligation
type ObligationId struct {
	Id    int64  `json:"id" example:"31"`
	Topic string `json:"topic" example:"copyleft"`
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
