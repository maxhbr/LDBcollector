// SPDX-FileCopyrightText: 2026 Siemens AG
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package models

import "github.com/google/uuid"

// ObligationCategory represents one of the possible of obligation category values
type ObligationCategory struct {
	Id       uuid.UUID `gorm:"type:uuid;primary_key;column:id;default:uuid_generate_v4()" json:"-"`
	Category string    `gorm:"column:category" validate:"required,uppercase" example:"GENERAL" json:"category"`
	Active   *bool     `gorm:"column:active;default:true" json:"-"`
}

func (ObligationCategory) TableName() string {
	return "obligation_categories"
}

// ObligationCategoryResponse represents the response format for obligation category data.
type ObligationCategoryResponse struct {
	Status int                  `json:"status" example:"200"`
	Data   []ObligationCategory `json:"data"`
	Meta   *PaginationMeta      `json:"paginationmeta"`
}
