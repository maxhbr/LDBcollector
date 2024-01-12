// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/gin-gonic/gin"
)

// GetAllLicense The get all License function returns all the license data present in the database.
func GetAllLicense(c *gin.Context) {

	var licenses []models.LicenseDB

	err := db.DB.Find(&licenses).Error
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
		Meta: models.PaginationMeta{
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
	var license []models.LicenseDB
	query := db.DB.Model(&license)

	if SpdxId == "" && GPLv2compatible == "" && GPLv3compatible == "" && DetectorType == "" && marydone == "" && active == "" && fsffree == "" && OSIapproved == "" && copyleft == "" {
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
	query.Find(&license)

	res := models.LicenseResponse{
		Data:   license,
		Status: http.StatusOK,
		Meta: models.PaginationMeta{
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
		Meta: models.PaginationMeta{
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
		Meta: models.PaginationMeta{
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
	if err := c.ShouldBindJSON(&update); err != nil {
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
	if err := db.DB.Model(&license).Updates(update).Error; err != nil {
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
		Meta: models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	var user models.User
	db.DB.Where(models.User{Username: username}).First(&user)
	audit := models.Audit{
		UserId:    user.Id,
		TypeId:    license.Id,
		Timestamp: time.Now(),
		Type:      "license",
	}

	db.DB.Create(&audit)

	if oldlicense.Fullname != license.Fullname {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Fullname",
			OldValue:     oldlicense.Fullname,
			UpdatedValue: license.Fullname,
		}
		db.DB.Create(&change)
	}
	if oldlicense.Url != license.Url {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Url",
			OldValue:     oldlicense.Url,
			UpdatedValue: license.Url,
		}
		db.DB.Create(&change)
	}
	if oldlicense.AddDate != license.AddDate {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Adddate",
			OldValue:     oldlicense.AddDate.Format(time.RFC3339),
			UpdatedValue: license.AddDate.Format(time.RFC3339),
		}
		db.DB.Create(&change)
	}
	if oldlicense.Active != license.Active {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Active",
			OldValue:     strconv.FormatBool(oldlicense.Active),
			UpdatedValue: strconv.FormatBool(license.Active),
		}
		db.DB.Create(&change)
	}
	if oldlicense.Copyleft != license.Copyleft {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Copyleft",
			OldValue:     strconv.FormatBool(oldlicense.Copyleft),
			UpdatedValue: strconv.FormatBool(license.Copyleft),
		}
		db.DB.Create(&change)
	}
	if oldlicense.FSFfree != license.FSFfree {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "FSFfree",
			OldValue:     strconv.FormatBool(oldlicense.FSFfree),
			UpdatedValue: strconv.FormatBool(license.FSFfree),
		}
		db.DB.Create(&change)
	}
	if oldlicense.GPLv2compatible != license.GPLv2compatible {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "GPLv2compatible",
			OldValue:     strconv.FormatBool(oldlicense.GPLv2compatible),
			UpdatedValue: strconv.FormatBool(license.GPLv2compatible),
		}
		db.DB.Create(&change)
	}
	if oldlicense.GPLv3compatible != license.GPLv3compatible {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "GPLv3compatible",
			OldValue:     strconv.FormatBool(oldlicense.GPLv3compatible),
			UpdatedValue: strconv.FormatBool(license.GPLv3compatible),
		}
		db.DB.Create(&change)
	}
	if oldlicense.OSIapproved != license.OSIapproved {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "OSIapproved",
			OldValue:     strconv.FormatBool(oldlicense.OSIapproved),
			UpdatedValue: strconv.FormatBool(license.OSIapproved),
		}
		db.DB.Create(&change)
	}
	if oldlicense.Text != license.Text {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Text",
			OldValue:     oldlicense.Text,
			UpdatedValue: license.Text,
		}
		db.DB.Create(&change)
	}
	if oldlicense.TextUpdatable != license.TextUpdatable {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "TextUpdatable",
			OldValue:     strconv.FormatBool(oldlicense.TextUpdatable),
			UpdatedValue: strconv.FormatBool(license.TextUpdatable),
		}
		db.DB.Create(&change)
	}
	if oldlicense.Fedora != license.Fedora {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Fedora",
			OldValue:     oldlicense.Fedora,
			UpdatedValue: license.Fedora,
		}
		db.DB.Create(&change)
	}
	if oldlicense.Flag != license.Flag {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Flag",
			OldValue:     strconv.FormatInt(oldlicense.Flag, 10),
			UpdatedValue: strconv.FormatInt(license.Flag, 10),
		}
		db.DB.Create(&change)
	}
	if oldlicense.Notes != license.Notes {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Notes",
			OldValue:     oldlicense.Notes,
			UpdatedValue: license.Notes,
		}
		db.DB.Create(&change)
	}
	if oldlicense.DetectorType != license.DetectorType {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "DetectorType",
			OldValue:     strconv.FormatInt(oldlicense.DetectorType, 10),
			UpdatedValue: strconv.FormatInt(license.DetectorType, 10),
		}
		db.DB.Create(&change)
	}
	if oldlicense.Source != license.Source {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Source",
			OldValue:     oldlicense.Source,
			UpdatedValue: license.Source,
		}
		db.DB.Create(&change)
	}
	if oldlicense.SpdxId != license.SpdxId {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "SpdxId",
			OldValue:     oldlicense.SpdxId,
			UpdatedValue: license.SpdxId,
		}
		db.DB.Create(&change)
	}
	if oldlicense.Risk != license.Risk {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Risk",
			OldValue:     strconv.FormatInt(oldlicense.Risk, 10),
			UpdatedValue: strconv.FormatInt(license.Risk, 10),
		}
		db.DB.Create(&change)
	}
	if oldlicense.Marydone != license.Marydone {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Marydone",
			OldValue:     strconv.FormatBool(oldlicense.Marydone),
			UpdatedValue: strconv.FormatBool(license.Marydone),
		}
		db.DB.Create(&change)
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
		Meta: models.PaginationMeta{
			ResourceCount: len(license),
		},
	}
	c.JSON(http.StatusOK, res)
}
