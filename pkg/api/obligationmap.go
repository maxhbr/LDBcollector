// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"errors"
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
//	@Security		ApiKeyAuth || {}
//	@Router			/obligation_maps/topic/{topic} [get]
func GetObligationMapByTopic(c *gin.Context) {
	var obligation models.Obligation
	var obMap []models.ObligationMap
	var resObMap models.ObligationMapUser
	var shortnameList []string

	topic := c.Param("topic")

	if err := db.DB.Where(models.Obligation{Topic: topic}).First(&obligation).Error; err != nil {
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

	if err := db.DB.Where(models.ObligationMap{ObligationPk: obligation.Id}).Find(&obMap).Error; err != nil {
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
		if err := db.DB.Where(models.LicenseDB{Id: obMap[i].RfPk}).First(&license).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusNotFound,
				Message:   "Unable to fetch license shortnames",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusNotFound, er)
			return
		}
		shortnameList = append(shortnameList, license.Shortname)
	}

	resObMap = models.ObligationMapUser{
		Topic:      topic,
		Type:       obligation.Type,
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
	var obMap []models.ObligationMap
	var resObMapList []models.ObligationMapUser

	licenseShortName := c.Param("license")

	if err := db.DB.Where(models.LicenseDB{Shortname: licenseShortName}).First(&license).Error; err != nil {
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

	if err := db.DB.Where(models.ObligationMap{RfPk: license.Id}).Find(&obMap).Error; err != nil {
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
		if err := db.DB.Where(models.Obligation{Id: obMap[i].ObligationPk}).First(&obligation).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusNotFound,
				Message:   fmt.Sprintf("Unable to fetch obligations linked with license '%s'", licenseShortName),
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusNotFound, er)
			return
		}
		resObMapList = append(resObMapList, models.ObligationMapUser{
			Type:       obligation.Type,
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

	if err := db.DB.Where(models.Obligation{Topic: topic}).First(&obligation).Error; err != nil {
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
		if err := db.DB.Where(&models.LicenseDB{Shortname: obMapInput.MapInput[i].Shortname}).First(&license).Error; err != nil {
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
		if err := db.DB.Where(&models.ObligationMap{ObligationPk: obligation.Id, RfPk: license.Id}).First(&obligationMap).Error; err != nil {
			// License not in map
			if errors.Is(err, gorm.ErrRecordNotFound) {
				if obMapInput.MapInput[i].Add {
					// Add to insert slice
					insertLicenseIds = append(insertLicenseIds, license.Id)
				}
			} else {
				er := models.LicenseError{
					Status:    http.StatusInternalServerError,
					Message:   fmt.Sprintf("unable to fetch obligation maps for obligation with topic '%s'", obligation.Topic),
					Error:     err.Error(),
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				}
				c.JSON(http.StatusInternalServerError, er)
				return
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

	res, err := PerformObligationMapActions(username, obligation, removeLicenseIds, insertLicenseIds)
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Something went wrong",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
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
	var removeLicenseIds []int64
	var insertLicenseIds []int64

	topic := c.Param("topic")

	if err := db.DB.Where(models.Obligation{Topic: topic}).First(&obligation).Error; err != nil {
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

	username := c.GetString("username")

	if err := GenerateDiffOfLicenses(c, &obligation, obMapInput.Shortnames, &removeLicenseIds, &insertLicenseIds); err != nil {
		return
	}

	res, err := PerformObligationMapActions(username, obligation, removeLicenseIds, insertLicenseIds)
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Something went wrong",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	c.JSON(http.StatusOK, res)
}

// GenerateDiffOfLicenses calculates diff from the obligation maps list in database and the list provided by the user to determine the licenses to be
// inserted and the licenses to be removed. Basically, it replaces the list present in database by the list given by the user.
func GenerateDiffOfLicenses(c *gin.Context, obligation *models.Obligation, inputShortnames []string, removeLicenseIds, insertLicenseIds *[]int64) error {
	var oldObMaps []models.ObligationMap
	if err := db.DB.Where(models.ObligationMap{ObligationPk: obligation.Id}).Find(&oldObMaps).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("obligation maps for obligation with topic '%s' not found", obligation.Topic),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return err
	}

	for i := 0; i < len(oldObMaps); i++ {
		*removeLicenseIds = append(*removeLicenseIds, oldObMaps[i].RfPk)
	}

	for i := 0; i < len(inputShortnames); i++ {
		var license models.LicenseDB
		var obligationMap models.ObligationMap
		if err := db.DB.Where(&models.LicenseDB{Shortname: inputShortnames[i]}).First(&license).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusNotFound,
				Message:   fmt.Sprintf("license with shortname '%s' not found", inputShortnames[i]),
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusNotFound, er)
			return err
		}
		if err := db.DB.Where(&models.ObligationMap{ObligationPk: obligation.Id, RfPk: license.Id}).First(&obligationMap).Error; err != nil {
			// License not in map, add to insert slice
			if errors.Is(err, gorm.ErrRecordNotFound) {
				*insertLicenseIds = append(*insertLicenseIds, license.Id)
			} else {
				er := models.LicenseError{
					Status:    http.StatusInternalServerError,
					Message:   fmt.Sprintf("unable to fetch obligation maps for obligation with topic '%s'", obligation.Topic),
					Error:     err.Error(),
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				}
				c.JSON(http.StatusInternalServerError, er)
				return err
			}
		}
		// License in request, remove from removal slice
		*removeLicenseIds = removeFromSlice(*removeLicenseIds, license.Id)
	}

	return nil
}

// PerformObligationMapActions performs the actions for ObligationMap endpoint PATCH and PUT calls.
// It takes the input of obligation which is being modified, list of licenses to be removed and added,
// and the user making the changes. The function computes the changelog and returns the response.
func PerformObligationMapActions(username string, obligation models.Obligation, removeLicenseIds []int64,
	insertLicenseIds []int64) (*models.ObligationMapResponse, error) {
	var oldObMaps []models.ObligationMap
	var newObMaps []models.ObligationMap
	var removeObMaps []models.ObligationMap
	var insertObMaps []models.ObligationMap

	if err := db.DB.Where(models.ObligationMap{ObligationPk: obligation.Id}).Find(&oldObMaps).Error; err != nil {
		return nil, err
	}

	for i := 0; i < len(removeLicenseIds); i++ {
		deleteItem := models.ObligationMap{
			ObligationPk: obligation.Id,
			RfPk:         removeLicenseIds[i],
		}
		// Find the primary key to make delete faster
		if err := db.DB.Where(&deleteItem).First(&deleteItem).Error; err != nil {
			return nil, err
		}
		removeObMaps = append(removeObMaps, deleteItem)
	}
	for i := 0; i < len(insertLicenseIds); i++ {
		insertObMaps = append(insertObMaps, models.ObligationMap{
			ObligationPk: obligation.Id,
			RfPk:         insertLicenseIds[i],
		})
	}

	if err := db.DB.Transaction(func(tx *gorm.DB) error {
		if len(removeObMaps) > 0 {
			// Bulk delete removeObMaps from DB
			if err := tx.Delete(&removeObMaps).Error; err != nil {
				return err
			}
		}
		if len(insertObMaps) > 0 {
			// Bulk create insertObMaps in DB
			if err := tx.Create(&insertObMaps).Error; err != nil {
				return err
			}
		}

		if err := tx.Where(models.ObligationMap{ObligationPk: obligation.Id}).Find(&newObMaps).Error; err != nil {
			return err
		}

		return createObligationMapChangelog(tx, username, oldObMaps, newObMaps, &obligation)

	}); err != nil {
		return nil, err
	}

	obMap, err := createObligationMapUser(obligation, newObMaps)
	if err != nil {
		return nil, err
	}

	res := models.ObligationMapResponse{
		Data:   []models.ObligationMapUser{*obMap},
		Status: http.StatusOK,
		Meta: models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	return &res, nil
}

// createObligationMapChangelog creates the changelog for the obligation map changes.
func createObligationMapChangelog(tx *gorm.DB, username string, oldObMaps, newObMaps []models.ObligationMap, obligation *models.Obligation) error {
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
		Field:        "RfPk",
		OldValue:     &oldVal,
		UpdatedValue: &newVal,
	}

	var user models.User
	if err := tx.Where(models.User{Username: username}).First(&user).Error; err != nil {
		return err
	}

	audit := models.Audit{
		UserId:     user.Id,
		TypeId:     obligation.Id,
		Timestamp:  time.Now(),
		Type:       "license",
		ChangeLogs: []models.ChangeLog{change},
	}

	if err := tx.Create(&audit).Error; err != nil {
		return err
	}

	return nil
}

// removeFromSlice removes the item from the slice if it exists.
func removeFromSlice[E string | int64](slice []E, item E) []E {
	if slices.Contains(slice, item) {
		return append(slice[:slices.Index(slice, item)], slice[slices.Index(slice, item)+1:]...)
	}
	return slice
}

// createObligationMapUser creates the response data for the obligation map endpoint.
func createObligationMapUser(obligation models.Obligation, obMaps []models.ObligationMap) (*models.ObligationMapUser, error) {
	var shortnameList []string
	for i := 0; i < len(obMaps); i++ {
		var license models.LicenseDB
		if err := db.DB.Where(models.LicenseDB{Id: obMaps[i].RfPk}).First(&license).Error; err != nil {
			return nil, err
		}
		shortnameList = append(shortnameList, license.Shortname)
	}
	return &models.ObligationMapUser{
		Topic:      obligation.Topic,
		Type:       obligation.Type,
		Shortnames: shortnameList,
	}, nil
}
