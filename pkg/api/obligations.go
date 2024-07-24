// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"path/filepath"
	"strconv"
	"strings"
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
//	@Param			active		query		bool	true	"Active obligation only"
//	@Param			page		query		int		false	"Page number"
//	@Param			limit		query		int		false	"Number of records per page"
//	@Param			order_by	query		string	false	"Asc or desc ordering"	Enums(asc, desc)	default(asc)
//	@Success		200			{object}	models.ObligationResponse
//	@Failure		404			{object}	models.LicenseError	"No obligations in DB"
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

	orderBy := c.Query("order_by")
	queryOrderString := "topic"

	if orderBy != "" && orderBy == "desc" {
		queryOrderString += " desc"
	}

	query.Order(queryOrderString)

	if err = query.Find(&obligations).Error; err != nil {
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
//	@Param			obligation	body		models.ObligationPOSTRequestJSONSchema	true	"Obligation to create"
//	@Success		201			{object}	models.ObligationResponse
//	@Failure		400			{object}	models.LicenseError	"Bad request body"
//	@Failure		409			{object}	models.LicenseError	"Obligation with same body exists"
//	@Failure		500			{object}	models.LicenseError	"Unable to create obligation"
//	@Security		ApiKeyAuth
//	@Router			/obligations [post]
func CreateObligation(c *gin.Context) {
	var input models.ObligationPOSTRequestJSONSchema

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

	obligation := models.Obligation{
		Md5:            md5hash,
		Type:           input.Type,
		Topic:          input.Topic,
		Text:           input.Text,
		Classification: input.Classification,
		Comment:        input.Comment,
		Modifications:  input.Modifications,
		Active:         input.Active,
		TextUpdatable:  false,
	}

	result := db.DB.
		Where(&models.Obligation{Topic: obligation.Topic}).
		Or(&models.Obligation{Md5: obligation.Md5}).
		FirstOrCreate(&obligation)

	if result.RowsAffected == 0 {
		er := models.LicenseError{
			Status:  http.StatusConflict,
			Message: "can not create obligation with same topic or text",
			Error: fmt.Sprintf("Error: Obligation with topic '%s' or Text '%s'... already exists",
				obligation.Topic, obligation.Text[0:10]),
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
//	@Param			topic		path		string									true	"Topic of the obligation to be updated"
//	@Param			obligation	body		models.ObligationPATCHRequestJSONSchema	true	"Obligation to be updated"
//	@Success		200			{object}	models.ObligationResponse
//	@Failure		400			{object}	models.LicenseError	"Invalid request"
//	@Failure		404			{object}	models.LicenseError	"No obligation with given topic found"
//	@Failure		500			{object}	models.LicenseError	"Unable to update obligation"
//	@Security		ApiKeyAuth
//	@Router			/obligations/{topic} [patch]
func UpdateObligation(c *gin.Context) {
	_ = db.DB.Transaction(func(tx *gorm.DB) error {
		var updates models.ObligationPATCHRequestJSONSchema
		var oldObligation models.Obligation
		newObligationMap := make(map[string]interface{})
		username := c.GetString("username")
		tp := c.Param("topic")

		if err := tx.Model(&oldObligation).Where(models.Obligation{Topic: tp}).First(&oldObligation).Error; err != nil {
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

		if err := c.ShouldBindJSON(&updates); err != nil {
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

		if updates.Text.IsDefined {
			if updates.Text.Value == "" {
				er := models.LicenseError{
					Status:    http.StatusBadRequest,
					Message:   "Text cannot be an empty string",
					Error:     "invalid request",
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				}
				c.JSON(http.StatusBadRequest, er)
				return errors.New("invalid request")
			}

			updatedHash := md5.Sum([]byte(updates.Text.Value))
			updatedMd5hash := hex.EncodeToString(updatedHash[:])
			if !oldObligation.TextUpdatable {
				if updatedMd5hash != oldObligation.Md5 {
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
			}
			newObligationMap["md5"] = updatedMd5hash
			newObligationMap["text"] = updates.Text.Value
		}

		if updates.Type.IsDefined {
			if updates.Type.Value == "" {
				er := models.LicenseError{
					Status:    http.StatusBadRequest,
					Message:   "Type cannot be an empty string",
					Error:     "invalid request",
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				}
				c.JSON(http.StatusBadRequest, er)
				return errors.New("invalid request")
			}
			newObligationMap["type"] = updates.Type.Value
		}

		if updates.Classification.IsDefined {
			if updates.Classification.Value == "" {
				er := models.LicenseError{
					Status:    http.StatusBadRequest,
					Message:   "Classification cannot be an empty string",
					Error:     "invalid request",
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				}
				c.JSON(http.StatusBadRequest, er)
				return errors.New("invalid request")
			}
			newObligationMap["classification"] = updates.Classification.Value
		}

		if updates.Modifications.IsDefined {
			newObligationMap["modifications"] = updates.Modifications.Value
		}

		if updates.Comment.IsDefined {
			newObligationMap["comment"] = updates.Comment.Value
		}

		if updates.Active.IsDefined {
			newObligationMap["active"] = updates.Active.Value
		}

		if updates.TextUpdatable.IsDefined {
			newObligationMap["text_updatable"] = updates.TextUpdatable.Value
		}

		var newObligation models.Obligation
		newObligation.Id = oldObligation.Id
		if err := tx.Model(&newObligation).Clauses(clause.Returning{}).Updates(newObligationMap).Error; err != nil {
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

		if err := addChangelogsForObligationUpdate(tx, username, &newObligation, &oldObligation); err != nil {
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
			Data:   []models.Obligation{newObligation},
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

// GetObligationAudits fetches audits corresponding to an obligation

// @Summary		Fetches audits corresponding to an obligation
// @Description	Fetches audits corresponding to an obligation
// @Id				GetObligationAudits
// @Tags			Obligations
// @Accept			json
// @Produce		json
// @Param			topic	path		string	true	"Topic of the obligation for which audits need to be fetched"
// @Param			page	query		int		false	"Page number"
// @Param			limit	query		int		false	"Number of records per page"
// @Success		200		{object}	models.AuditResponse
// @Failure		404		{object}	models.LicenseError	"No obligation with given topic found"
// @Failure		500		{object}	models.LicenseError	"unable to find audits with such obligation topic"
// @Security		ApiKeyAuth
// @Router			/obligations/{topic}/audits [get]
func GetObligationAudits(c *gin.Context) {
	var obligation models.Obligation
	topic := c.Param("topic")

	result := db.DB.Where(models.Obligation{Topic: topic}).Select("id").First(&obligation)
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
	query := db.DB.Model(&models.Audit{})
	query.Where(models.Audit{TypeId: obligation.Id, Type: "Obligation"})
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
	username := c.GetString("username")
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

	var obligations []models.ObligationJSONFileFormat
	decoder := json.NewDecoder(file)
	if err := decoder.Decode(&obligations); err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "invalid json",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	res := models.ImportObligationsResponse{
		Status: http.StatusOK,
	}

	for _, obligation := range obligations {
		_ = db.DB.Transaction(func(tx *gorm.DB) error {
			ob := models.Obligation{
				Topic:          obligation.Topic,
				Type:           obligation.Type,
				Text:           obligation.Text,
				Classification: obligation.Classification,
				Modifications:  obligation.Modifications,
				Comment:        obligation.Comment,
				Active:         obligation.Active,
				TextUpdatable:  obligation.TextUpdatable,
			}

			hash := md5.Sum([]byte(ob.Text))
			md5hash := hex.EncodeToString(hash[:])
			ob.Md5 = md5hash

			oldObligation := ob
			result := tx.
				Where(&models.Obligation{Topic: ob.Topic}).
				Or(&models.Obligation{Md5: ob.Md5}).
				FirstOrCreate(&oldObligation)
			if result.Error != nil {
				res.Data = append(res.Data, models.LicenseError{
					Status:    http.StatusInternalServerError,
					Message:   fmt.Sprintf("Failed to create obligation: %s", result.Error.Error()),
					Error:     ob.Topic,
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				})
				return err
			} else if result.RowsAffected == 0 {
				// case when obligation exists in database and is updated
				result := tx.Model(&ob).Clauses(clause.Returning{}).Where(&models.Obligation{Topic: ob.Topic}).Updates(&ob)
				if result.Error != nil {
					res.Data = append(res.Data, models.LicenseError{
						Status:    http.StatusInternalServerError,
						Message:   fmt.Sprintf("Failed to update obligation: %s", result.Error.Error()),
						Error:     ob.Topic,
						Path:      c.Request.URL.Path,
						Timestamp: time.Now().Format(time.RFC3339),
					})
					return err
				}

				if result.RowsAffected == 0 {
					res.Data = append(res.Data, models.LicenseError{
						Status:    http.StatusConflict,
						Message:   "Another obligation with the same text exists",
						Error:     ob.Topic,
						Path:      c.Request.URL.Path,
						Timestamp: time.Now().Format(time.RFC3339),
					})
					return err
				}

				if err := addChangelogsForObligationUpdate(tx, username, &ob, &oldObligation); err != nil {
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
					Data:   models.ObligationId{Id: ob.Id, Topic: ob.Topic},
					Status: http.StatusOK,
				})

			} else {
				// case when obligation doesn't exist in database and is inserted
				res.Data = append(res.Data, models.ObligationImportStatus{
					Data:   models.ObligationId{Id: oldObligation.Id, Topic: oldObligation.Topic},
					Status: http.StatusCreated,
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
//	@Success		200	{array}		models.ObligationJSONFileFormat
//	@Failure		500	{object}	models.LicenseError	"Failed to fetch obligations"
//	@Router			/obligations/export [get]
func ExportObligations(c *gin.Context) {
	var obligations []models.Obligation
	var obligationsJSONFileFormat []models.ObligationJSONFileFormat

	if err := db.DB.Model(&models.Obligation{}).Find(&obligations).Error; err != nil {
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

	for _, obligation := range obligations {
		var obligationMaps []models.ObligationMap
		if err := db.DB.Model(&obligationMaps).Preload("LicenseDB").Where(models.ObligationMap{ObligationPk: obligation.Id}).Find(&obligationMaps).Error; err != nil {
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

		var shortnames []string
		for _, obMap := range obligationMaps {
			shortnames = append(shortnames, obMap.LicenseDB.Shortname)
		}

		obJSONFileFormat := models.ObligationJSONFileFormat{
			Topic:          obligation.Topic,
			Type:           obligation.Type,
			Text:           obligation.Text,
			Shortnames:     shortnames,
			TextUpdatable:  obligation.TextUpdatable,
			Active:         obligation.Active,
			Modifications:  obligation.Modifications,
			Comment:        obligation.Comment,
			Classification: obligation.Classification,
		}

		obligationsJSONFileFormat = append(obligationsJSONFileFormat, obJSONFileFormat)
	}

	fileName := strings.Map(func(r rune) rune {
		if r == '+' || r == ':' {
			return '_'
		}
		return r
	}, fmt.Sprintf("obligations-export-%s.json", time.Now().Format(time.RFC3339)))

	c.Header("Content-Disposition", fmt.Sprintf("attachment; filename=%s", fileName))
	c.JSON(http.StatusOK, &obligationsJSONFileFormat)
}

// addChangelogsForObligationUpdate adds changelogs for the updated fields on obligation update
func addChangelogsForObligationUpdate(tx *gorm.DB, username string,
	newObligation, oldObligation *models.Obligation) error {
	var user models.User
	if err := tx.Where(models.User{Username: username}).First(&user).Error; err != nil {
		return err
	}
	var changes []models.ChangeLog

	if oldObligation.Topic != newObligation.Topic {
		changes = append(changes, models.ChangeLog{
			Field:        "Topic",
			OldValue:     &oldObligation.Topic,
			UpdatedValue: &newObligation.Topic,
		})
	}
	if oldObligation.Type != newObligation.Type {
		changes = append(changes, models.ChangeLog{
			Field:        "Type",
			OldValue:     &oldObligation.Type,
			UpdatedValue: &newObligation.Type,
		})
	}
	if oldObligation.Md5 != newObligation.Md5 {
		changes = append(changes, models.ChangeLog{
			Field:        "Text",
			OldValue:     &oldObligation.Text,
			UpdatedValue: &newObligation.Text,
		})
	}
	if oldObligation.Classification != newObligation.Classification {
		changes = append(changes, models.ChangeLog{
			Field:        "Classification",
			OldValue:     &oldObligation.Classification,
			UpdatedValue: &newObligation.Classification,
		})
	}
	if oldObligation.Modifications != newObligation.Modifications {
		oldVal := strconv.FormatBool(oldObligation.Modifications)
		newVal := strconv.FormatBool(newObligation.Modifications)
		changes = append(changes, models.ChangeLog{
			Field:        "Modifications",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldObligation.Comment != newObligation.Comment {
		changes = append(changes, models.ChangeLog{
			Field:        "Comment",
			OldValue:     &oldObligation.Comment,
			UpdatedValue: &newObligation.Comment,
		})
	}
	if oldObligation.Active != newObligation.Active {
		oldVal := strconv.FormatBool(oldObligation.Active)
		newVal := strconv.FormatBool(newObligation.Active)
		changes = append(changes, models.ChangeLog{
			Field:        "Active",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldObligation.TextUpdatable != newObligation.TextUpdatable {
		oldVal := strconv.FormatBool(oldObligation.TextUpdatable)
		newVal := strconv.FormatBool(newObligation.TextUpdatable)
		changes = append(changes, models.ChangeLog{
			Field:        "TextUpdatable",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}

	if len(changes) != 0 {
		audit := models.Audit{
			UserId:     user.Id,
			TypeId:     newObligation.Id,
			Timestamp:  time.Now(),
			Type:       "Obligation",
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
	query := db.DB.Model(&models.Obligation{})
	query.Where("active = ?", parsedActive)

	if err = query.Find(&obligations).Error; err != nil {
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
			Topic: ob.Topic,
			Type:  ob.Type,
		})
	}

	res := models.ObligationPreviewResponse{
		Data:   obligationPreviews,
		Status: http.StatusOK,
	}

	c.JSON(http.StatusOK, res)
}
