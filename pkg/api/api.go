// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"crypto/md5"
	"encoding/hex"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/fossology/LicenseDb/pkg/auth"
	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/gin-gonic/gin"
)

func Router() *gin.Engine {
	// r is a default instance of gin engine
	r := gin.Default()

	// return error for invalid routes
	r.NoRoute(HandleInvalidUrl)

	// authorization not required for these routes
	r.GET("/api/licenses/:shortname", GetLicense)
	r.POST("/api/search", SearchInLicense)
	r.GET("/api/licenses", FilterLicense)

	// set up authentication
	authorized := r.Group("/")
	authorized.Use(auth.AuthenticationMiddleware())

	authorized.POST("/api/licenses", CreateLicense)
	authorized.PATCH("/api/licenses/:shortname", UpdateLicense)
	authorized.POST("/api/users", auth.CreateUser)
	authorized.GET("/api/users", auth.GetAllUser)
	authorized.GET("/api/users/:id", auth.GetUser)

	authorized.GET("/api/audit", GetAllAudit)
	authorized.GET("/api/audit/:audit_id", GetAudit)
	authorized.GET("/api/audit/:audit_id/changes", GetChangeLog)
	authorized.GET("/api/audit/:audit_id/changes/:id", GetChangeLogbyId)

	authorized.POST("/api/obligations", CreateObligation)
	authorized.DELETE("/api/obligations/:topic", DeleteObligation)
	authorized.PATCH("/api/obligations/:topic", UpdateObligation)
	r.GET("/api/obligations", GetAllObligation)
	r.GET("/api/obligations/:topic", GetObligation)

	return r
}

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

func GetLicense(c *gin.Context) {
	var license models.LicenseDB

	queryParam := c.Param("shortname")
	if queryParam == "" {
		return
	}

	err := db.DB.Where("shortname = ?", queryParam).First(&license).Error

	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("no license with shortname '%s' exists", queryParam),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
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

	if input.Active == "" {
		input.Active = "t"
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
			Status:    http.StatusBadRequest,
			Message:   "can not create license with same shortname",
			Error:     fmt.Sprintf("Error: License with shortname '%s' already exists", input.Shortname),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
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

func UpdateLicense(c *gin.Context) {
	var update models.LicenseDB
	var license models.LicenseDB
	var oldlicense models.LicenseDB

	username := c.GetString("username")

	shortname := c.Param("shortname")
	if err := db.DB.Where("shortname = ?", shortname).First(&license).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("license with shortname '%s' not found", shortname),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
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
	db.DB.Where("username = ?", username).First(&user)
	audit := models.Audit{
		UserId:    user.Id,
		TypeId:    license.Id,
		Timestamp: time.Now().Format(time.RFC3339),
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
			OldValue:     oldlicense.AddDate,
			UpdatedValue: license.AddDate,
		}
		db.DB.Create(&change)
	}
	if oldlicense.Active != license.Active {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Active",
			OldValue:     oldlicense.Active,
			UpdatedValue: license.Active,
		}
		db.DB.Create(&change)
	}
	if oldlicense.Copyleft != license.Copyleft {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Copyleft",
			OldValue:     oldlicense.Copyleft,
			UpdatedValue: license.Copyleft,
		}
		db.DB.Create(&change)
	}
	if oldlicense.FSFfree != license.FSFfree {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "FSFfree",
			OldValue:     oldlicense.FSFfree,
			UpdatedValue: license.FSFfree,
		}
		db.DB.Create(&change)
	}
	if oldlicense.GPLv2compatible != license.GPLv2compatible {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "GPLv2compatible",
			OldValue:     oldlicense.GPLv2compatible,
			UpdatedValue: license.GPLv2compatible,
		}
		db.DB.Create(&change)
	}
	if oldlicense.GPLv3compatible != license.GPLv3compatible {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "GPLv3compatible",
			OldValue:     oldlicense.GPLv3compatible,
			UpdatedValue: license.GPLv3compatible,
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
			OldValue:     oldlicense.TextUpdatable,
			UpdatedValue: license.TextUpdatable,
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
			OldValue:     oldlicense.DetectorType,
			UpdatedValue: license.DetectorType,
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
			OldValue:     oldlicense.Risk,
			UpdatedValue: license.Risk,
		}
		db.DB.Create(&change)
	}
	if oldlicense.Marydone != license.Marydone {
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Marydone",
			OldValue:     oldlicense.Marydone,
			UpdatedValue: license.Marydone,
		}
		db.DB.Create(&change)
	}
	c.JSON(http.StatusOK, res)

}

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
		query = query.Where("active=?", active)
	}

	if fsffree != "" {
		query = query.Where("fs_ffree=?", fsffree)
	}

	if OSIapproved != "" {
		query = query.Where("os_iapproved=?", OSIapproved)
	}

	if copyleft != "" {
		query = query.Where("copyleft=?", copyleft)
	}

	if SpdxId != "" {
		query = query.Where("spdx_id=?", SpdxId)
	}

	if DetectorType != "" {
		query = query.Where("detector_type=?", DetectorType)
	}

	if GPLv2compatible != "" {
		query = query.Where("gp_lv2compatible=?", GPLv2compatible)
	}

	if GPLv3compatible != "" {
		query = query.Where("gp_lv3compatible=?", GPLv3compatible)
	}

	if marydone != "" {
		query = query.Where("marydone=?", marydone)
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
			Status:    http.StatusBadRequest,
			Message:   "search algorithm doesn't exist",
			Error:     "search algorithm with such name doesn't exists",
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

func GetAllAudit(c *gin.Context) {
	var audit []models.Audit

	if err := db.DB.Find(&audit).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Change log not found",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
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

func GetAudit(c *gin.Context) {
	var chngelog models.Audit
	id := c.Param("audit_id")

	if err := db.DB.Where("id = ?", id).First(&chngelog).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "no change log with such id exists",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
	}
	res := models.AuditResponse{
		Data:   []models.Audit{chngelog},
		Status: http.StatusOK,
		Meta: models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusOK, res)
}

func GetChangeLog(c *gin.Context) {
	var changelog []models.ChangeLog
	id := c.Param("audit_id")

	if err := db.DB.Where("audit_id = ?", id).Find(&changelog).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "no change log with such id exists",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
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

func GetChangeLogbyId(c *gin.Context) {
	var changelog models.ChangeLog
	auditid := c.Param("audit_id")
	id := c.Param("id")

	if err := db.DB.Where("id = ?", id).Find(&changelog).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "no change history with such id exists",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
	}
	audit_id, _ := strconv.Atoi(auditid)
	if changelog.AuditId != audit_id {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "no change history with such id and audit id exists",
			Error:     "Invalid change history for the requested audit id",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
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
	fmt.Printf(md5hash)
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
	fmt.Print(obligation)

	result := db.DB.Debug().FirstOrCreate(&obligation)

	fmt.Print(obligation)
	if result.RowsAffected == 0 {

		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "can not create obligation with same Md5",
			Error:     fmt.Sprintf("Error: Obligation with Md5 '%s' already exists", obligation.Md5),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
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
		db.DB.Where("shortname = ?", i).Find(&license)
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

func GetAllObligation(c *gin.Context) {
	var obligations []models.Obligation
	query := db.DB.Model(&obligations)
	query = query.Where("active=?", true)
	err := query.Find(&obligations).Error
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Obligations not found",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
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

func UpdateObligation(c *gin.Context) {
	var update models.UpdateObligation
	var oldobligation models.Obligation
	var obligation models.Obligation

	username := c.GetString("username")
	query := db.DB.Model(&obligation)
	query = query.Where("active=?", true)
	tp := c.Param("topic")
	if err := query.Where("topic = ?", tp).First(&obligation).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("obligation with topic '%s' not found", tp),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
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
	db.DB.Where("username = ?", username).First(&user)
	audit := models.Audit{
		UserId:    user.Id,
		TypeId:    obligation.Id,
		Timestamp: time.Now().Format(time.RFC3339),
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
			OldValue:     oldobligation.Modifications,
			UpdatedValue: obligation.Modifications,
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

func DeleteObligation(c *gin.Context) {
	var obligation models.Obligation
	tp := c.Param("topic")
	if err := db.DB.Where("topic= ?", tp).First(&obligation).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("obligation with topic '%s' not found", tp),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}
	obligation.Active = false
}

func GetObligation(c *gin.Context) {
	var obligation models.Obligation
	query := db.DB.Model(&obligation)
	query = query.Where("active=?", true)
	tp := c.Param("topic")
	if err := query.Where("topic= ?", tp).First(&obligation).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("obligation with topic '%s' not found", tp),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
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
