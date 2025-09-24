// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
// SPDX-FileContributor: 2025 Chayan Das <01chayandas@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"encoding/json"
	"fmt"
	"net/http"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"golang.org/x/exp/slices"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
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
//	@Param			active		query		bool	true	"Active obligation only"
//	@Param			page		query		int		false	"Page number"
//	@Param			limit		query		int		false	"Number of records per page"
//	@Param			order_by	query		string	false	"Asc or desc ordering"	Enums(asc, desc)	default(asc)
//	@Success		200			{object}	models.ObligationResponse
//	@Failure		400			{object}	models.LicenseError	"Invalid active value"
//	@Failure		500			{object}	models.LicenseError	"Internal server error"
//	@Security		ApiKeyAuth || {}
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
	query.Where(&models.Obligation{Active: &parsedActive})

	_ = utils.PreparePaginateResponse(c, query, &models.ObligationResponse{})

	orderBy := c.Query("order_by")
	queryOrderString := "topic"

	if orderBy != "" && orderBy == "desc" {
		queryOrderString += " desc"
	}

	query.Order(queryOrderString)

	if err = query.Joins("Type").Joins("Classification").Preload("Licenses").Find(&obligations).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Unable to fetch obligations",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	var obligationDtos []models.ObligationResponseDTO

	for _, o := range obligations {
		obDto := o.ConvertToObligationResponseDTO()
		obligationDtos = append(obligationDtos, obDto)
	}

	res := models.ObligationResponse{
		Data:   obligationDtos,
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
//	@Description	Get an active based on given id
//	@Id				GetObligation
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			id	path		string	true	"Id of the obligation"
//	@Success		200	{object}	models.ObligationResponse
//	@Failure		404	{object}	models.LicenseError	"No obligation with given id found"
//	@Security		ApiKeyAuth || {}
//	@Router			/obligations/{id} [get]
func GetObligation(c *gin.Context) {
	var obligation models.Obligation
	query := db.DB.Model(&obligation)

	obligationId, err := uuid.Parse(c.Param("id"))
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("no obligation with id '%s' exists", obligationId.String()),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	if err := query.Joins("Type").Joins("Classification").Preload("Licenses").Where(models.Obligation{Id: obligationId}).First(&obligation).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("obligation with id '%s' not found", obligationId.String()),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	obDto := obligation.ConvertToObligationResponseDTO()

	res := models.ObligationResponse{
		Data:   []models.ObligationResponseDTO{obDto},
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
//	@Param			obligation	body		models.ObligationCreateDTO	true	"Obligation to create"
//	@Success		201			{object}	models.ObligationResponse
//	@Failure		400			{object}	models.LicenseError	"Bad request body"
//	@Failure		500			{object}	models.LicenseError	"Unable to create obligation"
//	@Security		ApiKeyAuth
//	@Router			/obligations [post]
func CreateObligation(c *gin.Context) {
	var obligation models.ObligationCreateDTO
	userId := c.MustGet("userId").(uuid.UUID)

	if err := c.ShouldBindJSON(&obligation); err != nil {
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

	_ = db.DB.Transaction(func(tx *gorm.DB) error {
		ob := obligation.ConvertToObligation()
		result := tx.Omit("Licenses").Create(&ob)

		if result.Error != nil {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "Failed to create obligation",
				Error:     result.Error.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusBadRequest, er)
			return result.Error
		}

		if err := addChangelogsForObligation(tx, userId, &ob, &models.Obligation{}); err != nil {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "Failed to create obligation",
				Error:     result.Error.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusBadRequest, er)
			return err
		}

		var combinedMapErrors string
		var removeLicenses, insertLicenses []uuid.UUID
		insertLicenses = obligation.LicenseIds
		_, errs := utils.PerformObligationMapActions(tx, userId, &ob, removeLicenses, insertLicenses)
		if len(errs) != 0 {
			for _, err := range errs {
				if err != nil {
					combinedMapErrors += fmt.Sprintf("%s\n", err)
				}
			}
		}

		if combinedMapErrors == "" {
			obdto := ob.ConvertToObligationResponseDTO()
			res := models.ObligationResponse{
				Data:   []models.ObligationResponseDTO{obdto},
				Status: http.StatusOK,
				Meta: models.PaginationMeta{
					ResourceCount: 1,
				},
			}

			c.JSON(http.StatusCreated, res)
		} else {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "Obligation created successfully but license association failed",
				Error:     combinedMapErrors,
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusBadRequest, er)
		}

		return nil
	})
}

// UpdateObligation updates an existing active obligation record
//
//	@Summary		Update obligation
//	@Description	Update an existing obligation record
//	@Id				UpdateObligation
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			id			path		string						true	"Id of the obligation to be updated"
//	@Param			obligation	body		models.ObligationUpdateDTO	true	"Obligation to be updated"
//	@Success		200			{object}	models.ObligationResponse
//	@Failure		400			{object}	models.LicenseError	"Invalid request"
//	@Failure		404			{object}	models.LicenseError	"No obligation with given id found"
//	@Failure		500			{object}	models.LicenseError	"Unable to update obligation"
//	@Security		ApiKeyAuth
//	@Router			/obligations/{id} [patch]
func UpdateObligation(c *gin.Context) {
	var updates models.ObligationUpdateDTO
	var oldObligation models.Obligation
	userId := c.MustGet("userId").(uuid.UUID)

	obligationId, err := uuid.Parse(c.Param("id"))
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("no obligation with id '%s' exists", obligationId.String()),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	if err := db.DB.Joins("Classification").Joins("Type").Preload("Licenses").Where(models.Obligation{Id: obligationId}).First(&oldObligation).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("obligation with id '%s' not found", obligationId.String()),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	if err := c.ShouldBindJSON(&updates); err != nil {
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

	newObligation := updates.ConvertToObligation()
	if newObligation.Text != nil && *oldObligation.Text != *newObligation.Text && !*oldObligation.TextUpdatable {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Text is not updatable",
			Error:     "Field `text_updatable` needs to be true to update the text",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}
	newObligation.Id = oldObligation.Id
	var combinedMapErrors string

	if err := db.DB.Transaction(func(tx *gorm.DB) error {
		if err := tx.Omit("Licenses", "Topic").Updates(&newObligation).Error; err != nil {
			return err
		}

		if err := tx.Joins("Type").Joins("Classification").First(&newObligation).Error; err != nil {
			return err
		}

		if err := addChangelogsForObligation(tx, userId, &newObligation, &oldObligation); err != nil {
			return err
		}

		if updates.LicenseIds == nil {
			return nil
		}

		if err := tx.Where(&models.Obligation{Id: oldObligation.Id}).Preload("Licenses").First(&oldObligation).Error; err != nil {
			return nil
		}
		var licenseIds, removeLicenses, insertLicenses []uuid.UUID

		licenseIds = slices.Compact(*updates.LicenseIds)

		utils.GenerateDiffForReplacingLicenses(&oldObligation, licenseIds, &removeLicenses, &insertLicenses)

		userId := c.MustGet("userId").(uuid.UUID)
		_, errs := utils.PerformObligationMapActions(tx, userId, &oldObligation, removeLicenses, insertLicenses)
		if len(errs) != 0 {
			for _, err := range errs {
				if err != nil {
					combinedMapErrors += fmt.Sprintf("%s\n", err)
				}
			}
			return nil
		}

		return nil
	}); err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Failed to update license",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	if combinedMapErrors != "" {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Obligation created successfully but license association failed",
			Error:     combinedMapErrors,
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
	} else {
		obDto := newObligation.ConvertToObligationResponseDTO()

		res := models.ObligationResponse{
			Data:   []models.ObligationResponseDTO{obDto},
			Status: http.StatusOK,
			Meta: models.PaginationMeta{
				ResourceCount: 1,
			},
		}
		c.JSON(http.StatusOK, res)
	}
}

// DeleteObligation marks an existing obligation record as inactive
//
//	@Summary		Deactivate obligation
//	@Description	Deactivate an obligation
//	@Id				DeleteObligation
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			id	path	string	true	"Id of the obligation to be updated"
//	@Success		204
//	@Failure		404	{object}	models.LicenseError	"No obligation with given id found"
//	@Security		ApiKeyAuth
//	@Router			/obligations/{id} [delete]
func DeleteObligation(c *gin.Context) {
	var obligation models.Obligation

	obligationId, err := uuid.Parse(c.Param("id"))
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("no obligation with id '%s' exists", obligationId.String()),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	if err := db.DB.Where(models.Obligation{Id: obligationId}).First(&obligation).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("obligation with id '%s' not found", obligationId.String()),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}
	*obligation.Active = false
	if err := db.DB.Updates(&obligation).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "failed to delete obligation",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}
	c.Status(http.StatusNoContent)
}

// GetObligationAudits fetches audits corresponding to an obligation
//
//	@Summary		Fetches audits corresponding to an obligation
//	@Description	Fetches audits corresponding to an obligation
//	@Id				GetObligationAudits
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			id		path		string	true	"Id of the obligation for which audits need to be fetched"
//	@Param			page	query		int		false	"Page number"
//	@Param			limit	query		int		false	"Number of records per page"
//	@Success		200		{object}	models.AuditResponse
//	@Failure		404		{object}	models.LicenseError	"No obligation with given id found"
//	@Failure		500		{object}	models.LicenseError	"unable to find audits with such obligation id"
//	@Security		ApiKeyAuth || {}
//	@Router			/obligations/{id}/audits [get]
func GetObligationAudits(c *gin.Context) {
	obligationId, err := uuid.Parse(c.Param("id"))
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("no obligation with id '%s' exists", obligationId.String()),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	var audits []models.Audit
	query := db.DB.Model(&models.Audit{}).Preload("User")
	query.Where(models.Audit{TypeId: obligationId, Type: "OBLIGATION"}).Order("timestamp desc")
	_ = utils.PreparePaginateResponse(c, query, &models.AuditResponse{})

	res := query.Find(&audits)
	if res.Error != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   fmt.Sprintf("unable to find audits with such obligation id '%s'", obligationId.String()),
			Error:     res.Error.Error(),
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
				Message:   fmt.Sprintf("unable to find audits with such obligation id '%s'", obligationId.String()),
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return
		}
	}

	response := models.AuditResponse{
		Data:   audits,
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: len(audits),
		},
	}

	c.JSON(http.StatusOK, response)
}

// ImportObligations creates new obligation records via a json file.
//
//	@Summary		Import obligations by uploading a json file
//	@Description	Import obligations by uploading a json file
//	@Id				ImportObligations
//	@Tags			Obligations
//	@Accept			multipart/form-data
//	@Produce		json
//	@Param			file	formData	file	true	"obligations json file list"
//	@Success		200		{object}	models.ImportObligationsResponse{data=[]models.ObligationImportStatus}
//	@Failure		400		{object}	models.LicenseError	"input file must be present"
//	@Failure		500		{object}	models.LicenseError	"Internal server error"
//	@Security		ApiKeyAuth
//	@Router			/obligations/import [post]
func ImportObligations(c *gin.Context) {
	userId := c.MustGet("userId").(uuid.UUID)
	file, header, err := c.Request.FormFile("file")
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "input file must be present",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}
	defer file.Close()

	if filepath.Ext(header.Filename) != ".json" {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "only files with format *.json are allowed",
			Error:     "only files with format *.json are allowed",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	var obligations []models.ObligationFileDTO
	decoder := json.NewDecoder(file)
	if err := decoder.Decode(&obligations); err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "invalid json",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	res := models.ImportObligationsResponse{
		Status: http.StatusOK,
	}

	for _, ob := range obligations {
		oldObligation := ob.ConvertToObligation()
		newObligation := oldObligation
		_ = db.DB.Transaction(func(tx *gorm.DB) error {
			// If id not present in json object, create a new one.
			//
			// If id present in json object, but entry not found in database (can arise in cases when
			// license/obligation file exported from one LicenseDb instance is imported in another instance)
			// then create a new one
			//
			// If id present in json object and entry found in database, update the database with field values
			// of the json object
			if ob.Id == nil {
				result := tx.Create(&oldObligation)
				if result.Error != nil {
					res.Data = append(res.Data, models.LicenseError{
						Status:    http.StatusBadRequest,
						Message:   fmt.Sprintf("Failed to create/update obligation: %s", result.Error.Error()),
						Error:     *ob.Topic,
						Path:      c.Request.URL.Path,
						Timestamp: time.Now().Format(time.RFC3339),
					})
					return err
				}

				if err := addChangelogsForObligation(tx, userId, &oldObligation, &models.Obligation{}); err != nil {
					res.Data = append(res.Data, models.LicenseError{
						Status:    http.StatusInternalServerError,
						Message:   "Failed to update license",
						Error:     err.Error(),
						Path:      c.Request.URL.Path,
						Timestamp: time.Now().Format(time.RFC3339),
					})
					return err
				}
				// case when obligation doesn't exist in database and is inserted
				res.Data = append(res.Data, models.ObligationImportStatus{
					Data:    models.ObligationId{Id: oldObligation.Id, Topic: *oldObligation.Topic},
					Status:  http.StatusCreated,
					Message: "obligation created successfully",
				})
			} else {
				if err := tx.Where(&models.Obligation{Id: oldObligation.Id}).First(&oldObligation).Error; err != nil {
					res.Data = append(res.Data, models.LicenseError{
						Status:    http.StatusInternalServerError,
						Message:   "Error updating license associations",
						Error:     err.Error(),
						Path:      c.Request.URL.Path,
						Timestamp: time.Now().Format(time.RFC3339),
					})
					return nil
				}
				newObligation.Id = oldObligation.Id
				if err := tx.Omit("Licenses", "Topic").Clauses(clause.Returning{}).Updates(&newObligation).Error; err != nil {
					res.Data = append(res.Data, models.LicenseError{
						Status:    http.StatusBadRequest,
						Message:   fmt.Sprintf("Failed to update obligation: %s", err.Error()),
						Error:     *ob.Topic,
						Path:      c.Request.URL.Path,
						Timestamp: time.Now().Format(time.RFC3339),
					})
					return err
				}
				if err := addChangelogsForObligation(tx, userId, &newObligation, &oldObligation); err != nil {
					res.Data = append(res.Data, models.LicenseError{
						Status:    http.StatusInternalServerError,
						Message:   "Failed to update license",
						Error:     err.Error(),
						Path:      c.Request.URL.Path,
						Timestamp: time.Now().Format(time.RFC3339),
					})
					return err
				}

				res.Data = append(res.Data, models.ObligationImportStatus{
					Data:    models.ObligationId{Id: *ob.Id, Topic: *ob.Topic},
					Status:  http.StatusOK,
					Message: "obligation updated successfully",
				})
			}

			if ob.LicenseIds == nil {
				return nil
			}
			// do not return error so that obligations
			// are created/updated even if the association fails(license is not found etc)
			if err := tx.Where(&models.Obligation{Id: oldObligation.Id}).Preload("Licenses").First(&oldObligation).Error; err != nil {
				return nil
			}
			var licenseIds, removeLicenses, insertLicenses []uuid.UUID

			licenseIds = slices.Compact(*ob.LicenseIds)

			utils.GenerateDiffForReplacingLicenses(&oldObligation, licenseIds, &removeLicenses, &insertLicenses)

			userId := c.MustGet("userId").(uuid.UUID)
			_, errs := utils.PerformObligationMapActions(tx, userId, &oldObligation, removeLicenses, insertLicenses)
			if len(errs) != 0 {
				var combinedErrors string
				for _, err := range errs {
					if err != nil {
						combinedErrors += fmt.Sprintf("%s\n", err)
					}
				}
				res.Data = append(res.Data, models.LicenseError{
					Status:    http.StatusInternalServerError,
					Message:   "Error updating license associations",
					Error:     combinedErrors,
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				})
			} else {
				res.Data = append(res.Data, models.ObligationImportStatus{
					Data:    models.ObligationId{Id: oldObligation.Id, Topic: *ob.Topic},
					Status:  http.StatusOK,
					Message: "licenses associated with obligations successfully",
				})
			}

			return nil
		})
	}

	c.JSON(http.StatusOK, res)
}

// ExportObligations gives users all obligations as a json file.
//
//	@Summary		Export all obligations as a json file
//	@Description	Export all obligations as a json file
//	@Id				ExportObligations
//	@Tags			Obligations
//	@Produce		json
//	@Success		200	{array}		models.ObligationResponseDTO
//	@Failure		500	{object}	models.LicenseError	"Failed to fetch obligations"
//	@Security		ApiKeyAuth || {}
//	@Router			/obligations/export [get]
func ExportObligations(c *gin.Context) {
	var obligations []models.Obligation

	if err := db.DB.Joins("Type").Joins("Classification").Preload("Licenses").Find(&obligations).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Failed to fetch obligations",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	var obligationDtos []models.ObligationResponseDTO

	for _, ob := range obligations {
		obdto := ob.ConvertToObligationResponseDTO()
		obligationDtos = append(obligationDtos, obdto)
	}

	fileName := strings.Map(func(r rune) rune {
		if r == '+' || r == ':' {
			return '_'
		}
		return r
	}, fmt.Sprintf("obligations-export-%s.json", time.Now().Format(time.RFC3339)))

	c.Header("Content-Disposition", fmt.Sprintf("attachment; filename=%s", fileName))
	c.JSON(http.StatusOK, &obligationDtos)
}

// addChangelogsForObligation adds changelogs for the updated fields on obligation update
func addChangelogsForObligation(tx *gorm.DB, userId uuid.UUID,
	newObligation, oldObligation *models.Obligation) error {
	var changes []models.ChangeLog

	var oldType, newType *string
	oldType = nil
	newType = nil
	if oldObligation.Type != nil {
		oldType = &(oldObligation.Type).Type
	}
	if newObligation.Type != nil {
		newType = &(newObligation.Type).Type
	}
	utils.AddChangelog("Type", oldType, newType, &changes)

	utils.AddChangelog("Text", oldObligation.Text, newObligation.Text, &changes)

	oldType = nil
	newType = nil
	if oldObligation.Classification != nil {
		oldType = &(oldObligation.Classification).Classification
	}
	if newObligation.Classification != nil {
		newType = &(newObligation.Classification).Classification
	}
	utils.AddChangelog("Classification", oldType, newType, &changes)

	utils.AddChangelog("Comment", oldObligation.Comment, newObligation.Comment, &changes)

	utils.AddChangelog("Active", oldObligation.Active, newObligation.Active, &changes)

	utils.AddChangelog("Text Updatable", oldObligation.TextUpdatable, newObligation.TextUpdatable, &changes)

	if len(changes) != 0 {
		audit := models.Audit{
			UserId:     userId,
			TypeId:     newObligation.Id,
			Timestamp:  time.Now(),
			Type:       "OBLIGATION",
			ChangeLogs: changes,
		}

		if err := tx.Create(&audit).Error; err != nil {
			return err
		}
	}

	return nil
}

// GetAllObligationPreviews retrieves a list of topics and types of all obligations
//
//	@Summary		Get topic and types of all active obligations
//	@Description	Get topic and type of all active obligations from the service
//	@Id				GetAllObligationPreviews
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			active	query		bool	true	"Active obligation only"
//	@Success		200		{object}	models.ObligationPreviewResponse
//	@Security		ApiKeyAuth || {}
//	@Router			/obligations/preview [get]
func GetAllObligationPreviews(c *gin.Context) {
	var obligations []models.Obligation
	var obligationPreviews []models.ObligationPreview
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

	if err = db.DB.Joins("Type").Where(&models.Obligation{Active: &parsedActive}).Find(&obligations).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Unable to fetch obligations",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	for _, ob := range obligations {
		obligationPreviews = append(obligationPreviews, models.ObligationPreview{
			Topic: *ob.Topic,
			Type:  (*ob.Type).Type,
			Id:    ob.Id,
		})
	}

	res := models.ObligationPreviewResponse{
		Data:   obligationPreviews,
		Status: http.StatusOK,
	}

	c.JSON(http.StatusOK, res)
}

// getSimilarObligation finds similar obligation texts using trigram similarity
//
//	@Summary		Find similar obligations
//	@Description	Returns the top 5 obligations with text similar to the input using pg_trgm
//	@ID				getSimilarObligation
//	@Tags			Obligations
//	@Accept			json
//	@Produce		json
//	@Param			obligation	body		models.SimilarityRequest	true	"Text to compare against stored obligations"
//	@Success		200			{object}	[]models.SimilarObligation	"Similar obligations found"
//	@Failure		400			{object}	models.LicenseError			"Invalid input or database query failure"
//	@Failure		500			{object}	models.LicenseError			"Unexpected server error"
//	@Security		ApiKeyAuth
//	@Router			/obligations/similarity [post]
func getSimilarObligations(c *gin.Context) {
	var req models.SimilarityRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Text field is required",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}
	var results []models.SimilarObligation
	utils.SetSimilarityThreshold()
	rawQuery := `
		SELECT id, topic,text, similarity(text, ?) AS similarity
		FROM obligations
		WHERE text % ?
		ORDER BY similarity DESC
	`
	if err := db.DB.Raw(rawQuery, req.Text, req.Text).Scan(&results).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Database query failed",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}
	res := models.ApiResponse[[]models.SimilarObligation]{
		Status: http.StatusOK,
		Data:   results,
		Meta: &models.PaginationMeta{
			ResourceCount: len(results),
		},
	}
	c.JSON(http.StatusOK, res)
}
