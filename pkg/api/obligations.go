// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
// SPDX-FileContributor: 2025 Chayan Das <01chayandas@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"context"
	"encoding/json"
	"errors"
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
//	@Success		200			{object}	models.SwaggerObligationResponse
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

	res := models.ObligationResponse{
		Data:   obligations,
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: 0,
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
//	@Success		200		{object}	models.SwaggerObligationResponse
//	@Failure		404		{object}	models.LicenseError	"No obligation with given topic found"
//	@Security		ApiKeyAuth || {}
//	@Router			/obligations/{topic} [get]
func GetObligation(c *gin.Context) {
	var obligation models.Obligation
	query := db.DB.Model(&obligation)
	tp := c.Param("topic")
	if err := query.Joins("Type").Joins("Classification").Preload("Licenses").Where(models.Obligation{Topic: &tp}).First(&obligation).Error; err != nil {
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
//	@Param			obligation	body		models.ObligationDTO	true	"Obligation to create"
//	@Success		201			{object}	models.SwaggerObligationResponse
//	@Failure		400			{object}	models.LicenseError	"Bad request body"
//	@Failure		409			{object}	models.LicenseError	"Obligation with same body exists"
//	@Failure		500			{object}	models.LicenseError	"Unable to create obligation"
//	@Security		ApiKeyAuth
//	@Router			/obligations [post]
func CreateObligation(c *gin.Context) {
	var obligation models.Obligation
	userId := c.MustGet("userId").(int64)

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
		result := tx.
			Where(&models.Obligation{Topic: obligation.Topic}).
			Or(&models.Obligation{Md5: obligation.Md5}).
			FirstOrCreate(&obligation)

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

		if result.RowsAffected == 0 {
			er := models.LicenseError{
				Status:  http.StatusConflict,
				Message: "can not create obligation with same topic or text",
				Error: fmt.Sprintf("Error: Obligation with topic '%s' or Text '%s'... already exists",
					*obligation.Topic, (*obligation.Text)[0:10]),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusConflict, er)
			return errors.New("can not create obligation with same topic or text")
		}

		if err := addChangelogsForObligation(tx, userId, &obligation, &models.Obligation{}); err != nil {
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

		res := models.ObligationResponse{
			Data:   []models.Obligation{obligation},
			Status: http.StatusCreated,
			Meta: &models.PaginationMeta{
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
//	@Param			topic		path		string						true	"Topic of the obligation to be updated"
//	@Param			obligation	body		models.ObligationUpdateDTO	true	"Obligation to be updated"
//	@Success		200			{object}	models.SwaggerObligationResponse
//	@Failure		400			{object}	models.LicenseError	"Invalid request"
//	@Failure		404			{object}	models.LicenseError	"No obligation with given topic found"
//	@Failure		500			{object}	models.LicenseError	"Unable to update obligation"
//	@Security		ApiKeyAuth
//	@Router			/obligations/{topic} [patch]
func UpdateObligation(c *gin.Context) {
	var updates models.ObligationUpdateDTO
	var oldObligation models.Obligation
	userId := c.MustGet("userId").(int64)
	tp := c.Param("topic")

	if err := db.DB.Joins("Classification").Joins("Type").Preload("Licenses").Where(models.Obligation{Topic: &tp}).First(&oldObligation).Error; err != nil {
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

	newObligation := updates.Converter()
	newObligation.Id = oldObligation.Id

	if err := db.DB.Transaction(func(tx *gorm.DB) error {
		// https://gorm.io/docs/context.html#Context-in-Hooks-x2F-Callbacks
		ctx := context.WithValue(context.Background(), models.ContextKey("oldObligation"), &oldObligation)
		if err := tx.WithContext(ctx).Omit("Licenses", "Topic").Updates(&newObligation).Error; err != nil {
			return err
		}

		if err := tx.Joins("Type").Joins("Classification").First(&newObligation).Error; err != nil {
			return err
		}

		if err := addChangelogsForObligation(tx, userId, newObligation, &oldObligation); err != nil {
			return err
		}

		newObligation.Licenses = oldObligation.Licenses

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

	res := models.ObligationResponse{
		Data:   []models.Obligation{*newObligation},
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
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
//	@Security		ApiKeyAuth
//	@Router			/obligations/{topic} [delete]
func DeleteObligation(c *gin.Context) {
	var obligation models.Obligation
	tp := c.Param("topic")
	if err := db.DB.Where(models.Obligation{Topic: &tp}).First(&obligation).Error; err != nil {
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
	*obligation.Active = false
	if err := db.DB.Session(&gorm.Session{SkipHooks: true}).Updates(&obligation).Error; err != nil {
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
//	@Param			topic	path		string	true	"Topic of the obligation for which audits need to be fetched"
//	@Param			page	query		int		false	"Page number"
//	@Param			limit	query		int		false	"Number of records per page"
//	@Success		200		{object}	models.AuditResponse
//	@Failure		404		{object}	models.LicenseError	"No obligation with given topic found"
//	@Failure		500		{object}	models.LicenseError	"unable to find audits with such obligation topic"
//
//	@Security		ApiKeyAuth || {}
//
//	@Router			/obligations/{topic}/audits [get]
func GetObligationAudits(c *gin.Context) {
	var obligation models.Obligation
	topic := c.Param("topic")

	result := db.DB.Where(models.Obligation{Topic: &topic}).Select("id").First(&obligation)
	if result.Error != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("obligation with topic '%s' not found", topic),
			Error:     result.Error.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	var audits []models.Audit
	query := db.DB.Model(&models.Audit{}).Preload("User")
	query.Where(models.Audit{TypeId: obligation.Id, Type: "Obligation"}).Order("timestamp desc")
	_ = utils.PreparePaginateResponse(c, query, &models.AuditResponse{})

	res := query.Find(&audits)
	if res.Error != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "unable to find audits with such obligation topic",
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
				Message:   "unable to find audits with such obligation topic",
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
	userId := c.MustGet("userId").(int64)
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

	var obligations []models.Obligation
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
		oldObligation := ob
		newObligation := ob
		_ = db.DB.Transaction(func(tx *gorm.DB) error {
			result := tx.
				Joins("Type").
				Joins("Classification").
				Preload("Licenses").
				Where(&models.Obligation{Topic: oldObligation.Topic}).
				Or(&models.Obligation{Md5: oldObligation.Md5}).
				Omit("Licenses").
				FirstOrCreate(&oldObligation)
			if result.Error != nil {
				res.Data = append(res.Data, models.LicenseError{
					Status:    http.StatusBadRequest,
					Message:   fmt.Sprintf("Failed to create/update obligation: %s", result.Error.Error()),
					Error:     *ob.Topic,
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				})
				return err
			} else if result.RowsAffected == 0 {
				// case when obligation exists in database and is updated
				newObligation.Id = oldObligation.Id
				ctx := context.WithValue(context.Background(), models.ContextKey("oldObligation"), &oldObligation)
				if err := tx.WithContext(ctx).Omit("Licenses", "Topic").Clauses(clause.Returning{}).Updates(&newObligation).Error; err != nil {
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
					Data:    models.ObligationId{Id: ob.Id, Topic: *ob.Topic},
					Status:  http.StatusOK,
					Message: "obligation updated successfully",
				})

			} else {

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
			}

			return nil
		})

		// creating license-obligation associations out of the transaction so that obligations
		// are created/updated even if the association fails(license is not found etc)
		var shortnames, removeLicenses, insertLicenses []string
		for _, lic := range ob.Licenses {
			shortnames = append(shortnames, *lic.Shortname)
		}
		shortnames = slices.Compact(shortnames)

		utils.GenerateDiffForReplacingLicenses(&oldObligation, shortnames, &removeLicenses, &insertLicenses)

		userId := c.MustGet("userId").(int64)
		_, errs := utils.PerformObligationMapActions(userId, &oldObligation, removeLicenses, insertLicenses)
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
				Data:    models.ObligationId{Id: ob.Id, Topic: *ob.Topic},
				Status:  http.StatusOK,
				Message: "licenses associated with obligations successfully",
			})
		}
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
//	@Success		200	{array}		models.ObligationDTO
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

	fileName := strings.Map(func(r rune) rune {
		if r == '+' || r == ':' {
			return '_'
		}
		return r
	}, fmt.Sprintf("obligations-export-%s.json", time.Now().Format(time.RFC3339)))

	c.Header("Content-Disposition", fmt.Sprintf("attachment; filename=%s", fileName))
	c.JSON(http.StatusOK, &obligations)
}

// addChangelogsForObligation adds changelogs for the updated fields on obligation update
func addChangelogsForObligation(tx *gorm.DB, userId int64,
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

	utils.AddChangelog("Modifications", oldObligation.Modifications, newObligation.Modifications, &changes)

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
