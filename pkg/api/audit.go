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
