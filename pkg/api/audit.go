// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"net/http"
	"time"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/gin-gonic/gin"
)

// GetAllAudit retrieves a list of all audit records from the database
//
//	@Summary		Get audit records
//	@Description	Get all audit records from the server
//	@Id				GetAllAudit
//	@Tags			Audits
//	@Accept			json
//	@Produce		json
//	@Param			page	query		int						false	"Page number"
//	@Param			limit	query		int						false	"Number of records per page"
//	@Success		200		{object}	models.AuditResponse	"Audit records"
//	@Failure		404		{object}	models.LicenseError		"Not changelogs in DB"
//	@Security		ApiKeyAuth || {}
//	@Router			/audits [get]
func GetAllAudit(c *gin.Context) {
	var audits []models.Audit

	query := db.DB.Model(&models.Audit{}).Preload("User")

	_ = utils.PreparePaginateResponse(c, query, &models.AuditResponse{})

	if err := query.Order("timestamp desc").Find(&audits).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "unable to fetch audits",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	for i := 0; i < len(audits); i++ {
		if err := utils.GetAuditEntity(c, &audits[i]); err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "unable to find audits",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return
		}
	}
	res := models.AuditResponse{
		Data:   audits,
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: len(audits),
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
//	@Security		ApiKeyAuth || {}
//	@Router			/audits/{audit_id} [get]
func GetAudit(c *gin.Context) {
	var audit models.Audit
	id := c.Param("audit_id")
	parsedId, err := utils.ParseIdToInt(c, id, "audit")
	if err != nil {
		return
	}
	if parsedId == 0 {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Invalid audit ID",
			Error:     "audit ID must be greater than 0",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	if err := db.DB.Preload("User").Where(&models.Audit{Id: parsedId}).First(&audit).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   "no audit with such id exists",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	if err := utils.GetAuditEntity(c, &audit); err != nil {
		return
	}

	res := models.AuditResponse{
		Data:   []models.Audit{audit},
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
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
//	@Failure		500			{object}	models.LicenseError	"unable to find changes"
//	@Security		ApiKeyAuth || {}
//	@Router			/audits/{audit_id}/changes [get]
func GetChangeLogs(c *gin.Context) {
	var changelog []models.ChangeLog
	id := c.Param("audit_id")
	parsedId, err := utils.ParseIdToInt(c, id, "audit")
	if err != nil {
		return
	}
	if parsedId == 0 {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Invalid audit ID",
			Error:     "audit ID must be greater than 0",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	result := db.DB.Where(models.ChangeLog{AuditId: parsedId}).Find(&changelog)
	if result.Error != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "unable to fetch changes",
			Error:     result.Error.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	if result.RowsAffected == 0 {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   "no audit entry with given ID",
			Error:     "No audit entry with given ID",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
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
//	@Security		ApiKeyAuth || {}
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

	if parsedChangeLogId == 0 {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Invalid changelog ID",
			Error:     "changelog ID must be greater than 0",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
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
		return
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
		return
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
