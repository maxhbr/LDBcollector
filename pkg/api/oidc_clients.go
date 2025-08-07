// SPDX-FileCopyrightText: 2025 Siemens AG
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"net/http"
	"time"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/gin-gonic/gin"
)

// GetUserOidcClients retrieves a list of all oidc clients added by the user
//
//	@Summary		Get all oidc clients added by the user
//	@Description	Get all oidc clients added by the user for initiating M2M flow with fossology
//	@Id				GetUserOidcClients
//	@Tags			OIDC Clients
//	@Produce		json
//	@Success		200	{object}	models.OidcClientsResponse
//	@Failure		500	{object}	models.LicenseError	"Something went wrong"
//	@Security		ApiKeyAuth
//	@Router			/oidcClients [get]
func GetUserOidcClients(c *gin.Context) {
	var oidcClients []models.OidcClient

	userId := c.MustGet("userId").(int64)

	if err := db.DB.Where(&models.OidcClient{UserId: userId}).Find(&oidcClients).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Unable to fetch oidc clients",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	dtos := make([]models.OidcClientDTO, 0, len(oidcClients))
	for _, c := range oidcClients {
		dtos = append(dtos, models.OidcClientDTO(c))
	}

	res := models.OidcClientsResponse{
		Data:   dtos,
		Status: http.StatusOK,
		Meta: models.PaginationMeta{
			ResourceCount: len(dtos),
		},
	}

	c.JSON(http.StatusOK, res)
}

// AddOidcClient adds a new oidc client.
//
//	@Summary		Adds a new oidc client
//	@Description	Add a new client for initiating M2M flow with fossology
//	@Id				CreateOidcClient
//	@Tags			OIDC Clients
//	@Accept			json
//	@Produce		json
//	@Param			oidc_client	body		models.CreateDeleteOidcClientDTO	true	"Oidc client to add"
//	@Success		201			{object}	models.OidcClientsResponse
//	@Failure		400			{object}	models.LicenseError	"invalid json body"
//	@Failure		409			{object}	models.LicenseError	"oidc client already exists"
//	@Failure		500			{object}	models.LicenseError	"something went wrong while adding new oidc client"
//	@Security		ApiKeyAuth
//	@Router			/oidcClients [post]
func AddOidcClient(c *gin.Context) {
	var oidcClientDto models.CreateDeleteOidcClientDTO
	if err := c.ShouldBindJSON(&oidcClientDto); err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "invalid json body",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	userId := c.MustGet("userId").(int64)

	oidcClient := models.OidcClient(oidcClientDto)
	oidcClient.UserId = userId

	result := db.DB.Where(&models.OidcClient{ClientId: oidcClient.ClientId}).FirstOrCreate(&oidcClient)

	if result.Error != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Unable to create oidc client",
			Error:     result.Error.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	if result.RowsAffected == 0 {
		er := models.LicenseError{
			Status:    http.StatusConflict,
			Message:   "Unable to create oidc client",
			Error:     "Oidc client already exists",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusConflict, er)
		return
	}

	res := models.OidcClientsResponse{
		Data:   []models.OidcClientDTO{models.OidcClientDTO(oidcClient)},
		Status: http.StatusOK,
		Meta: models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusCreated, res)
}

// RevokeClient removes an oidc client
//
//	@Summary		Remove an oidc client
//	@Description	Remove an oidc client if it gets expired or is compromised
//	@Id				RevokeClient
//	@Tags			OIDC Clients
//	@Accept			json
//	@Produce		json
//	@Param			oidc_client	body	models.CreateDeleteOidcClientDTO	true	"Oidc client to add"
//	@Success		204
//	@Failure		404	{object}	models.LicenseError	"Oidc Client not found"
//	@Security		ApiKeyAuth
//	@Router			/oidcClients [delete]
func RevokeClient(c *gin.Context) {
	var deleteOidcClientDto models.CreateDeleteOidcClientDTO
	if err := c.ShouldBindJSON(&deleteOidcClientDto); err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "invalid json body",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	userId := c.MustGet("userId").(int64)

	oidcClient := models.OidcClient(deleteOidcClientDto)
	result := db.DB.Where(&models.OidcClient{ClientId: deleteOidcClientDto.ClientId, UserId: userId}).Delete(&oidcClient)

	if result.Error != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Unable to delete oidc client",
			Error:     result.Error.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	} else if result.RowsAffected == 0 {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   "Unable to delete oidc client",
			Error:     result.Error.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	c.Status(http.StatusNoContent)
}
