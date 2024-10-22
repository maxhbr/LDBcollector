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

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/gin-gonic/gin"
)

// GetObligationMapByTopic retrieves obligation maps for a given obligation topic
//
//	@Summary		Get maps for an obligation
//	@Description	Get obligation maps for a given obligation topic
//	@Id				GetObligationMapByTopic
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			topic	path		string	true	"Topic of the obligation"
//	@Success		200		{object}	models.ObligationMapResponse
//	@Failure		404		{object}	models.LicenseError	"No obligation with given topic found or no map for
//	obligation exists"
//	@Security		ApiKeyAuth || {}
//	@Router			/obligation_maps/topic/{topic} [get]
func GetObligationMapByTopic(c *gin.Context) {
	var obligation models.Obligation
	var resObMap models.ObligationMapUser
	var shortnameList []string

	topic := c.Param("topic")

	if err := db.DB.Joins("Classification").Joins("Type").Preload("Licenses").Where(models.Obligation{Topic: &topic}).First(&obligation).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("obligation with topic '%s' not found", topic),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	for _, lic := range obligation.Licenses {
		shortnameList = append(shortnameList, *lic.Shortname)
	}

	resObMap = models.ObligationMapUser{
		Topic:      topic,
		Type:       (*obligation.Type).Type,
		Shortnames: shortnameList,
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

// GetObligationMapByLicense retrieves obligation maps for given license shortname
//
//	@Summary		Get maps for a license
//	@Description	Get obligation maps for a given license shortname
//	@Id				GetObligationMapByLicense
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			license	path		string	true	"Shortname of the license"
//	@Success		200		{object}	models.ObligationMapResponse
//	@Failure		404		{object}	models.LicenseError	"No license with given shortname found or no map for
//	license exists"
//	@Security		ApiKeyAuth || {}
//	@Router			/obligation_maps/license/{license} [get]
func GetObligationMapByLicense(c *gin.Context) {
	var license models.LicenseDB
	var resObMapList []models.ObligationMapUser

	licenseShortName := c.Param("license")

	if err := db.DB.Preload("Obligations").Preload("Obligations.Type").Preload("Obligations.Classification").Where(models.LicenseDB{Shortname: &licenseShortName}).First(&license).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("license with shortname '%s' not found", licenseShortName),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	for _, ob := range license.Obligations {
		resObMapList = append(resObMapList, models.ObligationMapUser{
			Type:       (*ob.Type).Type,
			Topic:      *ob.Topic,
			Shortnames: []string{licenseShortName},
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

// PatchObligationMap Add or remove licenses from obligation map for a given obligation topic
//
//	@Summary		Add or remove licenses from obligation map
//	@Description	Add or remove licenses from obligation map for a given obligation topic
//	@Id				PatchObligationMap
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			topic		path		string								true	"Topic of the obligation"
//	@Param			shortname	body		models.LicenseMapShortnamesInput	true	"Shortnames of the licenses with action"
//	@Success		200			{object}	models.ObligationMapResponse
//	@Failure		400			{object}	models.LicenseError	"Invalid json body"
//	@Failure		404			{object}	models.LicenseError	"No license or obligation found."
//	@Failure		500			{object}	models.LicenseError	"Failure to insert new maps"
//	@Security		ApiKeyAuth
//	@Router			/obligation_maps/topic/{topic}/license [patch]
func PatchObligationMap(c *gin.Context) {
	var obligation models.Obligation
	var obMapInput models.LicenseMapShortnamesInput
	var removeLicenses, insertLicenses []string

	topic := c.Param("topic")

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

	if err := db.DB.Preload("Licenses").Joins("Type").Where(models.Obligation{Topic: &topic}).First(&obligation).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("obligation with topic '%s' not found", topic),
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
				if lic.Shortname == *l.Shortname {
					found = true
					break
				}
			}
			if !found {
				insertLicenses = append(insertLicenses, lic.Shortname)
			}
		} else {
			removeLicenses = append(removeLicenses, lic.Shortname)
		}
	}

	username := c.GetString("username")
	newLicenseAssociations, errs := utils.PerformObligationMapActions(username, &obligation, removeLicenses, insertLicenses)
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
		return
	}

	obMap := &models.ObligationMapUser{
		Topic:      *obligation.Topic,
		Type:       (*obligation.Type).Type,
		Shortnames: newLicenseAssociations,
	}

	res := models.ObligationMapResponse{
		Data:   []models.ObligationMapUser{*obMap},
		Status: http.StatusOK,
		Meta: models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusOK, res)
}

// UpdateLicenseInObligationMap Update license list of an obligation map
//
//	@Summary		Change license list
//	@Description	Replaces the license list of an obligation topic with the given list in the obligation map.
//	@Id				UpdateLicenseInObligationMap
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			topic		path		string							true	"Topic of the obligation"
//	@Param			shortnames	body		models.LicenseShortnamesInput	true	"Shortnames of the licenses to be in map"
//	@Success		200			{object}	models.ObligationMapResponse
//	@Failure		400			{object}	models.LicenseError	"Invalid json body"
//	@Failure		404			{object}	models.LicenseError	"No license or obligation found."
//	@Security		ApiKeyAuth
//	@Router			/obligation_maps/topic/{topic}/license [put]
func UpdateLicenseInObligationMap(c *gin.Context) {
	var obligation models.Obligation
	var obMapInput models.LicenseShortnamesInput
	var removeLicenses, insertLicenses []string

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

	topic := c.Param("topic")
	if err := db.DB.Preload("Licenses").Joins("Type").Where(models.Obligation{Topic: &topic}).First(&obligation).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("obligation with topic '%s' not found", topic),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	obMapInput.Shortnames = slices.Compact(obMapInput.Shortnames)

	utils.GenerateDiffForReplacingLicenses(&obligation, obMapInput.Shortnames, &removeLicenses, &insertLicenses)

	username := c.GetString("username")
	newLicenseAssociations, errs := utils.PerformObligationMapActions(username, &obligation, removeLicenses, insertLicenses)
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
		return
	}

	obMap := &models.ObligationMapUser{
		Topic:      *obligation.Topic,
		Type:       (*obligation.Type).Type,
		Shortnames: newLicenseAssociations,
	}

	res := models.ObligationMapResponse{
		Data:   []models.ObligationMapUser{*obMap},
		Status: http.StatusOK,
		Meta: models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusOK, res)
}
