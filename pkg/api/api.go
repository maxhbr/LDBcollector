// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"crypto/md5"
	"encoding/hex"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/gin-gonic/gin"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"

	"github.com/fossology/LicenseDb/pkg/auth"
	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
)

// Router Get the gin router with all the routes defined
//
//	@title						laas (License as a Service) API
//	@version					0.0.9
//	@description				Service to host license information for other services to query over REST API.
//
//	@contact.name				FOSSology
//	@contact.url				https://fossology.org
//	@contact.email				fossology@fossology.org
//
//	@license.name				GPL-2.0-only
//	@license.url				https://github.com/fossology/LicenseDb/blob/main/LICENSE
//
//	@host						localhost:8080
//	@BasePath					/api/v1
//
//	@securityDefinitions.basic	BasicAuth
func Router() *gin.Engine {
	// r is a default instance of gin engine
	r := gin.Default()

	// return error for invalid routes
	r.NoRoute(HandleInvalidUrl)

	// CORS middleware
	r.Use(auth.CORSMiddleware())

	unAuthorizedv1 := r.Group("/api/v1")
	{
		licenses := unAuthorizedv1.Group("/licenses")
		{
			licenses.GET("", FilterLicense)
			licenses.GET(":shortname", GetLicense)
		}
		search := unAuthorizedv1.Group("/search")
		{
			search.POST("", SearchInLicense)
		}
		obligations := unAuthorizedv1.Group("/obligations")
		{
			obligations.GET("", GetAllObligation)
			obligations.GET(":topic", GetObligation)
		}
	}

	authorizedv1 := r.Group("/api/v1")
	authorizedv1.Use(auth.AuthenticationMiddleware())
	{
		licenses := authorizedv1.Group("/licenses")
		{
			licenses.POST("", CreateLicense)
			licenses.PATCH(":shortname", UpdateLicense)
		}
		users := authorizedv1.Group("/users")
		{
			users.GET("", auth.GetAllUser)
			users.GET(":id", auth.GetUser)
			users.POST("", auth.CreateUser)
		}
		audit := authorizedv1.Group("/audits")
		{
			audit.GET("", GetAllAudit)
			audit.GET(":audit_id", GetAudit)
			audit.GET(":audit_id/changes", GetChangeLogs)
			audit.GET(":audit_id/changes/:id", GetChangeLogbyId)
		}
		obligations := authorizedv1.Group("/obligations")
		{
			obligations.POST("", CreateObligation)
			obligations.PATCH(":topic", UpdateObligation)
			obligations.DELETE(":topic", DeleteObligation)
		}
	}

	// Host the swagger UI at /swagger/index.html
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	return r
}

// The HandleInvalidUrl function returns the error when an invalid url is entered
func HandleInvalidUrl(c *gin.Context) {

	er := models.LicenseError{
		Status:    http.StatusNotFound,
		Message:   "No such path exists please check URL",
		Error:     "invalid path",
		Path:      c.Request.URL.Path,
		Timestamp: time.Now().Format(time.RFC3339),
	}
	c.JSON(http.StatusNotFound, er)
}

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
//	@Security		BasicAuth
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

	result := db.DB.FirstOrCreate(&license)
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
//	@Param			license		body		models.LicenseDB		true	"Update license body"
//	@Success		200			{object}	models.LicenseResponse	"License updated successfully"
//	@Failure		400			{object}	models.LicenseError		"Invalid license body"
//	@Failure		404			{object}	models.LicenseError		"License with shortname not found"
//	@Failure		409			{object}	models.LicenseError		"License with same shortname already exists"
//	@Failure		500			{object}	models.LicenseError		"Failed to update license"
//	@Security		BasicAuth
//	@Router			/licenses/{shortname} [patch]
func UpdateLicense(c *gin.Context) {
	var update models.LicenseDB
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

	if oldlicense.Shortname != license.Shortname {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "shortname",
			OldValue:     oldlicense.Shortname,
			UpdatedValue: license.Shortname,
		}
		db.DB.Create(&change)
	}
	if oldlicense.Fullname != license.Fullname {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "fullname",
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
			OldValue:     oldlicense.Shortname,
			UpdatedValue: license.Shortname,
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
			OldValue:     oldlicense.Shortname,
			UpdatedValue: license.Shortname,
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

// GetAllAudit retrieves a list of all audit records from the database
//
//	@Summary		Get audit records
//	@Description	Get all audit records from the server
//	@Id				GetAllAudit
//	@Tags			Audits
//	@Accept			json
//	@Produce		json
//	@Success		200	{object}	models.AuditResponse	"Audit records"
//	@Failure		404	{object}	models.LicenseError		"Not changelogs in DB"
//	@Security		BasicAuth
//	@Router			/audits [get]
func GetAllAudit(c *gin.Context) {
	var audit []models.Audit

	if err := db.DB.Find(&audit).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   "Change log not found",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}
	res := models.AuditResponse{
		Data:   audit,
		Status: http.StatusOK,
		Meta: models.PaginationMeta{
			ResourceCount: len(audit),
		},
	}

	c.JSON(http.StatusOK, res)
}

// GetAudit retrieves a specific audit record by its ID from the database
//
//	@Summary		Get an audit record
//	@Description	Get a specific audit records by ID
//	@Id				GetAudit
//	@Tags			Audits
//	@Accept			json
//	@Produce		json
//	@Param			audit_id	path		string	true	"Audit ID"
//	@Success		200			{object}	models.AuditResponse
//	@Failure		400			{object}	models.LicenseError	"Invalid audit ID"
//	@Failure		404			{object}	models.LicenseError	"No audit entry with given ID"
//	@Security		BasicAuth
//	@Router			/audits/{audit_id} [get]
func GetAudit(c *gin.Context) {
	var changelog models.Audit
	id := c.Param("audit_id")
	parsedId, err := utils.ParseIdToInt(c, id, "audit")
	if err != nil {
		return
	}

	if err := db.DB.Where(models.Audit{Id: parsedId}).First(&changelog).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   "no change log with such id exists",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
	}
	res := models.AuditResponse{
		Data:   []models.Audit{changelog},
		Status: http.StatusOK,
		Meta: models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusOK, res)
}

// GetChangeLogs retrieves a list of change history records associated with a specific audit
//
//	@Summary		Get changelogs
//	@Description	Get changelogs of an audit record
//	@Id				GetChangeLogs
//	@Tags			Audits
//	@Accept			json
//	@Produce		json
//	@Param			audit_id	path		string	true	"Audit ID"
//	@Success		200			{object}	models.ChangeLogResponse
//	@Failure		400			{object}	models.LicenseError	"Invalid audit ID"
//	@Failure		404			{object}	models.LicenseError	"No audit entry with given ID"
//	@Security		BasicAuth
//	@Router			/audits/{audit_id}/changes [get]
func GetChangeLogs(c *gin.Context) {
	var changelog []models.ChangeLog
	id := c.Param("audit_id")
	parsedId, err := utils.ParseIdToInt(c, id, "audit")
	if err != nil {
		return
	}

	if err := db.DB.Where(models.ChangeLog{AuditId: parsedId}).Find(&changelog).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   "no change log with such id exists",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
	}

	res := models.ChangeLogResponse{
		Data:   changelog,
		Status: http.StatusOK,
		Meta: models.PaginationMeta{
			ResourceCount: len(changelog),
		},
	}

	c.JSON(http.StatusOK, res)
}

// GetChangeLogbyId retrieves a specific change history record by its ID for a given audit.
//
//	@Summary		Get a changelog
//	@Description	Get a specific changelog of an audit record by its ID
//	@Id				GetChangeLogbyId
//	@Tags			Audits
//	@Accept			json
//	@Produce		json
//	@Param			audit_id	path		string	true	"Audit ID"
//	@Param			id			path		string	true	"Changelog ID"
//	@Success		200			{object}	models.ChangeLogResponse
//	@Failure		400			{object}	models.LicenseError	"Invalid ID"
//	@Failure		404			{object}	models.LicenseError	"No changelog with given ID found"
//	@Security		BasicAuth
//	@Router			/audits/{audit_id}/changes/{id} [get]
func GetChangeLogbyId(c *gin.Context) {
	var changelog models.ChangeLog
	auditId := c.Param("audit_id")
	parsedAuditId, err := utils.ParseIdToInt(c, auditId, "audit")
	if err != nil {
		return
	}
	changelogId := c.Param("id")
	parsedChangeLogId, err := utils.ParseIdToInt(c, changelogId, "changelog")
	if err != nil {
		return
	}

	if err := db.DB.Where(models.ChangeLog{Id: parsedChangeLogId}).Find(&changelog).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   "no change history with such id exists",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
	}
	if changelog.AuditId != parsedAuditId {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   "no change history with such id and audit id exists",
			Error:     "Invalid change history for the requested audit id",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
	}
	res := models.ChangeLogResponse{
		Data:   []models.ChangeLog{changelog},
		Status: http.StatusOK,
		Meta: models.PaginationMeta{
			ResourceCount: 1,
		},
	}
	c.JSON(http.StatusOK, res)
}

// CreateObligation creates a new obligation record and associates it with relevant licenses.
//
//	@Summary		Create an obligation
//	@Description	Create an obligation and associate it with licenses
//	@Id				CreateObligation
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			obligation	body		models.ObligationInput	true	"Obligation to create"
//	@Success		201			{object}	models.ObligationResponse
//	@Failure		400			{object}	models.LicenseError	"Bad request body"
//	@Failure		409			{object}	models.LicenseError	"Obligation with same body exists"
//	@Failure		500			{object}	models.LicenseError	"Unable to create obligation"
//	@Security		BasicAuth
//	@Router			/obligations [post]
func CreateObligation(c *gin.Context) {
	var input models.ObligationInput

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
	s := input.Text
	hash := md5.Sum([]byte(s))
	md5hash := hex.EncodeToString(hash[:])
	input.Active = true

	input.TextUpdatable = false

	obligation := models.Obligation{
		Md5:            md5hash,
		Type:           input.Type,
		Topic:          input.Topic,
		Text:           input.Text,
		Classification: input.Classification,
		Comment:        input.Comment,
		Modifications:  input.Modifications,
		TextUpdatable:  input.TextUpdatable,
		Active:         input.Active,
	}

	result := db.DB.Debug().FirstOrCreate(&obligation)

	fmt.Print(obligation)
	if result.RowsAffected == 0 {

		er := models.LicenseError{
			Status:    http.StatusConflict,
			Message:   "can not create obligation with same MD5",
			Error:     fmt.Sprintf("Error: Obligation with MD5 '%s' already exists", obligation.Md5),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusConflict, er)
		return
	}
	if result.Error != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Failed to create obligation",
			Error:     result.Error.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}
	for _, i := range input.Shortnames {
		var license models.LicenseDB
		db.DB.Where(models.LicenseDB{Shortname: i}).Find(&license)
		obmap := models.ObligationMap{
			ObligationPk: obligation.Id,
			RfPk:         license.Id,
		}
		db.DB.Create(&obmap)
	}

	res := models.ObligationResponse{
		Data:   []models.Obligation{obligation},
		Status: http.StatusCreated,
		Meta: models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusCreated, res)
}

// GetAllObligation retrieves a list of all active obligation records
//
//	@Summary		Get all active obligations
//	@Description	Get all active obligations from the service
//	@Id				GetAllObligation
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Success		200	{object}	models.ObligationResponse
//	@Failure		404	{object}	models.LicenseError	"No obligations in DB"
//	@Router			/obligations [get]
func GetAllObligation(c *gin.Context) {
	var obligations []models.Obligation
	query := db.DB.Model(&obligations)
	query = query.Where(models.Obligation{Active: true})
	err := query.Find(&obligations).Error
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   "Obligations not found",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}
	res := models.ObligationResponse{
		Data:   obligations,
		Status: http.StatusOK,
		Meta: models.PaginationMeta{
			ResourceCount: len(obligations),
		},
	}

	c.JSON(http.StatusOK, res)
}

// UpdateObligation updates an existing active obligation record
//
//	@Summary		Update obligation
//	@Description	Update an existing obligation record
//	@Id				UpdateObligation
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			topic		path		string					true	"Topic of the obligation to be updated"
//	@Param			obligation	body		models.UpdateObligation	true	"Obligation to be updated"
//	@Success		200			{object}	models.ObligationResponse
//	@Failure		400			{object}	models.LicenseError	"Invalid request"
//	@Failure		404			{object}	models.LicenseError	"No obligation with given topic found"
//	@Failure		500			{object}	models.LicenseError	"Unable to update obligation"
//	@Security		BasicAuth
//	@Router			/obligations/{topic} [patch]
func UpdateObligation(c *gin.Context) {
	var update models.UpdateObligation
	var oldobligation models.Obligation
	var obligation models.Obligation

	username := c.GetString("username")
	query := db.DB.Model(&obligation)
	tp := c.Param("topic")
	if err := query.Where(models.Obligation{Active: true, Topic: tp}).First(&obligation).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("obligation with topic '%s' not found", tp),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}
	oldobligation = obligation
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
	if err := db.DB.Model(&obligation).Updates(update).Error; err != nil {
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

	var user models.User
	db.DB.Where(models.User{Username: username}).First(&user)
	audit := models.Audit{
		UserId:    user.Id,
		TypeId:    obligation.Id,
		Timestamp: time.Now(),
		Type:      "Obligation",
	}
	db.DB.Create(&audit)

	if oldobligation.Topic != obligation.Topic {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Topic",
			OldValue:     oldobligation.Topic,
			UpdatedValue: obligation.Topic,
		}
		db.DB.Create(&change)
	}
	if oldobligation.Type != obligation.Type {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Type",
			OldValue:     oldobligation.Type,
			UpdatedValue: obligation.Type,
		}
		db.DB.Create(&change)
	}
	if oldobligation.Text != obligation.Text {
		if oldobligation.TextUpdatable == true {
			change := models.ChangeLog{
				AuditId:      audit.Id,
				Field:        "Text",
				OldValue:     oldobligation.Text,
				UpdatedValue: obligation.Text,
			}
			db.DB.Create(&change)
		} else {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "Can not update obligation text",
				Error:     "Invalid Request",
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusBadRequest, er)
			return
		}
	}
	if oldobligation.Classification == obligation.Classification {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Classification",
			OldValue:     oldobligation.Classification,
			UpdatedValue: obligation.Classification,
		}
		db.DB.Create(&change)
	}
	if oldobligation.Modifications == obligation.Modifications {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Modification",
			OldValue:     strconv.FormatBool(oldobligation.Modifications),
			UpdatedValue: strconv.FormatBool(obligation.Modifications),
		}
		db.DB.Create(&change)
	}
	if oldobligation.Comment == obligation.Comment {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Comment",
			OldValue:     oldobligation.Comment,
			UpdatedValue: obligation.Comment,
		}
		db.DB.Create(&change)
	}
	if oldobligation.Active == obligation.Active {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Active",
			OldValue:     strconv.FormatBool(oldobligation.Active),
			UpdatedValue: strconv.FormatBool(obligation.Active),
		}
		db.DB.Create(&change)
	}
	if oldobligation.TextUpdatable == obligation.TextUpdatable {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "TextUpdatable",
			OldValue:     strconv.FormatBool(oldobligation.TextUpdatable),
			UpdatedValue: strconv.FormatBool(obligation.TextUpdatable),
		}
		db.DB.Create(&change)
	}
	if oldobligation.Md5 == obligation.Md5 {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Md5",
			OldValue:     oldobligation.Md5,
			UpdatedValue: obligation.Md5,
		}
		db.DB.Create(&change)
	}
	res := models.ObligationResponse{
		Data:   []models.Obligation{obligation},
		Status: http.StatusOK,
		Meta: models.PaginationMeta{
			ResourceCount: 1,
		},
	}
	c.JSON(http.StatusOK, res)
}

// DeleteObligation marks an existing obligation record as inactive
//
//	@Summary		Deactivate obligation
//	@Description	Deactivate an obligation
//	@Id				DeleteObligation
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			topic	path	string	true	"Topic of the obligation to be updated"
//	@Success		204
//	@Failure		404	{object}	models.LicenseError	"No obligation with given topic found"
//	@Security		BasicAuth
//	@Router			/obligations/{topic} [delete]
func DeleteObligation(c *gin.Context) {
	var obligation models.Obligation
	tp := c.Param("topic")
	if err := db.DB.Where(models.Obligation{Topic: tp}).First(&obligation).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("obligation with topic '%s' not found", tp),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}
	obligation.Active = false
	db.DB.Where(models.Obligation{Topic: tp}).Save(&obligation)
	c.Status(http.StatusNoContent)
}

// GetObligation retrieves an active obligation record
//
//	@Summary		Get an obligation
//	@Description	Get an active based on given topic
//	@Id				GetObligation
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			topic	path		string	true	"Topic of the obligation"
//	@Success		200		{object}	models.ObligationResponse
//	@Failure		404		{object}	models.LicenseError	"No obligation with given topic found"
//	@Router			/obligations/{topic} [get]
func GetObligation(c *gin.Context) {
	var obligation models.Obligation
	query := db.DB.Model(&obligation)
	tp := c.Param("topic")
	if err := query.Where(models.Obligation{Active: true, Topic: tp}).First(&obligation).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("obligation with topic '%s' not found", tp),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}
	res := models.ObligationResponse{
		Data:   []models.Obligation{obligation},
		Status: http.StatusOK,
		Meta: models.PaginationMeta{
			ResourceCount: 1,
		},
	}
	c.JSON(http.StatusOK, res)
}
