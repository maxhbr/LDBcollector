// SPDX-FileCopyrightText: 2024 Siemens AG
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"errors"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/gin-gonic/gin"
	"github.com/go-playground/validator/v10"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"
)

// GetAllObligationType retrieves a list of all obligation types
//
//	@Summary		Get all active obligation types
//	@Description	Get all active obligation types from the service
//	@Id				GetAllObligationType
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			active	query		bool	true	"Active obligation type only"
//	@Success		200		{object}	models.ObligationTypeResponse
//	@Failure		404		{object}	models.LicenseError	"No obligation types in DB"
//	@Security		ApiKeyAuth
//	@Router			/obligations/types [get]
func GetAllObligationType(c *gin.Context) {
	var obligationTypes []models.ObligationType
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

	query := db.DB.Model(&models.ObligationType{})
	query.Where("active = ?", parsedActive)
	if err = query.Find(&obligationTypes).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Unable to fetch obligation types",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	res := models.ObligationTypeResponse{
		Data:   obligationTypes,
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: len(obligationTypes),
		},
	}

	c.JSON(http.StatusOK, res)
}

// CreateObligationType creates a new obligation type.
//
//	@Summary		Create an obligation type
//	@Description	Create an obligation type
//	@Id				CreateObligationType
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			obligation_type	body		models.ObligationType	true	"Obligation type to create"
//	@Success		201				{object}	models.ObligationTypeResponse
//	@Failure		400				{object}	models.LicenseError	"invalid json body"
//	@Failure		409				{object}	models.LicenseError	"obligation type already exists"
//	@Failure		500				{object}	models.LicenseError	"something went wrong while creating new obligation type"
//	@Security		ApiKeyAuth
//	@Router			/obligations/types [post]
func CreateObligationType(c *gin.Context) {
	var obType models.ObligationType
	if err := c.ShouldBindJSON(&obType); err != nil {
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

	validate := validator.New(validator.WithRequiredStructEnabled())
	if err := validate.Struct(&obType); err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "can not create obligation type with these field values",
			Error:     fmt.Sprintf("field '%s' failed validation: %s\n", err.(validator.ValidationErrors)[0].Field(), err.(validator.ValidationErrors)[0].Tag()),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	if err := db.DB.Transaction(func(tx *gorm.DB) error {
		result := tx.Where(&models.ObligationType{Type: obType.Type}).FirstOrCreate(&obType)
		if result.Error != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "something went wrong while creating new obligation type",
				Error:     result.Error.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return result.Error
		}
		if result.RowsAffected == 0 {
			if *obType.Active {
				er := models.LicenseError{
					Status:    http.StatusConflict,
					Message:   "obligation type already exists",
					Error:     "obligation type already exists",
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				}
				c.JSON(http.StatusConflict, er)
				return errors.New("obligation type already exists")
			}
			if err := toggleObligationTypeActiveStatus(c, tx, &obType); err != nil {
				er := models.LicenseError{
					Status:    http.StatusConflict,
					Message:   "obligation type already exists, something went wrong while reactvating it",
					Error:     err.Error(),
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				}
				c.JSON(http.StatusConflict, er)
				return err
			}
		}
		return nil
	}); err != nil {
		return
	}

	res := models.ObligationTypeResponse{
		Status: http.StatusCreated,
		Data:   []models.ObligationType{obType},
		Meta: &models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusCreated, res)
}

// DeleteObligationType marks an existing obligation type record as inactive
//
//	@Summary		Deactivate obligation type
//	@Description	Deactivate an obligation type
//	@Id				DeleteObligationType
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			type	path	string	true	"Obligation Type"
//	@Success		200
//	@Failure		400	{object}	models.LicenseError	"cannot delete obligation type 'RISK' as it's still referenced by some obligations"
//	@Failure		404	{object}	models.LicenseError	"obligation type 'RISK' not found"
//	@Failure		500	{object}	models.LicenseError	"something went wrong while deleting obligation type"
//	@Security		ApiKeyAuth
//	@Router			/obligations/types/{type} [delete]
func DeleteObligationType(c *gin.Context) {
	var obType models.ObligationType
	obTypeParam := c.Param("type")
	if err := db.DB.Where(models.ObligationType{Type: obTypeParam}).First(&obType).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("obligation type '%s' not found", obTypeParam),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	if !*obType.Active {
		c.Status(http.StatusOK)
		return
	}

	var count int64
	if err := db.DB.Model(&models.Obligation{}).Where(&models.Obligation{ObligationTypeId: obType.Id}).Count(&count).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "something went wrong while deleting obligation type",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	if count > 0 {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("cannot delete obligation type '%s' as it's still referenced by some obligations", obType.Type),
			Error:     fmt.Sprintf("cannot delete obligation type '%s' as it's still referenced by some obligations", obType.Type),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	if err := db.DB.Transaction(func(tx *gorm.DB) error {
		return toggleObligationTypeActiveStatus(c, tx, &obType)
	}); err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "something went wrong while deleting obligation type",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
	}
	c.Status(http.StatusOK)
}

func toggleObligationTypeActiveStatus(c *gin.Context, tx *gorm.DB, obType *models.ObligationType) error {
	*obType.Active = !*obType.Active
	if err := tx.Clauses(clause.Returning{}).Updates(&obType).Error; err != nil {
		return errors.New("unable to change 'active' status of obligation type")
	}

	username := c.GetString("username")
	var user models.User
	if err := tx.Where(models.User{Username: username}).First(&user).Error; err != nil {
		return errors.New("unable to change 'active' status of obligation type")
	}

	oldVal := strconv.FormatBool(!*obType.Active)
	newVal := strconv.FormatBool(*obType.Active)
	change := models.ChangeLog{
		Field:        "Active",
		OldValue:     &oldVal,
		UpdatedValue: &newVal,
	}

	audit := models.Audit{
		UserId:     user.Id,
		TypeId:     obType.Id,
		Timestamp:  time.Now(),
		Type:       "ObligationType",
		ChangeLogs: []models.ChangeLog{change},
	}

	if err := tx.Create(&audit).Error; err != nil {
		return errors.New("unable to change 'active' status of obligation type")
	}

	return nil
}
