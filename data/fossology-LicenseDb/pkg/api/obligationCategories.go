// SPDX-FileCopyrightText: 2026 Siemens AG
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
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
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/gin-gonic/gin"
	"github.com/go-playground/validator/v10"
	"github.com/google/uuid"
	"gorm.io/gorm"
)

// GetAllObligationCategories retrieves a list of all obligation categories
//
//	@Summary		Get all active obligation categories
//	@Description	Get all active obligation categories from the service
//	@Id				GetAllObligationCategories
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			active	query		bool	true	"Active obligation categories only"
//	@Success		200		{object}	models.ObligationCategoryResponse
//	@Failure		400		{object}	models.LicenseError	"Unable to fetch obligation categories"
//	@Failure		500		{object}	models.LicenseError	"Unable to fetch obligation categories"
//	@Security		ApiKeyAuth || {}
//	@Router			/obligations/categories [get]
func GetAllObligationCategories(c *gin.Context) {
	var obligationCategories []models.ObligationCategory
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

	query := db.DB.Model(&models.ObligationCategory{}).
		Where("active = ?", parsedActive)
	if err = query.Find(&obligationCategories).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Unable to fetch obligation categories",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	res := models.ObligationCategoryResponse{
		Data:   obligationCategories,
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: len(obligationCategories),
		},
	}

	c.JSON(http.StatusOK, res)
}

// CreateObligationCategory creates a new obligation category.
//
//	@Summary		Create an obligation category
//	@Description	Create an obligation category
//	@Id				CreateObligationCategory
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			obligation_category	body		models.ObligationCategory	true	"Obligation category to create"
//	@Success		201					{object}	models.ObligationCategoryResponse
//	@Failure		400					{object}	models.LicenseError	"invalid json body"
//	@Failure		409					{object}	models.LicenseError	"obligation category already exists"
//	@Failure		500					{object}	models.LicenseError	"something went wrong while creating new obligation category"
//	@Security		ApiKeyAuth
//	@Router			/obligations/categories [post]
func CreateObligationCategory(c *gin.Context) {
	var obCategory models.ObligationCategory
	userId := c.MustGet("userId").(uuid.UUID)
	if err := c.ShouldBindJSON(&obCategory); err != nil {
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

	err, status := utils.CreateObCategory(&obCategory, userId)

	switch status {
	case utils.CREATED:
		res := models.ObligationCategoryResponse{
			Status: http.StatusCreated,
			Data:   []models.ObligationCategory{obCategory},
			Meta: &models.PaginationMeta{
				ResourceCount: 1,
			},
		}
		c.JSON(http.StatusCreated, res)

	case utils.CONFLICT:
		er := models.LicenseError{
			Status:    http.StatusConflict,
			Message:   "obligation category already exists",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusConflict, er)

	case utils.CONFLICT_ACTIVATION_FAILED:
		er := models.LicenseError{
			Status:    http.StatusConflict,
			Message:   "obligation category already exists, something went wrong while reactvating it",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusConflict, er)

	case utils.VALIDATION_FAILED:
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "can not create obligation category with these field values",
			Error:     fmt.Sprintf("field '%s' failed validation: %s\n", err.(validator.ValidationErrors)[0].Field(), err.(validator.ValidationErrors)[0].Tag()),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)

	default:
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "something went wrong while creating new obligation category",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)

	}
}

// DeleteObligationCategory marks an existing obligation category record as inactive
//
//	@Summary		Deactivate obligation category
//	@Description	Deactivate an obligation category
//	@Id				DeleteObligationCategory
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			category	path	string	true	"Obligation Category"
//	@Success		200
//	@Failure		400	{object}	models.LicenseError	"cannot delete obligation category 'DISTRIBUTION' as it's still referenced by some obligations"
//	@Failure		404	{object}	models.LicenseError	"obligation category 'DISTRIBUTION' not found"
//	@Failure		500	{object}	models.LicenseError	"something went wrong while deleting obligation category"
//	@Security		ApiKeyAuth
//	@Router			/obligations/categories/{category} [delete]
func DeleteObligationCategory(c *gin.Context) {
	var obCategory models.ObligationCategory
	obCategoryParam := c.Param("category")
	userId := c.MustGet("userId").(uuid.UUID)
	if err := db.DB.Where(models.ObligationCategory{Category: obCategoryParam}).First(&obCategory).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("obligation category '%s' not found", obCategoryParam),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	if !*obCategory.Active {
		c.Status(http.StatusOK)
		return
	}

	var count int64
	if err := db.DB.Model(&models.Obligation{}).Where(&models.Obligation{ObligationCategoryId: obCategory.Id}).Count(&count).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "something went wrong while deleting obligation category",
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
			Message:   fmt.Sprintf("cannot delete obligation category '%s' as it's still referenced by some obligations", obCategory.Category),
			Error:     fmt.Sprintf("cannot delete obligation category '%s' as it's still referenced by some obligations", obCategory.Category),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	if err := db.DB.Transaction(func(tx *gorm.DB) error {
		return utils.ToggleObligationCategoryActiveStatus(userId, tx, &obCategory)
	}); err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "something went wrong while deleting obligation category",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}
	c.Status(http.StatusOK)
}
