// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"fmt"
	"net/http"
	"strconv"
	"strings"
	"time"

	"golang.org/x/exp/slices"
	"gorm.io/gorm"

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

	if err := getObligationMapsForObligation(obligation.Id, &obMap).Error; err != nil {
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

func getObligationMapsForObligation(obligationId int64, obMap *[]models.ObligationMap) *gorm.DB {
	return db.DB.Model(&obMap).Where(models.ObligationMap{ObligationPk: obligationId}).Find(&obMap)
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
	var removeLicenseIds []int64
	var insertLicenseIds []int64

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

	for i := 0; i < len(obMapInput.MapInput); i++ {
		var license models.LicenseDB
		var obligationMap models.ObligationMap
		err := db.DB.Model(&license).Where(&models.LicenseDB{Shortname: obMapInput.MapInput[i].Shortname}).First(
			&license).Error
		if err != nil {
			er := models.LicenseError{
				Status:    http.StatusNotFound,
				Message:   fmt.Sprintf("license with shortname '%s' not found", obMapInput.MapInput[i].Shortname),
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusNotFound, er)
			return
		}
		if err := db.DB.Model(&obligationMap).Where(&models.ObligationMap{ObligationPk: obligation.Id,
			RfPk: license.Id}).First(&obligationMap).Error; err != nil {
			// License not in map
			if obMapInput.MapInput[i].Add {
				// Add to insert slice
				insertLicenseIds = append(insertLicenseIds, license.Id)
			}
		} else {
			// License in map
			if !obMapInput.MapInput[i].Add {
				// Add to remove slice
				removeLicenseIds = append(removeLicenseIds, license.Id)
			}
		}
	}

	username := c.GetString("username")

	res := performObligationMapActions(username, obligation, removeLicenseIds, insertLicenseIds)

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
	var oldObMaps []models.ObligationMap
	var removeLicenseIds []int64
	var insertLicenseIds []int64

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

	obMapInput.Shortnames = slices.Compact(obMapInput.Shortnames)

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

	getObligationMapsForObligation(obligation.Id, &oldObMaps)

	for i := 0; i < len(oldObMaps); i++ {
		removeLicenseIds = append(removeLicenseIds, oldObMaps[i].RfPk)
	}

	for i := 0; i < len(obMapInput.Shortnames); i++ {
		var license models.LicenseDB
		var obligationMap models.ObligationMap
		err := db.DB.Model(&license).Where(&models.LicenseDB{Shortname: obMapInput.Shortnames[i]}).First(&license).Error
		if err != nil {
			er := models.LicenseError{
				Status:    http.StatusNotFound,
				Message:   fmt.Sprintf("license with shortname '%s' not found", obMapInput.Shortnames[i]),
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusNotFound, er)
			return
		}
		if err := db.DB.Model(&obligationMap).Where(&models.ObligationMap{ObligationPk: obligation.Id,
			RfPk: license.Id}).First(&obligationMap).Error; err != nil {
			// License not in map, add to insert slice
			insertLicenseIds = append(insertLicenseIds, license.Id)
		}
		// License in request, remove from removal slice
		removeLicenseIds = removeFromSlice(removeLicenseIds, license.Id)
	}

	username := c.GetString("username")

	res := performObligationMapActions(username, obligation, removeLicenseIds, insertLicenseIds)

	c.JSON(http.StatusOK, res)
}

// performObligationMapActions performs the actions for ObligationMap endpoint PATCH and PUT calls.
// It takes the input of obligation which is being modified, list of licenses to be removed and added,
// and the user making the changes. The function computes the changelog and returns the response.
func performObligationMapActions(username string, obligation models.Obligation, removeLicenseIds []int64,
	insertLicenseIds []int64) models.ObligationMapResponse {
	var oldObMaps []models.ObligationMap
	var newObMaps []models.ObligationMap
	var removeObMaps []models.ObligationMap
	var insertObMaps []models.ObligationMap

	getObligationMapsForObligation(obligation.Id, &oldObMaps)

	for i := 0; i < len(removeLicenseIds); i++ {
		deleteItem := models.ObligationMap{
			ObligationPk: obligation.Id,
			RfPk:         removeLicenseIds[i],
		}
		// Find the primary key to make delete faster
		db.DB.Where(&deleteItem).First(&deleteItem)
		removeObMaps = append(removeObMaps, deleteItem)
	}
	for i := 0; i < len(insertLicenseIds); i++ {
		insertObMaps = append(insertObMaps, models.ObligationMap{
			ObligationPk: obligation.Id,
			RfPk:         insertLicenseIds[i],
		})
	}

	if len(removeObMaps) > 0 {
		// Bulk delete removeObMaps from DB
		db.DB.Delete(&removeObMaps)
	}
	if len(insertObMaps) > 0 {
		// Bulk create insertObMaps in DB
		db.DB.Create(&insertObMaps)
	}

	getObligationMapsForObligation(obligation.Id, &newObMaps)

	res := models.ObligationMapResponse{
		Data:   []models.ObligationMapUser{createObligationMapUser(obligation, newObMaps)},
		Status: http.StatusOK,
		Meta: models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	var user models.User
	db.DB.Where(models.User{Username: username}).First(&user)
	audit := models.Audit{
		UserId:    user.Id,
		TypeId:    obligation.Id,
		Timestamp: time.Now(),
		Type:      "obligation_map",
	}

	db.DB.Create(&audit)

	change := createObligationMapChangelog(oldObMaps, newObMaps, audit)
	db.DB.Create(&change)
	return res
}

// createObligationMapChangelog creates the changelog for the obligation map changes.
func createObligationMapChangelog(oldObMaps []models.ObligationMap, newObMaps []models.ObligationMap,
	audit models.Audit) models.ChangeLog {
	var oldLicenses []string
	var newLicenses []string

	for i := 0; i < len(oldObMaps); i++ {
		oldLicenses = append(oldLicenses, strconv.FormatInt(oldObMaps[i].RfPk, 10))
	}
	for i := 0; i < len(newObMaps); i++ {
		newLicenses = append(newLicenses, strconv.FormatInt(newObMaps[i].RfPk, 10))
	}

	oldVal := strings.Join(oldLicenses, ",")
	newVal := strings.Join(newLicenses, ",")
	change := models.ChangeLog{
		AuditId:      audit.Id,
		Field:        "RfPk",
		OldValue:     &oldVal,
		UpdatedValue: &newVal,
	}
	return change
}

// removeFromSlice removes the item from the slice if it exists.
func removeFromSlice[E string | int64](slice []E, item E) []E {
	if slices.Contains(slice, item) {
		return append(slice[:slices.Index(slice, item)], slice[slices.Index(slice, item)+1:]...)
	}
	return slice
}

// createObligationMapUser creates the response data for the obligation map endpoint.
func createObligationMapUser(obligation models.Obligation, obMaps []models.ObligationMap) models.ObligationMapUser {
	var shortnameList []string
	for i := 0; i < len(obMaps); i++ {
		var license models.LicenseDB
		licenseQuery := db.DB.Model(&license)
		licenseQuery.Where(models.LicenseDB{Id: obMaps[i].RfPk}).First(&license)
		shortnameList = append(shortnameList, license.Shortname)
	}
	return models.ObligationMapUser{
		Topic:      obligation.Topic,
		Shortnames: shortnameList,
	}
}
