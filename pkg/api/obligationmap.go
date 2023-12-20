// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"fmt"
	"net/http"
	"time"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
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
//	@Router			/obligation_maps/topic/{topic} [get]
func GetObligationMapByTopic(c *gin.Context) {
	var obligation models.Obligation
	var obMap []models.ObligationMap
	var resObMap models.ObligationMapUser
	var shortnameList []string

	topic := c.Param("topic")
	query := db.DB.Model(&obligation)

	if err := query.Where(models.Obligation{Topic: topic}).First(&obligation).Error; err != nil {
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

	query = db.DB.Model(&obMap)

	if err := query.Where(models.ObligationMap{ObligationPk: obligation.Id}).Find(&obMap).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("Obligation map not found for topic '%s'", topic),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	for i := 0; i < len(obMap); i++ {
		var license models.LicenseDB
		licenseQuery := db.DB.Model(&license)
		licenseQuery.Where(models.LicenseDB{Id: obMap[i].RfPk}).First(&license)
		shortnameList = append(shortnameList, license.Shortname)
	}

	resObMap = models.ObligationMapUser{
		Topic:      topic,
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
//	@Router			/obligation_maps/license/{license} [get]
func GetObligationMapByLicense(c *gin.Context) {
	var license models.LicenseDB
	var obMap []models.ObligationMap
	var resObMapList []models.ObligationMapUser

	licenseShortName := c.Param("license")
	query := db.DB.Model(&license)

	if err := query.Where(models.LicenseDB{Shortname: licenseShortName}).First(&license).Error; err != nil {
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

	query = db.DB.Model(&obMap)

	if err := query.Where(models.ObligationMap{RfPk: license.Id}).Find(&obMap).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("Obligation map not found for license '%s'", licenseShortName),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	for i := 0; i < len(obMap); i++ {
		var obligation models.Obligation
		obligationQuery := db.DB.Model(&obligation)
		obligationQuery.Where(models.Obligation{Id: obMap[i].ObligationPk}).First(&obligation)
		resObMapList = append(resObMapList, models.ObligationMapUser{
			Topic:      obligation.Topic,
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
