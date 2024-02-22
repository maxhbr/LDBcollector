// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/gin-gonic/gin"

	"github.com/gin-gonic/gin/binding"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"
)

// GetAllLicense The get all License function returns all the license data present in the database.
func GetAllLicense(c *gin.Context) {

	var licenses []models.LicenseDB
	query := db.DB.Model(&models.LicenseDB{})

	_ = utils.PreparePaginateResponse(c, query, &models.LicenseResponse{})

	err := query.Find(&licenses).Error
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Licenses not found",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}
	res := models.LicenseResponse{
		Data:   licenses,
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: len(licenses),
		},
	}

	c.JSON(http.StatusOK, res)
}

// FilterLicense Get licenses from service based on different filters.
//
//	@Summary		Filter licenses
//	@Description	Filter licenses based on different parameters
//	@Id				FilterLicense
//	@Tags			Licenses
//	@Accept			json
//	@Produce		json
//	@Param			spdxid			query		string					false	"SPDX ID of the license"
//	@Param			detector_type	query		int						false	"License detector type"
//	@Param			gplv2compatible	query		bool					false	"GPLv2 compatibility flag status of license"
//	@Param			gplv3compatible	query		bool					false	"GPLv3 compatibility flag status of license"
//	@Param			marydone		query		bool					false	"Mary done flag status of license"
//	@Param			active			query		bool					false	"Active license only"
//	@Param			osiapproved		query		bool					false	"OSI Approved flag status of license"
//	@Param			fsffree			query		bool					false	"FSF Free flag status of license"
//	@Param			copyleft		query		bool					false	"Copyleft flag status of license"
//	@Param			page			query		int						false	"Page number"
//	@Param			limit			query		int						false	"Limit of responses per page"
//	@Param			externalRef		query		string					false	"External reference parameters"
//	@Success		200				{object}	models.LicenseResponse	"Filtered licenses"
//	@Failure		400				{object}	models.LicenseError		"Invalid value"
//	@Router			/licenses [get]
func FilterLicense(c *gin.Context) {
	SpdxId := c.Query("spdxid")
	DetectorType := c.Query("detector_type")
	GPLv2compatible := c.Query("gplv2compatible")
	GPLv3compatible := c.Query("gplv3compatible")
	marydone := c.Query("marydone")
	active := c.Query("active")
	OSIapproved := c.Query("osiapproved")
	fsffree := c.Query("fsffree")
	copyleft := c.Query("copyleft")
	externalRef := c.Query("externalRef")

	externalRefData := make(map[string]string)

	if len(externalRef) > 0 {
		err := json.Unmarshal([]byte(externalRef), &externalRefData)
		if err != nil {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "invalid external ref type value",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusBadRequest, er)
			return
		}
	}

	var license []models.LicenseDB
	query := db.DB.Model(&license)

	if SpdxId == "" && GPLv2compatible == "" && GPLv3compatible == "" && DetectorType == "" && marydone == "" && active == "" && fsffree == "" && OSIapproved == "" && copyleft == "" && externalRef == "" {
		GetAllLicense(c)
		return
	}
	if active != "" {
		parsedActive, err := strconv.ParseBool(active)
		if err != nil {
			parsedActive = false
		}
		query = query.Where(models.LicenseDB{Active: parsedActive})
	}

	if fsffree != "" {
		parsedFsffree, err := strconv.ParseBool(fsffree)
		if err != nil {
			parsedFsffree = false
		}
		query = query.Where(models.LicenseDB{FSFfree: parsedFsffree})
	}

	if OSIapproved != "" {
		parsedOsiApproved, err := strconv.ParseBool(OSIapproved)
		if err != nil {
			parsedOsiApproved = false
		}
		query = query.Where(models.LicenseDB{OSIapproved: parsedOsiApproved})
	}

	if copyleft != "" {
		parsedCopyleft, err := strconv.ParseBool(copyleft)
		if err != nil {
			parsedCopyleft = false
		}
		query = query.Where(models.LicenseDB{Copyleft: parsedCopyleft})
	}

	if SpdxId != "" {
		query = query.Where(models.LicenseDB{SpdxId: SpdxId})
	}

	if DetectorType != "" {
		parsedDetectorType, err := strconv.ParseInt(DetectorType, 10, 64)
		if err != nil {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "invalid detector type value",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusBadRequest, er)
			return
		}
		query = query.Where(models.LicenseDB{DetectorType: parsedDetectorType})
	}

	if GPLv2compatible != "" {
		parsedGPLv2compatible, err := strconv.ParseBool(GPLv2compatible)
		if err != nil {
			parsedGPLv2compatible = false
		}
		query = query.Where(models.LicenseDB{GPLv2compatible: parsedGPLv2compatible})
	}

	if GPLv3compatible != "" {
		parsedGPLv3compatible, err := strconv.ParseBool(GPLv3compatible)
		if err != nil {
			parsedGPLv3compatible = false
		}
		query = query.Where(models.LicenseDB{GPLv3compatible: parsedGPLv3compatible})
	}

	if marydone != "" {
		parsedMarydone, err := strconv.ParseBool(marydone)
		if err != nil {
			parsedMarydone = false
		}
		query = query.Where(models.LicenseDB{Marydone: parsedMarydone})
	}

	for externalRefKey, externalRefValue := range externalRefData {
		query = query.Where(fmt.Sprintf("external_ref->>'%s' = ?", externalRefKey), externalRefValue)
	}

	if err := query.Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "incorrect query to search in the database",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	_ = utils.PreparePaginateResponse(c, query, &models.LicenseResponse{})

	query.Find(&license)

	res := models.LicenseResponse{
		Data:   license,
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: len(license),
		},
	}
	c.JSON(http.StatusOK, res)
}

// GetLicense to get a single license by its shortname
//
//	@Summary		Get a license by shortname
//	@Description	Get a single license by its shortname
//	@Id				GetLicense
//	@Tags			Licenses
//	@Accept			json
//	@Produce		json
//	@Param			shortname	path		string	true	"Shortname of the license"
//	@Success		200			{object}	models.LicenseResponse
//	@Failure		404			{object}	models.LicenseError	"License with shortname not found"
//	@Router			/licenses/{shortname} [get]
func GetLicense(c *gin.Context) {
	var license models.LicenseDB

	queryParam := c.Param("shortname")
	if queryParam == "" {
		return
	}

	err := db.DB.Where(models.LicenseDB{Shortname: queryParam}).First(&license).Error

	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("no license with shortname '%s' exists", queryParam),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	res := models.LicenseResponse{
		Data:   []models.LicenseDB{license},
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusOK, res)
}

// CreateLicense creates a new license in the database.
//
//	@Summary		Create a new license
//	@Description	Create a new license in the service
//	@Id				CreateLicense
//	@Tags			Licenses
//	@Accept			json
//	@Produce		json
//	@Param			license	body		models.LicenseInput		true	"New license to be created"
//	@Success		201		{object}	models.LicenseResponse	"New license created successfully"
//	@Failure		400		{object}	models.LicenseError		"Invalid request body"
//	@Failure		409		{object}	models.LicenseError		"License with same shortname already exists"
//	@Failure		500		{object}	models.LicenseError		"Failed to create license"
//	@Security		ApiKeyAuth
//	@Router			/licenses [post]
func CreateLicense(c *gin.Context) {
	var input models.LicenseInput

	if err := c.ShouldBindJSON(&input); err != nil {
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

	license := models.LicenseDB{
		Shortname:       input.Shortname,
		Fullname:        input.Fullname,
		Text:            input.Text,
		Url:             input.Url,
		AddDate:         input.AddDate,
		Copyleft:        input.Copyleft,
		Active:          input.Active,
		FSFfree:         input.FSFfree,
		GPLv2compatible: input.GPLv2compatible,
		GPLv3compatible: input.GPLv3compatible,
		OSIapproved:     input.OSIapproved,
		TextUpdatable:   input.TextUpdatable,
		DetectorType:    input.DetectorType,
		Marydone:        input.Marydone,
		Notes:           input.Notes,
		Fedora:          input.Fedora,
		Flag:            input.Flag,
		Source:          input.Source,
		SpdxId:          input.SpdxId,
		Risk:            input.Risk,
		ExternalRef:     input.ExternalRef,
	}

	result := db.DB.
		Where(&models.LicenseDB{Shortname: license.Shortname}).
		FirstOrCreate(&license)
	if result.RowsAffected == 0 {
		er := models.LicenseError{
			Status:    http.StatusConflict,
			Message:   "can not create license with same shortname",
			Error:     fmt.Sprintf("Error: License with shortname '%s' already exists", input.Shortname),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusConflict, er)
		return
	}
	if result.Error != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Failed to create license",
			Error:     result.Error.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}
	res := models.LicenseResponse{
		Data:   []models.LicenseDB{license},
		Status: http.StatusCreated,
		Meta: &models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusCreated, res)
}

// UpdateLicense Update license with given shortname and create audit and changelog entries.
//
//	@Summary		Update a license
//	@Description	Update a license in the service
//	@Id				UpdateLicense
//	@Tags			Licenses
//	@Accept			json
//	@Produce		json
//	@Param			shortname	path		string					true	"Shortname of the license to be updated"
//	@Param			license		body		models.LicenseUpdate	true	"Update license body (requires only the fields to be updated)"
//	@Success		200			{object}	models.LicenseResponse	"License updated successfully"
//	@Failure		400			{object}	models.LicenseError		"Invalid license body"
//	@Failure		404			{object}	models.LicenseError		"License with shortname not found"
//	@Failure		409			{object}	models.LicenseError		"License with same shortname already exists"
//	@Failure		500			{object}	models.LicenseError		"Failed to update license"
//	@Security		ApiKeyAuth
//	@Router			/licenses/{shortname} [patch]
func UpdateLicense(c *gin.Context) {
	var update models.LicenseUpdate
	var externalRefsPayload models.UpdateExternalRefsJSONPayload
	var license models.LicenseDB
	var oldlicense models.LicenseDB

	username := c.GetString("username")

	shortname := c.Param("shortname")
	if err := db.DB.Where(models.LicenseDB{Shortname: shortname}).First(&license).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("license with shortname '%s' not found", shortname),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}
	oldlicense = license

	// https://github.com/gin-gonic/gin/pull/1341
	if err := c.ShouldBindBodyWith(&update, binding.JSON); err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "invalid json body update",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	if err := c.ShouldBindBodyWith(&externalRefsPayload, binding.JSON); err != nil {
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

	if update.Text != "" && !oldlicense.TextUpdatable && oldlicense.Text != update.Text {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Text is not updatable",
			Error:     "Field `rf_text_updatable` needs to be true to update the text",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}
	if oldlicense.Text != update.Text {
		// Update flag to indicate the license text was updated.
		update.Flag = 2
	}

	// Overwrite values of existing keys, add new key value pairs and remove keys with null values.
	if err := db.DB.Model(&license).UpdateColumn("external_ref", gorm.Expr("jsonb_strip_nulls(external_ref || ?)", externalRefsPayload.ExternalRef)).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Failed to update license",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	// Update all other fields except external_ref
	if err := db.DB.Model(&license).Clauses(clause.Returning{}).Updates(update).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Failed to update license",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	res := models.LicenseResponse{
		Data:   []models.LicenseDB{license},
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	var changes []models.ChangeLog

	if oldlicense.Fullname != license.Fullname {
		changes = append(changes, models.ChangeLog{
			Field:        "Fullname",
			OldValue:     &oldlicense.Fullname,
			UpdatedValue: &license.Fullname,
		})
	}
	if oldlicense.Url != license.Url {
		changes = append(changes, models.ChangeLog{
			Field:        "Url",
			OldValue:     &oldlicense.Url,
			UpdatedValue: &license.Url,
		})
	}
	if oldlicense.AddDate != license.AddDate {
		oldVal := oldlicense.AddDate.Format(time.RFC3339)
		newVal := license.AddDate.Format(time.RFC3339)
		changes = append(changes, models.ChangeLog{
			Field:        "Adddate",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldlicense.Active != license.Active {
		oldVal := strconv.FormatBool(oldlicense.Active)
		newVal := strconv.FormatBool(license.Active)
		changes = append(changes, models.ChangeLog{
			Field:        "Active",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldlicense.Copyleft != license.Copyleft {
		oldVal := strconv.FormatBool(oldlicense.Copyleft)
		newVal := strconv.FormatBool(license.Copyleft)
		changes = append(changes, models.ChangeLog{
			Field:        "Copyleft",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldlicense.FSFfree != license.FSFfree {
		oldVal := strconv.FormatBool(oldlicense.FSFfree)
		newVal := strconv.FormatBool(license.FSFfree)
		changes = append(changes, models.ChangeLog{
			Field:        "FSFfree",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldlicense.GPLv2compatible != license.GPLv2compatible {
		oldVal := strconv.FormatBool(oldlicense.GPLv2compatible)
		newVal := strconv.FormatBool(license.GPLv2compatible)
		changes = append(changes, models.ChangeLog{
			Field:        "GPLv2compatible",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldlicense.GPLv3compatible != license.GPLv3compatible {
		oldVal := strconv.FormatBool(oldlicense.GPLv3compatible)
		newVal := strconv.FormatBool(license.GPLv3compatible)
		changes = append(changes, models.ChangeLog{
			Field:        "GPLv3compatible",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldlicense.OSIapproved != license.OSIapproved {
		oldVal := strconv.FormatBool(oldlicense.OSIapproved)
		newVal := strconv.FormatBool(license.OSIapproved)
		changes = append(changes, models.ChangeLog{
			Field:        "OSIapproved",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldlicense.Text != license.Text {
		changes = append(changes, models.ChangeLog{
			Field:        "Text",
			OldValue:     &oldlicense.Text,
			UpdatedValue: &license.Text,
		})
	}
	if oldlicense.TextUpdatable != license.TextUpdatable {
		oldVal := strconv.FormatBool(oldlicense.TextUpdatable)
		newVal := strconv.FormatBool(license.TextUpdatable)
		changes = append(changes, models.ChangeLog{
			Field:        "TextUpdatable",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldlicense.Fedora != license.Fedora {
		changes = append(changes, models.ChangeLog{
			Field:        "Fedora",
			OldValue:     &oldlicense.Fedora,
			UpdatedValue: &license.Fedora,
		})
	}
	if oldlicense.Flag != license.Flag {
		oldVal := strconv.FormatInt(oldlicense.Flag, 10)
		newVal := strconv.FormatInt(license.Flag, 10)
		changes = append(changes, models.ChangeLog{
			Field:        "Flag",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldlicense.Notes != license.Notes {
		changes = append(changes, models.ChangeLog{
			Field:        "Notes",
			OldValue:     &oldlicense.Notes,
			UpdatedValue: &license.Notes,
		})
	}
	if oldlicense.DetectorType != license.DetectorType {
		oldVal := strconv.FormatInt(oldlicense.DetectorType, 10)
		newVal := strconv.FormatInt(license.DetectorType, 10)
		changes = append(changes, models.ChangeLog{
			Field:        "DetectorType",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldlicense.Source != license.Source {
		changes = append(changes, models.ChangeLog{
			Field:        "Source",
			OldValue:     &oldlicense.Source,
			UpdatedValue: &license.Source,
		})
	}
	if oldlicense.SpdxId != license.SpdxId {
		changes = append(changes, models.ChangeLog{
			Field:        "SpdxId",
			OldValue:     &oldlicense.SpdxId,
			UpdatedValue: &license.SpdxId,
		})
	}
	if oldlicense.Risk != license.Risk {
		oldVal := strconv.FormatInt(oldlicense.Risk, 10)
		newVal := strconv.FormatInt(license.Risk, 10)
		changes = append(changes, models.ChangeLog{
			Field:        "Risk",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldlicense.Marydone != license.Marydone {
		oldVal := strconv.FormatBool(oldlicense.Marydone)
		newVal := strconv.FormatBool(license.Marydone)
		changes = append(changes, models.ChangeLog{
			Field:        "Marydone",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if (oldlicense.ExternalRef.Data().InternalComment == nil && license.ExternalRef.Data().InternalComment != nil) ||
		(oldlicense.ExternalRef.Data().InternalComment != nil && license.ExternalRef.Data().InternalComment == nil) ||
		((oldlicense.ExternalRef.Data().InternalComment != nil && license.ExternalRef.Data().InternalComment != nil) && (*oldlicense.ExternalRef.Data().InternalComment != *license.ExternalRef.Data().InternalComment)) {
		changes = append(changes, models.ChangeLog{
			Field:        "ExternalRef.InternalComment",
			OldValue:     oldlicense.ExternalRef.Data().InternalComment,
			UpdatedValue: license.ExternalRef.Data().InternalComment,
		})
	}
	if (oldlicense.ExternalRef.Data().LicenseExplanation == nil && license.ExternalRef.Data().LicenseExplanation != nil) ||
		(oldlicense.ExternalRef.Data().LicenseExplanation != nil && license.ExternalRef.Data().LicenseExplanation == nil) ||
		((oldlicense.ExternalRef.Data().LicenseExplanation != nil && license.ExternalRef.Data().LicenseExplanation != nil) && (*oldlicense.ExternalRef.Data().LicenseExplanation != *license.ExternalRef.Data().LicenseExplanation)) {
		changes = append(changes, models.ChangeLog{
			Field:        "ExternalRef.LicenseExplanation",
			OldValue:     oldlicense.ExternalRef.Data().LicenseExplanation,
			UpdatedValue: license.ExternalRef.Data().LicenseExplanation,
		})
	}
	if (oldlicense.ExternalRef.Data().LicenseSuffix == nil && license.ExternalRef.Data().LicenseSuffix != nil) ||
		(oldlicense.ExternalRef.Data().LicenseSuffix != nil && license.ExternalRef.Data().LicenseSuffix == nil) ||
		((oldlicense.ExternalRef.Data().LicenseSuffix != nil && license.ExternalRef.Data().LicenseSuffix != nil) && (*oldlicense.ExternalRef.Data().LicenseSuffix != *license.ExternalRef.Data().LicenseSuffix)) {
		changes = append(changes, models.ChangeLog{
			Field:        "ExternalRef.LicenseSuffix",
			OldValue:     oldlicense.ExternalRef.Data().LicenseSuffix,
			UpdatedValue: license.ExternalRef.Data().LicenseSuffix,
		})
	}
	if (oldlicense.ExternalRef.Data().LicenseVersion == nil && license.ExternalRef.Data().LicenseVersion != nil) ||
		(oldlicense.ExternalRef.Data().LicenseVersion != nil && license.ExternalRef.Data().LicenseVersion == nil) ||
		((oldlicense.ExternalRef.Data().LicenseVersion != nil && license.ExternalRef.Data().LicenseVersion != nil) && (*oldlicense.ExternalRef.Data().LicenseVersion != *license.ExternalRef.Data().LicenseVersion)) {
		changes = append(changes, models.ChangeLog{
			Field:        "ExternalRef.LicenseVersion",
			OldValue:     oldlicense.ExternalRef.Data().LicenseVersion,
			UpdatedValue: license.ExternalRef.Data().LicenseVersion,
		})
	}

	if len(changes) != 0 {
		var user models.User
		if err := db.DB.Where(models.User{Username: username}).First(&user).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Failed to update license",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return
		}

		audit := models.Audit{
			UserId:     user.Id,
			TypeId:     license.Id,
			Timestamp:  time.Now(),
			Type:       "license",
			ChangeLogs: changes,
		}

		if err := db.DB.Create(&audit).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Failed to update license",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return
		}
	}

	c.JSON(http.StatusOK, res)
}

// SearchInLicense Search for license data based on user-provided search criteria.
//
//	@Summary		Search licenses
//	@Description	Search licenses on different filters and algorithms
//	@Id				SearchInLicense
//	@Tags			Licenses
//	@Accept			json
//	@Produce		json
//	@Param			search	body		models.SearchLicense	true	"Search criteria"
//	@Success		200		{object}	models.LicenseResponse	"Licenses matched"
//	@Failure		400		{object}	models.LicenseError		"Invalid request"
//	@Failure		404		{object}	models.LicenseError		"Search algorithm doesn't exist"
//	@Router			/search [post]
func SearchInLicense(c *gin.Context) {
	var input models.SearchLicense

	if err := c.ShouldBindJSON(&input); err != nil {
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

	var license []models.LicenseDB
	query := db.DB.Model(&license)

	if input.Search == "fuzzy" {
		query = query.Where(fmt.Sprintf("%s ILIKE ?", input.Field), fmt.Sprintf("%%%s%%", input.SearchTerm))
	} else if input.Search == "" || input.Search == "full_text_search" {
		query = query.Where(input.Field+" @@ plainto_tsquery(?)", input.SearchTerm)
	} else {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   "search algorithm doesn't exist",
			Error:     "search algorithm with such name doesn't exists",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}
	err := query.Find(&license).Error
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Query failed because of error",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	res := models.LicenseResponse{
		Data:   license,
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: len(license),
		},
	}
	c.JSON(http.StatusOK, res)
}
