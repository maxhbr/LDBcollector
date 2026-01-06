// SPDX-FileCopyrightText: 2025 Siemens AG
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package models

import (
	"time"

	"github.com/google/uuid"
)

// OidcClient struct for Database Layer.
type OidcClient struct {
	Id       uuid.UUID `gorm:"primary_key;type:uuid;column:id;default:uuid_generate_v4()"`
	ClientId string    `gorm:"column:client_id"`
	UserId   uuid.UUID
	User     User      `gorm:"foreignKey:UserId;references:Id"`
	AddDate  time.Time `json:"add_date" gorm:"column:add_date;default:CURRENT_TIMESTAMP" example:"2023-12-01T18:10:25.00+05:30"`
}

func (OidcClient) TableName() string {
	return "oidc_clients"
}

// OidcClient struct for Api Layer(POST, DELETE).
type CreateDeleteOidcClientDTO struct {
	Id       uuid.UUID `json:"-"`
	ClientId string    `validate:"required" example:"qwerty"`
	UserId   uuid.UUID `json:"-"`
	User     User      `json:"-"`
	AddDate  time.Time `json:"-"`
}

// OidcClient struct for Api Layer(GET).
type OidcClientDTO struct {
	Id       uuid.UUID `json:"id" example:"f81d4fae-7dec-11d0-a765-00a0c91e6bf6" swaggertype:"string"`
	ClientId string    `json:"client_id" example:"qwerty"`
	UserId   uuid.UUID `json:"-"`
	User     User      `json:"-"`
	AddDate  time.Time `json:"add_date"`
}

// OidcClientsResponse struct is response format for GET request for oidc clients added by an user
type OidcClientsResponse struct {
	Status int             `json:"status" example:"200"`
	Data   []OidcClientDTO `json:"data"`
	Meta   PaginationMeta  `json:"paginationmeta"`
}
