// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2025 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
// SPDX-FileContributor: 2025 Chayan Das <01chayandas@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package models

import (
	"encoding/json"
	"errors"
	"strconv"
	"time"

	"github.com/google/uuid"
	"gorm.io/datatypes"
	"gorm.io/gorm"
)

// The LicenseDB struct represents a license entity with various attributes and properties
// associated with it. It provides structured storage for license-related information.
type LicenseDB struct {
	Id            uuid.UUID                                    `gorm:"primary_key;type:uuid;column:rf_id;default:uuid_generate_v4()"`
	Shortname     *string                                      `gorm:"column:rf_shortname"`
	Fullname      *string                                      `gorm:"column:rf_fullname"`
	Text          *string                                      `gorm:"column:rf_text"`
	Url           *string                                      `gorm:"column:rf_url;default:''"`
	AddDate       time.Time                                    `gorm:"column:rf_add_date"`
	Copyleft      *bool                                        `gorm:"column:rf_copyleft;default:false"`
	OSIapproved   *bool                                        `gorm:"column:rf_osiapproved;default:false"`
	Notes         *string                                      `gorm:"column:rf_notes"`
	TextUpdatable *bool                                        `gorm:"column:rf_text_updatable;default:false"`
	Active        *bool                                        `gorm:"column:rf_active;default:true"`
	Source        *string                                      `gorm:"column:rf_source"`
	SpdxId        *string                                      `gorm:"column:rf_spdx_id"`
	Risk          *int64                                       `gorm:"column:rf_risk"`
	ExternalRef   datatypes.JSONType[LicenseDBSchemaExtension] `gorm:"column:external_ref"`
	Obligations   []Obligation                                 `gorm:"many2many:obligation_licenses;joinForeignKey:license_db_id;joinReferences:obligation_id"`
	User          User                                         `gorm:"foreignKey:UserId;references:Id"`
	UserId        uuid.UUID
}

func (LicenseDB) TableName() string {
	return "license_dbs"
}

func (l *LicenseDB) BeforeCreate(tx *gorm.DB) (err error) {
	if l.Shortname == nil || (l.Shortname != nil && *l.Shortname == "") {
		return errors.New("shortname cannot be empty")
	}

	if l.Fullname == nil || (l.Fullname != nil && *l.Fullname == "") {
		return errors.New("fullname cannot be empty")
	}

	if l.Text == nil || (l.Text != nil && *l.Text == "") {
		return errors.New("text cannot be empty")
	}

	if l.SpdxId == nil || (l.SpdxId != nil && *l.SpdxId == "") {
		return errors.New("spdx_id cannot be empty")
	}

	return nil
}

func (l *LicenseDB) BeforeUpdate(tx *gorm.DB) (err error) {
	if l.Shortname != nil && *l.Shortname == "" {
		return errors.New("shortname cannot be empty")
	}

	if l.Fullname != nil && *l.Fullname == "" {
		return errors.New("fullname cannot be empty")
	}

	if l.Text != nil && *l.Text == "" {
		return errors.New("text cannot be empty")
	}

	if l.SpdxId != nil && *l.SpdxId == "" {
		return errors.New("spdx_id cannot be empty")
	}

	return nil
}

func (l *LicenseDB) ConvertToLicenseResponseDTO() LicenseResponseDTO {
	var response LicenseResponseDTO
	response.Id = l.Id
	response.Shortname = *l.Shortname
	response.Active = *l.Active
	response.AddDate = l.AddDate
	response.Copyleft = *l.Copyleft
	response.ExternalRef = l.ExternalRef.Data()
	response.Fullname = *l.Fullname
	response.Notes = *l.Notes
	response.OSIapproved = *l.OSIapproved
	response.Risk = *l.Risk
	response.Source = *l.Source
	response.SpdxId = *l.SpdxId
	response.Text = *l.Text
	response.TextUpdatable = *l.TextUpdatable
	response.Url = *l.Url
	response.User = l.User

	obligations := []string{}
	for _, o := range l.Obligations {
		obligations = append(obligations, *o.Topic)
	}
	response.Obligations = obligations

	return response
}

// LicenseCreateDTO struct represents the input format for creating a license.
type LicenseCreateDTO struct {
	Shortname     string                   `json:"shortname" validate:"required" example:"MIT"`
	Fullname      string                   `json:"fullname" validate:"required" example:"MIT License"`
	Text          string                   `json:"text" validate:"required" example:"MIT License Text here"`
	Url           *string                  `json:"url" example:"https://opensource.org/licenses/MIT"`
	Copyleft      *bool                    `json:"copyleft" example:"false"`
	OSIapproved   *bool                    `json:"OSIapproved" example:"false"`
	Notes         *string                  `json:"notes" example:"This license has been superseded."`
	TextUpdatable *bool                    `json:"text_updatable" example:"false"`
	Active        *bool                    `json:"active" example:"true"`
	Source        *string                  `json:"source" example:"spdx"`
	SpdxId        string                   `json:"spdx_id" validate:"required,spdxId" example:"MIT"`
	Risk          *int64                   `json:"risk" validate:"min=0,max=5" example:"1"`
	ExternalRef   LicenseDBSchemaExtension `json:"external_ref"`
	Obligations   *[]uuid.UUID             `json:"obligations" swaggertype:"array,string" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6,f812jfae-7dbc-11d0-a765-00a0hf06bf6"`
}

func (dto *LicenseCreateDTO) ConvertToLicenseDB() LicenseDB {
	var l LicenseDB

	l.Shortname = &dto.Shortname
	l.Active = dto.Active
	l.Copyleft = dto.Copyleft
	l.ExternalRef = datatypes.NewJSONType(dto.ExternalRef)
	l.Fullname = &dto.Fullname
	l.Notes = dto.Notes
	l.OSIapproved = dto.OSIapproved
	l.Risk = dto.Risk
	l.Source = dto.Source
	l.SpdxId = &dto.SpdxId
	l.Text = &dto.Text
	l.TextUpdatable = dto.TextUpdatable
	l.Url = dto.Url

	if dto.Obligations != nil {
		obligations := []Obligation{}
		for _, id := range *dto.Obligations {
			obligations = append(obligations, Obligation{Id: id})
		}
		l.Obligations = obligations
	}

	return l
}

// LicenseResponseDTO struct represents the format for returning a license in an api request.
type LicenseResponseDTO struct {
	Id            uuid.UUID                `json:"id" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
	Shortname     string                   `json:"shortname" example:"MIT"`
	Fullname      string                   `json:"fullname" example:"MIT License"`
	Text          string                   `json:"text" example:"MIT License Text here"`
	Url           string                   `json:"url" example:"https://opensource.org/licenses/MIT"`
	Copyleft      bool                     `json:"copyleft"`
	OSIapproved   bool                     `json:"OSIapproved"`
	Notes         string                   `json:"notes" example:"This license has been superseded."`
	TextUpdatable bool                     `json:"text_updatable"`
	Active        bool                     `json:"active"`
	Source        string                   `json:"source"`
	SpdxId        string                   `json:"spdx_id" example:"MIT"`
	Risk          int64                    `json:"risk" example:"1"`
	ExternalRef   LicenseDBSchemaExtension `json:"external_ref"`
	Obligations   []string                 `json:"obligations"`
	User          User                     `json:"created_by"`
	AddDate       time.Time                `json:"add_date"`
}

// LicenseUpdateDTO struct represents the input format for updating an existing license.
type LicenseUpdateDTO struct {
	Shortname     *string                `json:"shortname" example:"MIT"`
	Fullname      *string                `json:"fullname" example:"MIT License"`
	Text          *string                `json:"text" example:"MIT License Text here"`
	Url           *string                `json:"url" example:"https://opensource.org/licenses/MIT"`
	Copyleft      *bool                  `json:"copyleft" example:"false"`
	OSIapproved   *bool                  `json:"OSIapproved" example:"false"`
	Notes         *string                `json:"notes" example:"This license has been superseded."`
	TextUpdatable *bool                  `json:"text_updatable" example:"false"`
	Active        *bool                  `json:"active" example:"true"`
	Source        *string                `json:"source" example:"Source"`
	SpdxId        *string                `json:"spdx_id" example:"MIT" validate:"omitempty,spdxId"`
	Risk          *int64                 `json:"risk" validate:"omitempty,min=0,max=5" example:"1"`
	ExternalRef   map[string]interface{} `json:"external_ref"`
	Obligations   *[]Obligation          `json:"obligations"`
}

func (dto *LicenseUpdateDTO) ConvertToLicenseDB() LicenseDB {
	var l LicenseDB

	l.Shortname = dto.Shortname
	l.Active = dto.Active
	l.Copyleft = dto.Copyleft
	l.Fullname = dto.Fullname
	l.Notes = dto.Notes
	l.OSIapproved = dto.OSIapproved
	l.Risk = dto.Risk
	l.Source = dto.Source
	l.SpdxId = dto.SpdxId
	l.Text = dto.Text
	l.TextUpdatable = dto.TextUpdatable
	l.Url = dto.Url

	return l
}

// LicenseFileDTO struct represents the input format for importing a license.
type LicenseImportDTO struct {
	Id            *uuid.UUID             `json:"id" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
	Shortname     *string                `json:"shortname" validate:"required" example:"MIT"`
	Fullname      *string                `json:"fullname" example:"MIT License"`
	Text          *string                `json:"text" example:"MIT License Text here"`
	Url           *string                `json:"url" example:"https://opensource.org/licenses/MIT"`
	Copyleft      *bool                  `json:"copyleft" example:"false"`
	OSIapproved   *bool                  `json:"OSIapproved" example:"false"`
	Notes         *string                `json:"notes" example:"This license has been superseded."`
	TextUpdatable *bool                  `json:"text_updatable" example:"false"`
	Active        *bool                  `json:"active" example:"true"`
	Source        *string                `json:"source" example:"Source"`
	SpdxId        *string                `json:"spdx_id" example:"MIT" validate:"omitempty,spdxId"`
	Risk          *int64                 `json:"risk" validate:"omitempty,min=0,max=5" example:"1"`
	ExternalRef   map[string]interface{} `json:"external_ref"`
	Obligations   *[]Obligation          `json:"obligations"`
}

func (dto *LicenseImportDTO) ConvertToLicenseDB() LicenseDB {
	var l LicenseDB
	l.Shortname = dto.Shortname
	l.Active = dto.Active
	l.Copyleft = dto.Copyleft
	l.Fullname = dto.Fullname
	l.Notes = dto.Notes
	l.OSIapproved = dto.OSIapproved
	l.Risk = dto.Risk
	l.Source = dto.Source
	l.SpdxId = dto.SpdxId
	l.Text = dto.Text
	l.TextUpdatable = dto.TextUpdatable
	l.Url = dto.Url

	var ext LicenseDBSchemaExtension

	bytes, _ := json.Marshal(dto.ExternalRef)

	if err := json.Unmarshal(bytes, &ext); err != nil {
		panic(err)
	}

	l.ExternalRef = datatypes.NewJSONType(ext)

	return l
}

type LicenseJson struct {
	Shortname      string `json:"rf_shortname"`
	Fullname       string `json:"rf_fullname"`
	Text           string `json:"rf_text"`
	Url            string `json:"rf_url"`
	Copyleft       string `json:"rf_copyleft"`
	OSIapproved    string `json:"rf_OSIapproved"`
	Notes          string `json:"rf_notes"`
	TextUpdatable  string `json:"rf_text_updatable"`
	Active         string `json:"rf_active"`
	Source         string `json:"rf_source"`
	SpdxCompatible string `json:"rf_spdx_compatible"`
	Risk           string `json:"rf_risk"`
	Flag           string `json:"rf_flag"`
}

// The Converter function takes an input of type models.LicenseJson and converts it into a
// corresponding models.LicenseDB object.
// It performs several field assignments and transformations to create the LicenseDB object,
// including generating the SpdxId based on the SpdxCompatible field.
// The resulting LicenseDB object is returned as the output of this function.
func (input *LicenseJson) Converter() LicenseImportDTO {
	spdxCompatible, err := strconv.ParseBool(input.SpdxCompatible)
	if err != nil {
		spdxCompatible = false
	}
	if spdxCompatible {
		input.SpdxCompatible = input.Shortname
	} else {
		input.SpdxCompatible = "LicenseRef-fossology-" + input.Shortname
	}

	copyleft, err := strconv.ParseBool(input.Copyleft)
	if err != nil {
		copyleft = false
	}
	osiApproved, err := strconv.ParseBool(input.OSIapproved)
	if err != nil {
		osiApproved = false
	}
	textUpdatable, err := strconv.ParseBool(input.TextUpdatable)
	if err != nil {
		textUpdatable = false
	}
	active, err := strconv.ParseBool(input.Active)
	if err != nil {
		active = false
	}
	risk, err := strconv.ParseInt(input.Risk, 10, 64)
	if err != nil {
		risk = 0
	}

	result := LicenseImportDTO{
		Shortname:     &input.Shortname,
		Fullname:      &input.Fullname,
		Text:          &input.Text,
		Url:           &input.Url,
		Copyleft:      &copyleft,
		OSIapproved:   &osiApproved,
		Notes:         &input.Notes,
		TextUpdatable: &textUpdatable,
		Active:        &active,
		Source:        &input.Source,
		SpdxId:        &input.SpdxCompatible,
		Risk:          &risk,
	}
	return result
}

type LicensePreview struct {
	Id        uuid.UUID `json:"id" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
	Shortname string    `json:"shortname" example:"GPL-2.0-or-later"`
}

// LicensePreviewResponse gets us the list of all license shortnames
type LicensePreviewResponse struct {
	Status   int              `json:"status" example:"200"`
	Licenses []LicensePreview `json:"licenses"`
}

// LicenseImportStatus is the status of license records successfully inserted in the database during import
type LicenseImportStatus struct {
	Status    int       `json:"status" example:"200"`
	Shortname string    `json:"shortname" example:"MIT"`
	Id        uuid.UUID `json:"id" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
}

// ImportObligationsResponse is the response structure for import obligation response
type ImportLicensesResponse struct {
	Status int           `json:"status" example:"200"`
	Data   []interface{} `json:"data"` // can be of type models.LicenseError or models.LicenseImportStatus
}

// LicenseResponse struct is representation of design API response of license.
// The LicenseResponse struct represents the response data structure for
// retrieving license information.
// It is used to encapsulate license-related data in an organized manner.
type LicenseResponse struct {
	Status int                  `json:"status" example:"200"`
	Data   []LicenseResponseDTO `json:"data"`
	Meta   *PaginationMeta      `json:"paginationmeta"`
}

type UpdateExternalRefsJSONPayload struct {
	ExternalRef map[string]interface{} `json:"external_ref"`
}
