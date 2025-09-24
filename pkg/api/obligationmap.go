// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"fmt"
	"net/http"
	"time"

	"golang.org/x/exp/slices"
	"gorm.io/gorm"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// GetObligationMapByObligationId retrieves obligation maps for a given obligation id
//
//	@Summary		Get maps for an obligation
//	@Description	Get obligation maps for a given obligation id
//	@Id				GetObligationMapByObligationId
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			id	path		string	true	"Id of the obligation"
//	@Success		200	{object}	models.ObligationMapResponse
//	@Failure		404	{object}	models.LicenseError	"No obligation with given id found"
//	@Security		ApiKeyAuth || {}
//	@Router			/obligation_maps/obligation/{id} [get]
func GetObligationMapByObligationId(c *gin.Context) {
	var obligation models.Obligation
	var resObMap models.ObligationMapUser
	var list []models.ObligationMapLicenseFormat

	obligationId, err := uuid.Parse(c.Param("id"))
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("no obligation with id '%s' exists", obligationId.String()),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	if err := db.DB.Joins("Classification").Joins("Type").Preload("Licenses").Where(models.Obligation{Id: obligationId}).First(&obligation).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("obligation with id '%s' not found", obligationId.String()),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	for _, lic := range obligation.Licenses {
		list = append(list, models.ObligationMapLicenseFormat{
			Id:        lic.Id,
			Shortname: *lic.Shortname,
		})
	}

	resObMap = models.ObligationMapUser{
		Id:       obligation.Id,
		Topic:    *obligation.Topic,
		Type:     (*obligation.Type).Type,
		Licenses: list,
	}

	res := models.ObligationMapResponse{
		Data:   []models.ObligationMapUser{resObMap},
		Status: http.StatusOK,
		Meta: models.PaginationMeta{
			ResourceCount: 1,
		},
	}
	c.JSON(http.StatusOK, res)
}

// GetObligationMapByLicenseId retrieves obligation maps for given license id
//
//	@Summary		Get maps for a license
//	@Description	Get obligation maps for a given license id
//	@Id				GetObligationMapByLicenseId
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			license	path		string	true	"id of the license"
//	@Success		200		{object}	models.ObligationMapResponse
//	@Failure		404		{object}	models.LicenseError	"No license with given id found"
//	@Security		ApiKeyAuth || {}
//	@Router			/obligation_maps/license/{id} [get]
func GetObligationMapByLicenseId(c *gin.Context) {
	var license models.LicenseDB
	var resObMapList []models.ObligationMapUser

	licenseId, err := uuid.Parse(c.Param("id"))
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("no license with id '%s' exists", licenseId.String()),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	if err := db.DB.Preload("Obligations").Preload("Obligations.Type").Preload("Obligations.Classification").Where(models.LicenseDB{Id: licenseId}).First(&license).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("no license with id '%s' exists", licenseId.String()),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	for _, ob := range license.Obligations {
		resObMapList = append(resObMapList, models.ObligationMapUser{
			Id:    ob.Id,
			Type:  (*ob.Type).Type,
			Topic: *ob.Topic,
			Licenses: []models.ObligationMapLicenseFormat{
				{
					Id:        license.Id,
					Shortname: *license.Shortname,
				},
			},
		})
	}

	res := models.ObligationMapResponse{
		Data:   resObMapList,
		Status: http.StatusOK,
		Meta: models.PaginationMeta{
			ResourceCount: len(resObMapList),
		},
	}
	c.JSON(http.StatusOK, res)
}

// PatchObligationMap Add or remove licenses from obligation map for a given obligation id
//
//	@Summary		Add or remove licenses from obligation map
//	@Description	Add or remove licenses from obligation map for a given obligation id
//	@Id				PatchObligationMap
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			id				path		string					true	"Id of the obligation"
//	@Param			license_maps	body		models.LicenseMapInput	true	"License ids with action"
//	@Success		200				{object}	models.ObligationMapResponse
//	@Failure		400				{object}	models.LicenseError	"Invalid json body"
//	@Failure		404				{object}	models.LicenseError	"No license or obligation found."
//	@Failure		500				{object}	models.LicenseError	"Failure to insert new maps"
//	@Security		ApiKeyAuth
//	@Router			/obligation_maps/obligations/{id}/license [patch]
func PatchObligationMap(c *gin.Context) {
	var obligation models.Obligation
	var obMapInput models.LicenseMapInput
	var removeLicenses, insertLicenses []uuid.UUID

	obligationId, err := uuid.Parse(c.Param("id"))
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("no obligation with id '%s' exists", obligationId.String()),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	if err := c.ShouldBindJSON(&obMapInput); err != nil {
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

	if err := db.DB.Preload("Licenses").Joins("Type").Where(models.Obligation{Id: obligationId}).First(&obligation).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("obligation with id '%s' not found", obligationId.String()),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	for _, lic := range obMapInput.MapInput {
		if lic.Add {
			found := false
			for _, l := range obligation.Licenses {
				if lic.Id == l.Id {
					found = true
					break
				}
			}
			if !found {
				insertLicenses = append(insertLicenses, lic.Id)
			}
		} else {
			removeLicenses = append(removeLicenses, lic.Id)
		}
	}

	userId := c.MustGet("userId").(uuid.UUID)
	_ = db.DB.Transaction(func(tx *gorm.DB) error {
		newLicenseAssociations, errs := utils.PerformObligationMapActions(tx, userId, &obligation, removeLicenses, insertLicenses)
		if len(errs) != 0 {
			var combinedErrors string
			for _, err := range errs {
				if err != nil {
					combinedErrors += fmt.Sprintf("%s\n", err)
				}
			}
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Unable to add/remove some of the licenses",
				Error:     combinedErrors,
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return nil
		}

		obMap := &models.ObligationMapUser{
			Topic:    *obligation.Topic,
			Type:     (*obligation.Type).Type,
			Licenses: newLicenseAssociations,
		}

		res := models.ObligationMapResponse{
			Data:   []models.ObligationMapUser{*obMap},
			Status: http.StatusOK,
			Meta: models.PaginationMeta{
				ResourceCount: 1,
			},
		}

		c.JSON(http.StatusOK, res)

		return nil
	})
}

// UpdateLicenseInObligationMap Update license list of an obligation map
//
//	@Summary		Change license list
//	@Description	Replaces the license list of an obligation id with the given list in the obligation map.
//	@Id				UpdateLicenseInObligationMap
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			id	path		string					true	"Id of the obligation"
//	@Param			Ids	body		models.LicenseListInput	true	"Ids of the licenses to be in map"
//	@Success		200	{object}	models.ObligationMapResponse
//	@Failure		400	{object}	models.LicenseError	"Invalid json body"
//	@Failure		404	{object}	models.LicenseError	"No license or obligation found."
//	@Security		ApiKeyAuth
//	@Router			/obligation_maps/obligations/{id}/license [put]
func UpdateLicenseInObligationMap(c *gin.Context) {
	var obligation models.Obligation
	var obMapInput models.LicenseListInput
	var removeLicenses, insertLicenses []uuid.UUID

	if err := c.ShouldBindJSON(&obMapInput); err != nil {
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

	obligationId, err := uuid.Parse(c.Param("id"))
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("no obligation with id '%s' exists", obligationId.String()),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	if err := db.DB.Preload("Licenses").Joins("Type").Where(models.Obligation{Id: obligationId}).First(&obligation).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("obligation with id '%s' not found", obligationId.String()),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	obMapInput.LicenseIds = slices.Compact(obMapInput.LicenseIds)

	utils.GenerateDiffForReplacingLicenses(&obligation, obMapInput.LicenseIds, &removeLicenses, &insertLicenses)

	userId := c.MustGet("userId").(uuid.UUID)
	_ = db.DB.Transaction(func(tx *gorm.DB) error {
		newLicenseAssociations, errs := utils.PerformObligationMapActions(tx, userId, &obligation, removeLicenses, insertLicenses)
		if len(errs) != 0 {
			var combinedErrors string
			for _, err := range errs {
				if err != nil {
					combinedErrors += fmt.Sprintf("%s\n", err)
				}
			}
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Unable to add/remove some of the licenses",
				Error:     combinedErrors,
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return nil
		}

		obMap := &models.ObligationMapUser{
			Id:       obligation.Id,
			Topic:    *obligation.Topic,
			Type:     (*obligation.Type).Type,
			Licenses: newLicenseAssociations,
		}

		res := models.ObligationMapResponse{
			Data:   []models.ObligationMapUser{*obMap},
			Status: http.StatusOK,
			Meta: models.PaginationMeta{
				ResourceCount: 1,
			},
		}

		c.JSON(http.StatusOK, res)

		return nil
	})
}
