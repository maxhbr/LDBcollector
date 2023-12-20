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

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/gin-gonic/gin"
)

// GetAllObligation retrieves a list of all obligation records
//
//	@Summary		Get all active obligations
//	@Description	Get all active obligations from the service
//	@Id				GetAllObligation
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			active	query		bool	true	"Active obligation only"
//	@Success		200		{object}	models.ObligationResponse
//	@Failure		404		{object}	models.LicenseError	"No obligations in DB"
//	@Router			/obligations [get]
func GetAllObligation(c *gin.Context) {
	var obligations []models.Obligation
	active := c.Query("active")
	if active == "" {
		active = "true"
	}
	var parsedActive bool
	parsedActive, err := strconv.ParseBool(active)
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Invalid active value",
			Error:     fmt.Sprintf("Parsing failed for value '%s'", active),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}
	// FIXME: this query is not filtering
	query := db.DB.Debug().Where(&models.Obligation{Active: parsedActive})
	err = query.Find(&obligations).Error
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

	result := db.DB.FirstOrCreate(&obligation)

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
	if oldobligation.TextUpdatable == false && update.Text != "" && update.Text != oldobligation.Text {
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
		change := models.ChangeLog{
			AuditId:      audit.Id,
			Field:        "Text",
			OldValue:     oldobligation.Text,
			UpdatedValue: obligation.Text,
		}
		db.DB.Create(&change)
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
			Field:        "Modifications",
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
