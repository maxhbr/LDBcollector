// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"crypto/md5"
	"encoding/hex"
	"errors"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"
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
//	@Param			page	query		int		false	"Page number"
//	@Param			limit	query		int		false	"Number of records per page"
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
	query := db.DB.Model(&models.Obligation{})
	query.Where("active = ?", parsedActive)

	_ = utils.PreparePaginateResponse(c, query, &models.ObligationResponse{})

	if err = query.Find(&obligations).Error; err != nil {
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
		Meta: &models.PaginationMeta{
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
	if err := query.Where(models.Obligation{Topic: tp}).First(&obligation).Error; err != nil {
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
		Meta: &models.PaginationMeta{
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
//	@Security		ApiKeyAuth
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

	result := db.DB.
		Where(&models.Obligation{Topic: obligation.Topic}).
		Or(&models.Obligation{Md5: obligation.Md5}).
		FirstOrCreate(&obligation)

	if result.RowsAffected == 0 {
		er := models.LicenseError{
			Status:  http.StatusConflict,
			Message: "can not create obligation with same MD5",
			Error: fmt.Sprintf("Error: Obligation with topic '%s' or MD5 '%s' already exists",
				obligation.Topic, obligation.Md5),
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
		Meta: &models.PaginationMeta{
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
//	@Security		ApiKeyAuth
//	@Router			/obligations/{topic} [patch]
func UpdateObligation(c *gin.Context) {
	db.DB.Transaction(func(tx *gorm.DB) error {
		var update models.UpdateObligation
		var oldobligation models.Obligation
		var obligation models.Obligation

		username := c.GetString("username")
		query := tx.Model(&obligation)
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
			return err
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
			return err
		}
		if !oldobligation.TextUpdatable && update.Text != "" && update.Text != oldobligation.Text {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "Can not update obligation text",
				Error:     "invalid request",
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusBadRequest, er)
			return errors.New("invalid request")
		}

		if err := tx.Model(&obligation).Clauses(clause.Returning{}).Updates(update).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Failed to update license",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return err
		}

		var user models.User
		if err := tx.Where(models.User{Username: username}).First(&user).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Failed to update license",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return err
		}

		audit := models.Audit{
			UserId:    user.Id,
			TypeId:    obligation.Id,
			Timestamp: time.Now(),
			Type:      "Obligation",
		}
		if err := tx.Create(&audit).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Failed to update license",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return err
		}

		var changes []models.ChangeLog

		if oldobligation.Topic != obligation.Topic {
			changes = append(changes, models.ChangeLog{
				AuditId:      audit.Id,
				Field:        "Topic",
				OldValue:     oldobligation.Topic,
				UpdatedValue: obligation.Topic,
			})
		}
		if oldobligation.Type != obligation.Type {
			changes = append(changes, models.ChangeLog{
				AuditId:      audit.Id,
				Field:        "Type",
				OldValue:     oldobligation.Type,
				UpdatedValue: obligation.Type,
			})
		}
		if oldobligation.Text != obligation.Text {
			changes = append(changes, models.ChangeLog{
				AuditId:      audit.Id,
				Field:        "Text",
				OldValue:     oldobligation.Text,
				UpdatedValue: obligation.Text,
			})
		}
		if oldobligation.Classification == obligation.Classification {
			changes = append(changes, models.ChangeLog{
				AuditId:      audit.Id,
				Field:        "Classification",
				OldValue:     oldobligation.Classification,
				UpdatedValue: obligation.Classification,
			})
		}
		if oldobligation.Modifications == obligation.Modifications {
			changes = append(changes, models.ChangeLog{
				AuditId:      audit.Id,
				Field:        "Modifications",
				OldValue:     strconv.FormatBool(oldobligation.Modifications),
				UpdatedValue: strconv.FormatBool(obligation.Modifications),
			})
		}
		if oldobligation.Comment == obligation.Comment {
			changes = append(changes, models.ChangeLog{
				AuditId:      audit.Id,
				Field:        "Comment",
				OldValue:     oldobligation.Comment,
				UpdatedValue: obligation.Comment,
			})
		}
		if oldobligation.Active == obligation.Active {
			changes = append(changes, models.ChangeLog{
				AuditId:      audit.Id,
				Field:        "Active",
				OldValue:     strconv.FormatBool(oldobligation.Active),
				UpdatedValue: strconv.FormatBool(obligation.Active),
			})
		}
		if oldobligation.TextUpdatable == obligation.TextUpdatable {
			changes = append(changes, models.ChangeLog{
				AuditId:      audit.Id,
				Field:        "TextUpdatable",
				OldValue:     strconv.FormatBool(oldobligation.TextUpdatable),
				UpdatedValue: strconv.FormatBool(obligation.TextUpdatable),
			})
		}
		if oldobligation.Md5 == obligation.Md5 {
			changes = append(changes, models.ChangeLog{
				AuditId:      audit.Id,
				Field:        "Md5",
				OldValue:     oldobligation.Md5,
				UpdatedValue: obligation.Md5,
			})
		}

		if err := tx.Create(&changes).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Failed to update license",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return err
		}

		res := models.ObligationResponse{
			Data:   []models.Obligation{obligation},
			Status: http.StatusOK,
			Meta: &models.PaginationMeta{
				ResourceCount: 1,
			},
		}
		c.JSON(http.StatusOK, res)

		return nil
	})
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
//	@Security		ApiKeyAuth
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
