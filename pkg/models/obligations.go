// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2025 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
// SPDX-FileContributor: 2025 Chayan Das <01chayandas@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package models

import (
	"errors"
	"fmt"
	"strings"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// Obligation represents an obligation record in the database.
type Obligation struct {
	Id                         uuid.UUID                 `gorm:"type:uuid;primary_key;column:id;default:uuid_generate_v4()"`
	Topic                      *string                   `gorm:"column:topic"`
	Text                       *string                   `gorm:"column:text"`
	Comment                    *string                   `gorm:"column:comment;default:''"`
	Active                     *bool                     `gorm:"column:active;default:true"`
	TextUpdatable              *bool                     `gorm:"column:text_updatable;default:false"`
	ObligationClassificationId uuid.UUID                 `gorm:"type:uuid;column:obligation_classification_id"`
	ObligationTypeId           uuid.UUID                 `gorm:"type:uuid;column:obligation_type_id"`
	Licenses                   []LicenseDB               `gorm:"many2many:obligation_licenses; joinForeignKey:obligation_id;joinReferences:license_db_id"`
	Type                       *ObligationType           `gorm:"foreignKey:ObligationTypeId;references:Id"`
	Classification             *ObligationClassification `gorm:"foreignKey:ObligationClassificationId;references:Id"`
	Category                   *string                   `json:"category" gorm:"default:GENERAL" enums:"DISTRIBUTION,PATENT,INTERNAL,CONTRACTUAL,EXPORT_CONTROL,GENERAL" example:"DISTRIBUTION"`
}

func (Obligation) TableName() string {
	return "obligations"
}

var validCategories = []string{"DISTRIBUTION", "PATENT", "INTERNAL", "CONTRACTUAL", "EXPORT_CONTROL", "GENERAL"}

func validateCategory(o *Obligation) error {
	// Check if the provided category is in the list of valid categories. Nil value allowed, will default to GENERAL
	if o.Category == nil {
		return nil
	}
	allCategories := strings.Join(validCategories, ", ")
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
	if o.Topic == nil || (o.Topic != nil && *o.Topic == "") {
		return errors.New("topic cannot be empty")
	}

	if o.Text == nil || (o.Text != nil && *o.Text == "") {
		return errors.New("text cannot be empty")
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
		if o.Type.Id.String() == "" {
			return fmt.Errorf("obligation type must be one of the following values:%s", allTypes)
		}
	} else {
		return errors.New("type cannot be empty")
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
		if o.Classification.Id.String() == "" {
			return fmt.Errorf("obligation classification must be one of the following values:%s", allClassifications)
		}
	} else {
		return errors.New("classification cannot be empty")
	}

	if err := validateCategory(o); err != nil {
		return err
	}

	return nil
}

func (o *Obligation) BeforeUpdate(tx *gorm.DB) (err error) {
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
		if o.Type.Id.String() == "" {
			return fmt.Errorf("obligation type must be one of the following values:%s", allTypes)
		}
	}
	if o.Text != nil && *o.Text == "" {
		return errors.New("text cannot be an empty string")
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
		if o.Classification.Id.String() == "" {
			return fmt.Errorf("obligation classification must be one of the following values:%s", allClassifications)
		}
	}

	if err := validateCategory(o); err != nil {
		return err
	}

	return nil
}

func (o *Obligation) ConvertToObligationResponseDTO() ObligationResponseDTO {
	dto := ObligationResponseDTO{
		Id:             o.Id,
		Topic:          *o.Topic,
		Text:           *o.Text,
		Active:         *o.Active,
		TextUpdatable:  *o.TextUpdatable,
		LicenseIds:     []uuid.UUID{},
		Type:           o.Type.Type,
		Classification: o.Classification.Classification,
		Comment:        o.Comment,
	}

	if o.Category != nil && *o.Category != "" {
		dto.Category = o.Category
	} else {
		category := "GENERAL"
		dto.Category = &category
	}

	for _, lic := range o.Licenses {
		dto.LicenseIds = append(dto.LicenseIds, lic.Id)
	}

	return dto
}

// ObligationResponseDTO represents an obligation json object.
type ObligationResponseDTO struct {
	Id             uuid.UUID   `json:"id" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
	Topic          string      `json:"topic" example:"copyleft" validate:"required"`
	Type           string      `json:"type" example:"RISK" validate:"required"`
	Text           string      `json:"text" example:"Source code be made available when distributing the software." validate:"required"`
	Classification string      `json:"classification" example:"GREEN" validate:"required"`
	Comment        *string     `json:"comment"`
	Active         bool        `json:"active"`
	TextUpdatable  bool        `json:"text_updatable" example:"true"`
	LicenseIds     []uuid.UUID `json:"license_ids" validate:"required" swaggertype:"array,string" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6,f812jfae-7dbc-11d0-a765-00a0hf06bf6"`
	Category       *string     `json:"category" example:"DISTRIBUTION" validate:"required"`
}

// ObligationUpdateDTO represents an obligation json object.
type ObligationUpdateDTO struct {
	Topic          *string      `json:"topic" example:"copyleft"`
	Type           *string      `json:"type" example:"RISK"`
	Text           *string      `json:"text" example:"Source code be made available when distributing the software."`
	Classification *string      `json:"classification" example:"GREEN"`
	Comment        *string      `json:"comment"`
	Active         *bool        `json:"active"`
	LicenseIds     *[]uuid.UUID `json:"license_ids" validate:"required" swaggertype:"array,string" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6,f812jfae-7dbc-11d0-a765-00a0hf06bf6"`
	TextUpdatable  *bool        `json:"text_updatable" example:"true"`
	Category       *string      `json:"category" example:"DISTRIBUTION"`
}

func (obDto *ObligationUpdateDTO) ConvertToObligation() Obligation {
	var o Obligation

	o.Topic = obDto.Topic
	if obDto.Type != nil {
		o.Type = &ObligationType{Type: *obDto.Type}
	}
	o.Text = obDto.Text
	if obDto.Classification != nil {
		o.Classification = &ObligationClassification{Classification: *obDto.Classification}
	}
	o.Comment = obDto.Comment
	o.Active = obDto.Active
	o.TextUpdatable = obDto.TextUpdatable
	o.Category = obDto.Category

	return o
}

// ObligationCreateDTO represents an obligation json object.
type ObligationCreateDTO struct {
	Topic          string      `json:"topic" example:"copyleft" validate:"required"`
	Type           string      `json:"type" example:"RISK" validate:"required"`
	Text           string      `json:"text" example:"Source code be made available when distributing the software." validate:"required"`
	Classification string      `json:"classification" example:"GREEN" validate:"required"`
	Comment        *string     `json:"comment"`
	Active         *bool       `json:"active"`
	TextUpdatable  *bool       `json:"text_updatable" example:"true"`
	LicenseIds     []uuid.UUID `json:"license_ids" validate:"required" swaggertype:"array,string" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6,f812jfae-7dbc-11d0-a765-00a0hf06bf6"`
	Category       *string     `json:"category" example:"DISTRIBUTION"`
}

func (dto *ObligationCreateDTO) ConvertToObligation() Obligation {
	var o Obligation

	o.Topic = &dto.Topic
	o.Text = &dto.Text
	o.Comment = dto.Comment
	o.Active = dto.Active
	o.TextUpdatable = dto.TextUpdatable
	o.Category = dto.Category

	o.Type = &ObligationType{
		Type: dto.Type,
	}

	o.Classification = &ObligationClassification{
		Classification: dto.Classification,
	}

	return o
}

// ObligationFileDTO represents an obligation json object.
type ObligationFileDTO struct {
	Id             *uuid.UUID   `json:"id" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
	Topic          *string      `json:"topic" example:"copyleft"`
	Type           *string      `json:"type" example:"RISK"`
	Text           *string      `json:"text" example:"Source code be made available when distributing the software."`
	Classification *string      `json:"classification" example:"GREEN"`
	Comment        *string      `json:"comment"`
	Active         *bool        `json:"active"`
	LicenseIds     *[]uuid.UUID `json:"license_ids" validate:"required" swaggertype:"array,string" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6,f812jfae-7dbc-11d0-a765-00a0hf06bf6"`
	TextUpdatable  *bool        `json:"text_updatable" example:"true"`
	Category       *string      `json:"category" example:"DISTRIBUTION"`
}

func (obDto *ObligationFileDTO) ConvertToObligation() Obligation {
	var o Obligation

	o.Topic = obDto.Topic
	if obDto.Type != nil {
		o.Type = &ObligationType{Type: *obDto.Type}
	}
	o.Text = obDto.Text
	if obDto.Classification != nil {
		o.Classification = &ObligationClassification{Classification: *obDto.Classification}
	}
	o.Comment = obDto.Comment
	o.Active = obDto.Active
	o.TextUpdatable = obDto.TextUpdatable
	o.Category = obDto.Category

	return o
}

// ObligationPreview is just the Type and Topic of Obligation
type ObligationPreview struct {
	Id    uuid.UUID `json:"id" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
	Topic string    `json:"topic" example:"Provide Copyright Notices"`
	Type  string    `json:"type" enums:"OBLIGATION,RESTRICTION,RISK,RIGHT"`
}

// ObligationResponse represents the response format for obligation data.
type ObligationPreviewResponse struct {
	Status int                 `json:"status" example:"200"`
	Data   []ObligationPreview `json:"data"`
}

// ObligationResponse represents the response format for obligation data.
type ObligationResponse struct {
	Status int                     `json:"status" example:"200"`
	Data   []ObligationResponseDTO `json:"data"`
	Meta   PaginationMeta          `json:"paginationmeta"`
}
