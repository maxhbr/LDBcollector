// SPDX-FileCopyrightText: 2025 Siemens AG
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package models

import "time"

// OidcClient struct for Database Layer.
type OidcClient struct {
	Id       int64  `gorm:"primary_key;column:id"`
	ClientId string `gorm:"column:client_id"`
	UserId   int64
	User     User      `gorm:"foreignKey:UserId;references:Id"`
	AddDate  time.Time `json:"add_date" gorm:"column:add_date;default:CURRENT_TIMESTAMP" example:"2023-12-01T18:10:25.00+05:30"`
}

func (OidcClient) TableName() string {
	return "oidc_clients"
}

// OidcClient struct for Api Layer(POST, DELETE).
type CreateDeleteOidcClientDTO struct {
	Id       int64     `json:"-"`
	ClientId string    `validate:"required" example:"qwerty"`
	UserId   int64     `json:"-"`
	User     User      `json:"-"`
	AddDate  time.Time `json:"-"`
}

// OidcClient struct for Api Layer(GET).
type OidcClientDTO struct {
	Id       int64     `json:"id" example:"123"`
	ClientId string    `json:"client_id" example:"qwerty"`
	UserId   int64     `json:"-"`
	User     User      `json:"-"`
	AddDate  time.Time `json:"add_date"`
}

// OidcClientsResponse struct is response format for GET request for oidc clients added by an user
type OidcClientsResponse struct {
	Status int             `json:"status" example:"200"`
	Data   []OidcClientDTO `json:"data"`
	Meta   PaginationMeta  `json:"paginationmeta"`
}
