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

// GetAllObligationClassification retrieves a list of all obligation classifications
//
//	@Summary		Get all active obligation classifications
//	@Description	Get all active obligation classifications from the service
//	@Id				GetAllObligationClassification
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			active	query		bool	true	"Active obligation classification only"
//	@Success		200		{object}	models.ObligationClassificationResponse
//	@Failure		404		{object}	models.LicenseError	"No obligation classifications in DB"
//	@Security		ApiKeyAuth || {}
//	@Router			/obligations/classifications [get]
func GetAllObligationClassification(c *gin.Context) {
	var obligationClassifications []models.ObligationClassification
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

	query := db.DB.Model(&models.ObligationClassification{})
	query.Where("active = ?", parsedActive)
	if err = query.Find(&obligationClassifications).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Unable to fetch obligation classifications",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	res := models.ObligationClassificationResponse{
		Data:   obligationClassifications,
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: len(obligationClassifications),
		},
	}

	c.JSON(http.StatusOK, res)
}

// CreateObligationClassification creates a new obligation classification.
//
//	@Summary		Create an obligation classification
//	@Description	Create an obligation classification
//	@Id				CreateObligationClassification
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			obligation_classification	body		models.ObligationClassification	true	"Obligation classification to create"
//	@Success		201							{object}	models.ObligationClassificationResponse
//	@Failure		400							{object}	models.LicenseError	"invalid json body"
//	@Failure		409							{object}	models.LicenseError	"obligation classification already exists"
//	@Failure		500							{object}	models.LicenseError	"something went wrong while creating new obligation classification"
//	@Security		ApiKeyAuth
//	@Router			/obligations/classifications [post]
func CreateObligationClassification(c *gin.Context) {
	var obClassification models.ObligationClassification
	if err := c.ShouldBindJSON(&obClassification); err != nil {
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
	if err := validate.Struct(&obClassification); err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "can not create obligation classification with these field values",
			Error:     fmt.Sprintf("field '%s' failed validation: %s\n", err.(validator.ValidationErrors)[0].Field(), err.(validator.ValidationErrors)[0].Tag()),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	if err := db.DB.Transaction(func(tx *gorm.DB) error {
		result := tx.Where(&models.ObligationClassification{Classification: obClassification.Classification}).FirstOrCreate(&obClassification)
		if result.Error != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "something went wrong while creating new obligation classification",
				Error:     result.Error.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return result.Error
		}
		if result.RowsAffected == 0 {
			if *obClassification.Active {
				er := models.LicenseError{
					Status:    http.StatusConflict,
					Message:   "obligation classification already exists",
					Error:     "obligation classification already exists",
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				}
				c.JSON(http.StatusConflict, er)
				return errors.New("obligation classification already exists")
			}
			if err := toggleObligationClassificationActiveStatus(c, tx, &obClassification); err != nil {
				er := models.LicenseError{
					Status:    http.StatusConflict,
					Message:   "obligation classification already exists, something went wrong while reactvating it",
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

	res := models.ObligationClassificationResponse{
		Status: http.StatusCreated,
		Data:   []models.ObligationClassification{obClassification},
		Meta: &models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusCreated, res)
}

// DeleteObligationClassification marks an existing obligation classification record as inactive
//
//	@Summary		Deactivate obligation classification
//	@Description	Deactivate an obligation classification
//	@Id				DeleteObligationClassification
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			classification	path	string	true	"Obligation Classification"
//	@Success		200
//	@Failure		400	{object}	models.LicenseError	"cannot delete obligation classification 'GREEN' as it's still referenced by some obligations"
//	@Failure		404	{object}	models.LicenseError	"obligation classification 'GREEN' not found"
//	@Failure		500	{object}	models.LicenseError	"something went wrong while deleting obligation classification"
//	@Security		ApiKeyAuth
//	@Router			/obligations/classifications/{classification} [delete]
func DeleteObligationClassification(c *gin.Context) {
	var obClassification models.ObligationClassification
	obClassificationParam := c.Param("classification")
	if err := db.DB.Where(models.ObligationClassification{Classification: obClassificationParam}).First(&obClassification).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("obligation classification '%s' not found", obClassificationParam),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	if !*obClassification.Active {
		c.Status(http.StatusOK)
		return
	}

	var count int64
	if err := db.DB.Model(&models.Obligation{}).Where(&models.Obligation{ObligationClassificationId: obClassification.Id}).Count(&count).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "something went wrong while deleting obligation classification",
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
			Message:   fmt.Sprintf("cannot delete obligation classification '%s' as it's still referenced by some obligations", obClassification.Classification),
			Error:     fmt.Sprintf("cannot delete obligation classification '%s' as it's still referenced by some obligations", obClassification.Classification),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	if err := db.DB.Transaction(func(tx *gorm.DB) error {
		return toggleObligationClassificationActiveStatus(c, tx, &obClassification)
	}); err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "something went wrong while deleting obligation classification",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
	}
	c.Status(http.StatusOK)
}

func toggleObligationClassificationActiveStatus(c *gin.Context, tx *gorm.DB, obClassification *models.ObligationClassification) error {
	*obClassification.Active = !*obClassification.Active
	if err := tx.Clauses(clause.Returning{}).Updates(&obClassification).Error; err != nil {
		return errors.New("unable to change 'active' status of obligation classification")
	}

	username := c.GetString("username")
	var user models.User
	if err := tx.Where(models.User{UserName: &username}).First(&user).Error; err != nil {
		return errors.New("unable to change 'active' status of obligation classification")
	}

	oldVal := strconv.FormatBool(!*obClassification.Active)
	newVal := strconv.FormatBool(*obClassification.Active)
	change := models.ChangeLog{
		Field:        "Active",
		OldValue:     &oldVal,
		UpdatedValue: &newVal,
	}

	audit := models.Audit{
		UserId:     user.Id,
		TypeId:     obClassification.Id,
		Timestamp:  time.Now(),
		Type:       "ObligationClassification",
		ChangeLogs: []models.ChangeLog{change},
	}

	if err := tx.Create(&audit).Error; err != nil {
		return errors.New("unable to change 'active' status of obligation classification")
	}

	return nil
}
