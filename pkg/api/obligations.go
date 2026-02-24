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
	"errors"
	"fmt"
	"net/http"
	"path/filepath"
	"reflect"
	"slices"
	"strconv"
	"strings"
	"time"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"gorm.io/gorm"
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
		if err := tx.Omit("Licenses").Create(&ob).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "Failed to create obligation",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusBadRequest, er)
			return err
		}

		insertLicenses := obligation.LicenseIds
		errs := utils.PerformObligationMapActions(tx, userId, &ob, insertLicenses)
		if len(errs) != 0 {
			var combinedMapErrors strings.Builder
			for _, err := range errs {
				if err != nil {
					fmt.Fprintf(&combinedMapErrors, "%s\n", err)
				}
			}
			er := models.LicenseError{
				Status:    http.StatusNotFound,
				Message:   "Failed to create obligation",
				Error:     combinedMapErrors.String(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusNotFound, er)
			return errors.New(combinedMapErrors.String())
		}

		if err := tx.Joins("Classification").Joins("Type").Preload("Licenses").First(&ob, ob.Id).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Failed to create obligation",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return err
		}

		if err := addChangelogsForObligation(tx, userId, &ob, &models.Obligation{}); err != nil {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "Failed to create obligation",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusBadRequest, er)
			return err
		}

		obdto := ob.ConvertToObligationResponseDTO()
		res := models.ObligationResponse{
			Data:   []models.ObligationResponseDTO{obdto},
			Status: http.StatusOK,
			Meta: models.PaginationMeta{
				ResourceCount: 1,
			},
		}

		c.JSON(http.StatusCreated, res)

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

	if err := db.DB.Transaction(func(tx *gorm.DB) error {
		// Overwrite values of existing keys, add new key value pairs and remove keys with null values.
		if err := tx.Model(&models.Obligation{}).Where(models.Obligation{Id: oldObligation.Id}).UpdateColumn("external_ref", gorm.Expr("jsonb_strip_nulls(COALESCE(external_ref, '{}'::jsonb) || ?)", updates.ExternalRef)).Error; err != nil {
			return err
		}

		if err := tx.Omit("ExternalRef", "Licenses", "Topic").Updates(&newObligation).Error; err != nil {
			return err
		}

		userId := c.MustGet("userId").(uuid.UUID)
		if updates.LicenseIds != nil {
			errs := utils.PerformObligationMapActions(tx, userId, &oldObligation, *updates.LicenseIds)
			if len(errs) != 0 {
				var combinedMapErrors strings.Builder
				for _, err := range errs {
					if err != nil {
						fmt.Fprintf(&combinedMapErrors, "%s\n", err)
					}
				}
				return errors.New(combinedMapErrors.String())
			}
		}

		if err := tx.Joins("Type").Joins("Classification").Preload("Licenses").First(&newObligation).Error; err != nil {
			return err
		}

		if err := addChangelogsForObligation(tx, userId, &newObligation, &oldObligation); err != nil {
			return err
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
			// (a) If id not present in json object, create a new one.
			//
			// (b) If id present in json object, but entry not found in database (can arise in cases when
			// license/obligation file exported from one LicenseDb instance is imported in another instance)
			// then create a new one
			//
			// (c) If id present in json object and entry found in database, update the database with field values
			// of the json object
			if ob.Id == nil {
				// Case (a)
				result := tx.Omit("Licenses").Create(&oldObligation)
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

				var message string
				if ob.LicenseIds != nil {
					userId := c.MustGet("userId").(uuid.UUID)
					errs := utils.PerformObligationMapActions(tx, userId, &oldObligation, *ob.LicenseIds)
					if len(errs) != 0 {
						var combinedMapErrors strings.Builder
						for _, err := range errs {
							if err != nil {
								fmt.Fprintf(&combinedMapErrors, "%s\n", err)
							}
						}
						message = fmt.Sprintf("Obligation created successfully but there was en error creating license associations: %s", combinedMapErrors.String())
					}
				}

				if err := tx.Joins("Classification").Joins("Type").Preload("Licenses").First(&oldObligation, oldObligation.Id).Error; err != nil {
					er := models.LicenseError{
						Status:    http.StatusInternalServerError,
						Message:   "Failed to create obligation",
						Error:     err.Error(),
						Path:      c.Request.URL.Path,
						Timestamp: time.Now().Format(time.RFC3339),
					}
					c.JSON(http.StatusInternalServerError, er)
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
				if message == "" {
					message = "obligation created successfully"
				}
				res.Data = append(res.Data, models.ObligationImportStatus{
					Data:    models.ObligationId{Id: oldObligation.Id, Topic: *oldObligation.Topic},
					Status:  http.StatusCreated,
					Message: message,
				})
			} else {
				if err := tx.Where(&models.Obligation{Id: oldObligation.Id}).First(&oldObligation).Error; err != nil {
					if errors.Is(err, gorm.ErrRecordNotFound) {
						result := tx.Omit("Licenses").Create(&oldObligation)
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

						var message string
						if ob.LicenseIds != nil {
							userId := c.MustGet("userId").(uuid.UUID)
							errs := utils.PerformObligationMapActions(tx, userId, &oldObligation, *ob.LicenseIds)
							if len(errs) != 0 {
								var combinedMapErrors strings.Builder
								for _, err := range errs {
									if err != nil {
										fmt.Fprintf(&combinedMapErrors, "%s\n", err)
									}
								}
								message = fmt.Sprintf("Obligation created successfully but there was en error creating license associations: %s", combinedMapErrors.String())
							}
						}

						if err := tx.Joins("Classification").Joins("Type").Preload("Licenses").First(&oldObligation, oldObligation.Id).Error; err != nil {
							res.Data = append(res.Data, models.LicenseError{
								Status:    http.StatusInternalServerError,
								Message:   "Failed to update license",
								Error:     err.Error(),
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
						if message == "" {
							message = "obligation created successfully"
						}
						res.Data = append(res.Data, models.ObligationImportStatus{
							Data:    models.ObligationId{Id: oldObligation.Id, Topic: *oldObligation.Topic},
							Status:  http.StatusCreated,
							Message: message,
						})
					} else {
						res.Data = append(res.Data, models.LicenseError{
							Status:    http.StatusInternalServerError,
							Message:   "Error updating license associations",
							Error:     err.Error(),
							Path:      c.Request.URL.Path,
							Timestamp: time.Now().Format(time.RFC3339),
						})
						return nil
					}
				} else {
					if newObligation.Text != nil && *oldObligation.Text != *newObligation.Text && !*oldObligation.TextUpdatable {
						res.Data = append(res.Data, models.LicenseError{
							Status:    http.StatusBadRequest,
							Message:   "Text is not updatable",
							Error:     "Field `text_updatable` needs to be true to update the text",
							Path:      c.Request.URL.Path,
							Timestamp: time.Now().Format(time.RFC3339),
						})
						return errors.New("field `text_updatable` needs to be true to update the text")
					}
					if err := tx.Model(&models.Obligation{}).Where(models.Obligation{Id: oldObligation.Id}).UpdateColumn("external_ref", gorm.Expr("jsonb_strip_nulls(COALESCE(external_ref, '{}'::jsonb) || ?)", ob.ExternalRef)).Error; err != nil {
						res.Data = append(res.Data, models.LicenseError{
							Status:    http.StatusInternalServerError,
							Message:   "Failed to update license",
							Error:     err.Error(),
							Path:      c.Request.URL.Path,
							Timestamp: time.Now().Format(time.RFC3339),
						})
						return err
					}

					if err := tx.Omit("ExternalRef", "Licenses", "Topic").Updates(&newObligation).Error; err != nil {
						res.Data = append(res.Data, models.LicenseError{
							Status:    http.StatusInternalServerError,
							Message:   "Failed to update license",
							Error:     err.Error(),
							Path:      c.Request.URL.Path,
							Timestamp: time.Now().Format(time.RFC3339),
						})
						return err
					}

					var message string
					if ob.LicenseIds != nil {
						userId := c.MustGet("userId").(uuid.UUID)
						errs := utils.PerformObligationMapActions(tx, userId, &oldObligation, *ob.LicenseIds)
						if len(errs) != 0 {
							var combinedMapErrors strings.Builder
							for _, err := range errs {
								if err != nil {
									fmt.Fprintf(&combinedMapErrors, "%s\n", err)
								}
							}
							message = fmt.Sprintf("Obligation updated successfully but there was en error updating license associations: %s", combinedMapErrors.String())
						}
					}

					if err := tx.Joins("Type").Joins("Classification").Preload("Licenses").First(&newObligation).Error; err != nil {
						res.Data = append(res.Data, models.LicenseError{
							Status:    http.StatusInternalServerError,
							Message:   "Failed to update license",
							Error:     err.Error(),
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

					if message == "" {
						message = "obligation updated successfully"
					}
					res.Data = append(res.Data, models.ObligationImportStatus{
						Data:    models.ObligationId{Id: *ob.Id, Topic: *ob.Topic},
						Status:  http.StatusOK,
						Message: message,
					})
				}
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
	uuidsToStr := func(ids []models.LicenseDB) string {
		if len(ids) == 0 {
			return ""
		}
		s := make([]string, 0, len(ids))
		for _, lic := range ids {
			s = append(s, lic.Id.String())
		}
		slices.Sort(s)
		return strings.Join(s, ", ")
	}
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

	oldObligationExternalRef := oldObligation.ExternalRef.Data()
	oldExternalRefVal := reflect.ValueOf(oldObligationExternalRef)
	typesOf := oldExternalRefVal.Type()

	newObligationExternalRef := newObligation.ExternalRef.Data()
	newExternalRefVal := reflect.ValueOf(newObligationExternalRef)

	for i := 0; i < oldExternalRefVal.NumField(); i++ {
		fieldName := typesOf.Field(i).Name

		switch typesOf.Field(i).Type.String() {
		case "*boolean":
			oldFieldPtr, _ := oldExternalRefVal.Field(i).Interface().(*bool)
			newFieldPtr, _ := newExternalRefVal.Field(i).Interface().(*bool)
			utils.AddChangelog(fmt.Sprintf("External Reference %s", fieldName), oldFieldPtr, newFieldPtr, &changes)
		case "*string":
			oldFieldPtr, _ := oldExternalRefVal.Field(i).Interface().(*string)
			newFieldPtr, _ := newExternalRefVal.Field(i).Interface().(*string)
			utils.AddChangelog(fmt.Sprintf("External Reference %s", fieldName), oldFieldPtr, newFieldPtr, &changes)
		case "*int":
			oldFieldPtr, _ := oldExternalRefVal.Field(i).Interface().(*int)
			newFieldPtr, _ := newExternalRefVal.Field(i).Interface().(*int)
			utils.AddChangelog(fmt.Sprintf("External Reference %s", fieldName), oldFieldPtr, newFieldPtr, &changes)
		}
	}

	oldVal := uuidsToStr(oldObligation.Licenses)
	newVal := uuidsToStr(newObligation.Licenses)

	utils.AddChangelog("Licenses", &oldVal, &newVal, &changes)

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
