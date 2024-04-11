// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/gin-gonic/gin"

	"github.com/gin-gonic/gin/binding"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"
)

// GetAllLicense The get all License function returns all the license data present in the database.
func GetAllLicense(c *gin.Context) {

	var licenses []models.LicenseDB
	query := db.DB.Model(&models.LicenseDB{})

	_ = utils.PreparePaginateResponse(c, query, &models.LicenseResponse{})

	err := query.Find(&licenses).Error
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Licenses not found",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}
	res := models.LicenseResponse{
		Data:   licenses,
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: len(licenses),
		},
	}

	c.JSON(http.StatusOK, res)
}

// FilterLicense Get licenses from service based on different filters.
//
//	@Summary		Filter licenses
//	@Description	Filter licenses based on different parameters
//	@Id				FilterLicense
//	@Tags			Licenses
//	@Accept			json
//	@Produce		json
//	@Param			spdxid			query		string					false	"SPDX ID of the license"
//	@Param			detector_type	query		int						false	"License detector type"
//	@Param			gplv2compatible	query		bool					false	"GPLv2 compatibility flag status of license"
//	@Param			gplv3compatible	query		bool					false	"GPLv3 compatibility flag status of license"
//	@Param			marydone		query		bool					false	"Mary done flag status of license"
//	@Param			active			query		bool					false	"Active license only"
//	@Param			osiapproved		query		bool					false	"OSI Approved flag status of license"
//	@Param			fsffree			query		bool					false	"FSF Free flag status of license"
//	@Param			copyleft		query		bool					false	"Copyleft flag status of license"
//	@Param			page			query		int						false	"Page number"
//	@Param			limit			query		int						false	"Limit of responses per page"
//	@Param			externalRef		query		string					false	"External reference parameters"
//	@Success		200				{object}	models.LicenseResponse	"Filtered licenses"
//	@Failure		400				{object}	models.LicenseError		"Invalid value"
//	@Router			/licenses [get]
func FilterLicense(c *gin.Context) {
	SpdxId := c.Query("spdxid")
	DetectorType := c.Query("detector_type")
	GPLv2compatible := c.Query("gplv2compatible")
	GPLv3compatible := c.Query("gplv3compatible")
	marydone := c.Query("marydone")
	active := c.Query("active")
	OSIapproved := c.Query("osiapproved")
	fsffree := c.Query("fsffree")
	copyleft := c.Query("copyleft")
	externalRef := c.Query("externalRef")

	externalRefData := make(map[string]string)

	if len(externalRef) > 0 {
		err := json.Unmarshal([]byte(externalRef), &externalRefData)
		if err != nil {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "invalid external ref type value",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusBadRequest, er)
			return
		}
	}

	var license []models.LicenseDB
	query := db.DB.Model(&license)

	if SpdxId == "" && GPLv2compatible == "" && GPLv3compatible == "" && DetectorType == "" && marydone == "" && active == "" && fsffree == "" && OSIapproved == "" && copyleft == "" && externalRef == "" {
		GetAllLicense(c)
		return
	}
	if active != "" {
		parsedActive, err := strconv.ParseBool(active)
		if err != nil {
			parsedActive = false
		}
		query = query.Where(models.LicenseDB{Active: parsedActive})
	}

	if fsffree != "" {
		parsedFsffree, err := strconv.ParseBool(fsffree)
		if err != nil {
			parsedFsffree = false
		}
		query = query.Where(models.LicenseDB{FSFfree: parsedFsffree})
	}

	if OSIapproved != "" {
		parsedOsiApproved, err := strconv.ParseBool(OSIapproved)
		if err != nil {
			parsedOsiApproved = false
		}
		query = query.Where(models.LicenseDB{OSIapproved: parsedOsiApproved})
	}

	if copyleft != "" {
		parsedCopyleft, err := strconv.ParseBool(copyleft)
		if err != nil {
			parsedCopyleft = false
		}
		query = query.Where(models.LicenseDB{Copyleft: parsedCopyleft})
	}

	if SpdxId != "" {
		query = query.Where(models.LicenseDB{SpdxId: SpdxId})
	}

	if DetectorType != "" {
		parsedDetectorType, err := strconv.ParseInt(DetectorType, 10, 64)
		if err != nil {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "invalid detector type value",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusBadRequest, er)
			return
		}
		query = query.Where(models.LicenseDB{DetectorType: parsedDetectorType})
	}

	if GPLv2compatible != "" {
		parsedGPLv2compatible, err := strconv.ParseBool(GPLv2compatible)
		if err != nil {
			parsedGPLv2compatible = false
		}
		query = query.Where(models.LicenseDB{GPLv2compatible: parsedGPLv2compatible})
	}

	if GPLv3compatible != "" {
		parsedGPLv3compatible, err := strconv.ParseBool(GPLv3compatible)
		if err != nil {
			parsedGPLv3compatible = false
		}
		query = query.Where(models.LicenseDB{GPLv3compatible: parsedGPLv3compatible})
	}

	if marydone != "" {
		parsedMarydone, err := strconv.ParseBool(marydone)
		if err != nil {
			parsedMarydone = false
		}
		query = query.Where(models.LicenseDB{Marydone: parsedMarydone})
	}

	for externalRefKey, externalRefValue := range externalRefData {
		query = query.Where(fmt.Sprintf("external_ref->>'%s' = ?", externalRefKey), externalRefValue)
	}

	if err := query.Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "incorrect query to search in the database",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	_ = utils.PreparePaginateResponse(c, query, &models.LicenseResponse{})

	query.Find(&license)

	res := models.LicenseResponse{
		Data:   license,
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: len(license),
		},
	}
	c.JSON(http.StatusOK, res)
}

// GetLicense to get a single license by its shortname
//
//	@Summary		Get a license by shortname
//	@Description	Get a single license by its shortname
//	@Id				GetLicense
//	@Tags			Licenses
//	@Accept			json
//	@Produce		json
//	@Param			shortname	path		string	true	"Shortname of the license"
//	@Success		200			{object}	models.LicenseResponse
//	@Failure		404			{object}	models.LicenseError	"License with shortname not found"
//	@Router			/licenses/{shortname} [get]
func GetLicense(c *gin.Context) {
	var license models.LicenseDB

	queryParam := c.Param("shortname")
	if queryParam == "" {
		return
	}

	err := db.DB.Where(models.LicenseDB{Shortname: queryParam}).First(&license).Error

	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   fmt.Sprintf("no license with shortname '%s' exists", queryParam),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	res := models.LicenseResponse{
		Data:   []models.LicenseDB{license},
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusOK, res)
}

// CreateLicense creates a new license in the database.
//
//	@Summary		Create a new license
//	@Description	Create a new license in the service
//	@Id				CreateLicense
//	@Tags			Licenses
//	@Accept			json
//	@Produce		json
//	@Param			license	body		models.LicensePOSTRequestJSONSchema	true	"New license to be created"
//	@Success		201		{object}	models.LicenseResponse				"New license created successfully"
//	@Failure		400		{object}	models.LicenseError					"Invalid request body"
//	@Failure		409		{object}	models.LicenseError					"License with same shortname already exists"
//	@Failure		500		{object}	models.LicenseError					"Failed to create license"
//	@Security		ApiKeyAuth
//	@Router			/licenses [post]
func CreateLicense(c *gin.Context) {
	var input models.LicensePOSTRequestJSONSchema

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

	license := models.LicenseDB{
		Shortname:       input.Shortname,
		Fullname:        input.Fullname,
		Text:            input.Text,
		Url:             input.Url,
		Copyleft:        input.Copyleft,
		Active:          input.Active,
		FSFfree:         input.FSFfree,
		GPLv2compatible: input.GPLv2compatible,
		GPLv3compatible: input.GPLv3compatible,
		OSIapproved:     input.OSIapproved,
		TextUpdatable:   input.TextUpdatable,
		DetectorType:    input.DetectorType,
		Marydone:        input.Marydone,
		Notes:           input.Notes,
		Fedora:          input.Fedora,
		Flag:            input.Flag,
		Source:          input.Source,
		SpdxId:          input.SpdxId,
		Risk:            input.Risk,
		ExternalRef:     input.ExternalRef,
	}

	result := db.DB.
		Where(&models.LicenseDB{Shortname: license.Shortname}).
		FirstOrCreate(&license)
	if result.RowsAffected == 0 {
		er := models.LicenseError{
			Status:    http.StatusConflict,
			Message:   "can not create license with same shortname",
			Error:     fmt.Sprintf("Error: License with shortname '%s' already exists", input.Shortname),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusConflict, er)
		return
	}
	if result.Error != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Failed to create license",
			Error:     result.Error.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}
	res := models.LicenseResponse{
		Data:   []models.LicenseDB{license},
		Status: http.StatusCreated,
		Meta: &models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusCreated, res)
}

// UpdateLicense Update license with given shortname and create audit and changelog entries.
//
//	@Summary		Update a license
//	@Description	Update a license in the service
//	@Id				UpdateLicense
//	@Tags			Licenses
//	@Accept			json
//	@Produce		json
//	@Param			shortname	path		string									true	"Shortname of the license to be updated"
//	@Param			license		body		models.LicensePATCHRequestJSONSchema	true	"Update license body (requires only the fields to be updated)"
//	@Success		200			{object}	models.LicenseResponse					"License updated successfully"
//	@Failure		400			{object}	models.LicenseError						"Invalid license body"
//	@Failure		404			{object}	models.LicenseError						"License with shortname not found"
//	@Failure		409			{object}	models.LicenseError						"License with same shortname already exists"
//	@Failure		500			{object}	models.LicenseError						"Failed to update license"
//	@Security		ApiKeyAuth
//	@Router			/licenses/{shortname} [patch]
func UpdateLicense(c *gin.Context) {
	_ = db.DB.Transaction(func(tx *gorm.DB) error {
		var updates models.LicensePATCHRequestJSONSchema
		var externalRefsPayload models.UpdateExternalRefsJSONPayload
		var newLicense models.LicenseDB
		var oldLicense models.LicenseDB
		newLicenseMap := make(map[string]interface{})

		username := c.GetString("username")

		shortname := c.Param("shortname")
		if err := tx.Where(models.LicenseDB{Shortname: shortname}).First(&oldLicense).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusNotFound,
				Message:   fmt.Sprintf("license with shortname '%s' not found", shortname),
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusNotFound, er)
			return err
		}

		// https://github.com/gin-gonic/gin/pull/1341
		if err := c.ShouldBindBodyWith(&updates, binding.JSON); err != nil {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "invalid json body update",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusBadRequest, er)
			return err
		}

		if err := c.ShouldBindBodyWith(&externalRefsPayload, binding.JSON); err != nil {
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

		// Overwrite values of existing keys, add new key value pairs and remove keys with null values.
		if err := tx.Model(&oldLicense).UpdateColumn("external_ref", gorm.Expr("jsonb_strip_nulls(external_ref || ?)", externalRefsPayload.ExternalRef)).Error; err != nil {
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

		if updates.Text.IsDefined && oldLicense.Text != updates.Text.Value {
			if !oldLicense.TextUpdatable {
				er := models.LicenseError{
					Status:    http.StatusBadRequest,
					Message:   "Text is not updatable",
					Error:     "Field `rf_text_updatable` needs to be true to update the text",
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				}
				c.JSON(http.StatusBadRequest, er)
				return errors.New("field `rf_text_updatable` needs to be true to update the text")
			}

			if updates.Text.Value == "" {
				er := models.LicenseError{
					Status:    http.StatusBadRequest,
					Message:   "`rf_text` field cannot be empty",
					Error:     "`rf_text` field cannot be empty",
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				}
				c.JSON(http.StatusBadRequest, er)
				return errors.New("`rf_text` field cannot be empty")
			}

			// Update flag to indicate the license text was updated.
			newLicenseMap["rf_flag"] = 2
			newLicenseMap["rf_text"] = updates.Text.Value
		}

		if updates.Fullname.IsDefined {
			if updates.Fullname.Value == "" {
				er := models.LicenseError{
					Status:    http.StatusBadRequest,
					Message:   "`rf_fullname` field cannot be empty",
					Error:     "`rf_fullname` field cannot be empty",
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				}
				c.JSON(http.StatusBadRequest, er)
				return errors.New("`rf_fullname` field cannot be empty")
			}
			newLicenseMap["rf_fullname"] = updates.Fullname.Value
		}

		if updates.SpdxId.IsDefined {
			if updates.SpdxId.Value == "" {
				er := models.LicenseError{
					Status:    http.StatusBadRequest,
					Message:   "`rf_spdx_id` field cannot be empty",
					Error:     "`rf_spdx_id` field cannot be empty",
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				}
				c.JSON(http.StatusBadRequest, er)
				return errors.New("`rf_spdx_id` field cannot be empty")
			}
			newLicenseMap["rf_spdx_id"] = updates.SpdxId.Value
		}

		if updates.Url.IsDefined {
			newLicenseMap["rf_url"] = updates.Url.Value
		}

		if updates.Copyleft.IsDefined {
			newLicenseMap["rf_copyleft"] = updates.Copyleft.Value
		}

		if updates.FSFfree.IsDefined {
			newLicenseMap["rf_FSFfree"] = updates.FSFfree.Value
		}

		if updates.OSIapproved.IsDefined {
			newLicenseMap["rf_OSIapproved"] = updates.OSIapproved.Value
		}

		if updates.GPLv2compatible.IsDefined {
			newLicenseMap["rf_GPLv2compatible"] = updates.GPLv2compatible.Value
		}

		if updates.GPLv3compatible.IsDefined {
			newLicenseMap["rf_GPLv3compatible"] = updates.GPLv3compatible.Value
		}

		if updates.Notes.IsDefined {
			newLicenseMap["rf_notes"] = updates.Notes.Value
		}

		if updates.Fedora.IsDefined {
			newLicenseMap["rf_Fedora"] = updates.Fedora.Value
		}

		if updates.TextUpdatable.IsDefined {
			newLicenseMap["rf_text_updatable"] = updates.TextUpdatable.Value
		}

		if updates.DetectorType.IsDefined {
			newLicenseMap["rf_detector_type"] = updates.DetectorType.Value
		}

		if updates.Active.IsDefined {
			newLicenseMap["rf_active"] = updates.Active.Value
		}

		if updates.Source.IsDefined {
			newLicenseMap["rf_source"] = updates.Source.Value
		}

		if updates.Risk.IsDefined {
			newLicenseMap["rf_risk"] = updates.Risk.Value
		}

		if updates.Flag.IsDefined {
			newLicenseMap["rf_flag"] = updates.Flag.Value
		}

		if updates.Marydone.IsDefined {
			newLicenseMap["marydone"] = updates.Marydone.Value
		}

		// Update all other fields except external_ref
		if err := tx.Model(&newLicense).Where(models.LicenseDB{Id: oldLicense.Id}).Clauses(clause.Returning{}).Updates(newLicenseMap).Error; err != nil {
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

		if err := addChangelogsForLicenseUpdate(tx, username, &newLicense, &oldLicense); err != nil {
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

		res := models.LicenseResponse{
			Data:   []models.LicenseDB{newLicense},
			Status: http.StatusOK,
			Meta: &models.PaginationMeta{
				ResourceCount: 1,
			},
		}

		c.JSON(http.StatusOK, res)

		return nil
	})
}

// addChangelogsForLicenseUpdate adds changelogs for the updated fields on license update
func addChangelogsForLicenseUpdate(tx *gorm.DB, username string,
	newLicense, oldLicense *models.LicenseDB) error {
	var user models.User
	if err := tx.Where(models.User{Username: username}).First(&user).Error; err != nil {
		return err
	}
	var changes []models.ChangeLog

	if oldLicense.Fullname != newLicense.Fullname {
		changes = append(changes, models.ChangeLog{
			Field:        "Fullname",
			OldValue:     &oldLicense.Fullname,
			UpdatedValue: &newLicense.Fullname,
		})
	}
	if oldLicense.Url != newLicense.Url {
		changes = append(changes, models.ChangeLog{
			Field:        "Url",
			OldValue:     &oldLicense.Url,
			UpdatedValue: &newLicense.Url,
		})
	}
	if oldLicense.AddDate != newLicense.AddDate {
		oldVal := oldLicense.AddDate.Format(time.RFC3339)
		newVal := newLicense.AddDate.Format(time.RFC3339)
		changes = append(changes, models.ChangeLog{
			Field:        "Adddate",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldLicense.Active != newLicense.Active {
		oldVal := strconv.FormatBool(oldLicense.Active)
		newVal := strconv.FormatBool(newLicense.Active)
		changes = append(changes, models.ChangeLog{
			Field:        "Active",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldLicense.Copyleft != newLicense.Copyleft {
		oldVal := strconv.FormatBool(oldLicense.Copyleft)
		newVal := strconv.FormatBool(newLicense.Copyleft)
		changes = append(changes, models.ChangeLog{
			Field:        "Copyleft",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldLicense.FSFfree != newLicense.FSFfree {
		oldVal := strconv.FormatBool(oldLicense.FSFfree)
		newVal := strconv.FormatBool(newLicense.FSFfree)
		changes = append(changes, models.ChangeLog{
			Field:        "FSFfree",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldLicense.GPLv2compatible != newLicense.GPLv2compatible {
		oldVal := strconv.FormatBool(oldLicense.GPLv2compatible)
		newVal := strconv.FormatBool(newLicense.GPLv2compatible)
		changes = append(changes, models.ChangeLog{
			Field:        "GPLv2compatible",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldLicense.GPLv3compatible != newLicense.GPLv3compatible {
		oldVal := strconv.FormatBool(oldLicense.GPLv3compatible)
		newVal := strconv.FormatBool(newLicense.GPLv3compatible)
		changes = append(changes, models.ChangeLog{
			Field:        "GPLv3compatible",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldLicense.OSIapproved != newLicense.OSIapproved {
		oldVal := strconv.FormatBool(oldLicense.OSIapproved)
		newVal := strconv.FormatBool(newLicense.OSIapproved)
		changes = append(changes, models.ChangeLog{
			Field:        "OSIapproved",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldLicense.Text != newLicense.Text {
		changes = append(changes, models.ChangeLog{
			Field:        "Text",
			OldValue:     &oldLicense.Text,
			UpdatedValue: &newLicense.Text,
		})
	}
	if oldLicense.TextUpdatable != newLicense.TextUpdatable {
		oldVal := strconv.FormatBool(oldLicense.TextUpdatable)
		newVal := strconv.FormatBool(newLicense.TextUpdatable)
		changes = append(changes, models.ChangeLog{
			Field:        "TextUpdatable",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldLicense.Fedora != newLicense.Fedora {
		changes = append(changes, models.ChangeLog{
			Field:        "Fedora",
			OldValue:     &oldLicense.Fedora,
			UpdatedValue: &newLicense.Fedora,
		})
	}
	if oldLicense.Flag != newLicense.Flag {
		oldVal := strconv.FormatInt(oldLicense.Flag, 10)
		newVal := strconv.FormatInt(newLicense.Flag, 10)
		changes = append(changes, models.ChangeLog{
			Field:        "Flag",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldLicense.Notes != newLicense.Notes {
		changes = append(changes, models.ChangeLog{
			Field:        "Notes",
			OldValue:     &oldLicense.Notes,
			UpdatedValue: &newLicense.Notes,
		})
	}
	if oldLicense.DetectorType != newLicense.DetectorType {
		oldVal := strconv.FormatInt(oldLicense.DetectorType, 10)
		newVal := strconv.FormatInt(newLicense.DetectorType, 10)
		changes = append(changes, models.ChangeLog{
			Field:        "DetectorType",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldLicense.Source != newLicense.Source {
		changes = append(changes, models.ChangeLog{
			Field:        "Source",
			OldValue:     &oldLicense.Source,
			UpdatedValue: &newLicense.Source,
		})
	}
	if oldLicense.SpdxId != newLicense.SpdxId {
		changes = append(changes, models.ChangeLog{
			Field:        "SpdxId",
			OldValue:     &oldLicense.SpdxId,
			UpdatedValue: &newLicense.SpdxId,
		})
	}
	if oldLicense.Risk != newLicense.Risk {
		oldVal := strconv.FormatInt(oldLicense.Risk, 10)
		newVal := strconv.FormatInt(newLicense.Risk, 10)
		changes = append(changes, models.ChangeLog{
			Field:        "Risk",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if oldLicense.Marydone != newLicense.Marydone {
		oldVal := strconv.FormatBool(oldLicense.Marydone)
		newVal := strconv.FormatBool(newLicense.Marydone)
		changes = append(changes, models.ChangeLog{
			Field:        "Marydone",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if (oldLicense.ExternalRef.Data().InternalComment == nil && newLicense.ExternalRef.Data().InternalComment != nil) ||
		(oldLicense.ExternalRef.Data().InternalComment != nil && newLicense.ExternalRef.Data().InternalComment == nil) ||
		((oldLicense.ExternalRef.Data().InternalComment != nil && newLicense.ExternalRef.Data().InternalComment != nil) && (*oldLicense.ExternalRef.Data().InternalComment != *newLicense.ExternalRef.Data().InternalComment)) {
		changes = append(changes, models.ChangeLog{
			Field:        "ExternalRef.InternalComment",
			OldValue:     oldLicense.ExternalRef.Data().InternalComment,
			UpdatedValue: newLicense.ExternalRef.Data().InternalComment,
		})
	}
	if (oldLicense.ExternalRef.Data().LicenseExplanation == nil && newLicense.ExternalRef.Data().LicenseExplanation != nil) ||
		(oldLicense.ExternalRef.Data().LicenseExplanation != nil && newLicense.ExternalRef.Data().LicenseExplanation == nil) ||
		((oldLicense.ExternalRef.Data().LicenseExplanation != nil && newLicense.ExternalRef.Data().LicenseExplanation != nil) && (*oldLicense.ExternalRef.Data().LicenseExplanation != *newLicense.ExternalRef.Data().LicenseExplanation)) {
		changes = append(changes, models.ChangeLog{
			Field:        "ExternalRef.LicenseExplanation",
			OldValue:     oldLicense.ExternalRef.Data().LicenseExplanation,
			UpdatedValue: newLicense.ExternalRef.Data().LicenseExplanation,
		})
	}
	if (oldLicense.ExternalRef.Data().LicenseSuffix == nil && newLicense.ExternalRef.Data().LicenseSuffix != nil) ||
		(oldLicense.ExternalRef.Data().LicenseSuffix != nil && newLicense.ExternalRef.Data().LicenseSuffix == nil) ||
		((oldLicense.ExternalRef.Data().LicenseSuffix != nil && newLicense.ExternalRef.Data().LicenseSuffix != nil) && (*oldLicense.ExternalRef.Data().LicenseSuffix != *newLicense.ExternalRef.Data().LicenseSuffix)) {
		changes = append(changes, models.ChangeLog{
			Field:        "ExternalRef.LicenseSuffix",
			OldValue:     oldLicense.ExternalRef.Data().LicenseSuffix,
			UpdatedValue: newLicense.ExternalRef.Data().LicenseSuffix,
		})
	}
	if (oldLicense.ExternalRef.Data().LicenseVersion == nil && newLicense.ExternalRef.Data().LicenseVersion != nil) ||
		(oldLicense.ExternalRef.Data().LicenseVersion != nil && newLicense.ExternalRef.Data().LicenseVersion == nil) ||
		((oldLicense.ExternalRef.Data().LicenseVersion != nil && newLicense.ExternalRef.Data().LicenseVersion != nil) && (*oldLicense.ExternalRef.Data().LicenseVersion != *newLicense.ExternalRef.Data().LicenseVersion)) {
		changes = append(changes, models.ChangeLog{
			Field:        "ExternalRef.LicenseVersion",
			OldValue:     oldLicense.ExternalRef.Data().LicenseVersion,
			UpdatedValue: newLicense.ExternalRef.Data().LicenseVersion,
		})
	}

	if len(changes) != 0 {
		var user models.User
		if err := tx.Where(models.User{Username: username}).First(&user).Error; err != nil {
			return err
		}

		audit := models.Audit{
			UserId:     user.Id,
			TypeId:     newLicense.Id,
			Timestamp:  time.Now(),
			Type:       "license",
			ChangeLogs: changes,
		}

		if err := tx.Create(&audit).Error; err != nil {
			return err
		}
	}

	return nil
}

// SearchInLicense Search for license data based on user-provided search criteria.
//
//	@Summary		Search licenses
//	@Description	Search licenses on different filters and algorithms
//	@Id				SearchInLicense
//	@Tags			Licenses
//	@Accept			json
//	@Produce		json
//	@Param			search	body		models.SearchLicense	true	"Search criteria"
//	@Success		200		{object}	models.LicenseResponse	"Licenses matched"
//	@Failure		400		{object}	models.LicenseError		"Invalid request"
//	@Failure		404		{object}	models.LicenseError		"Search algorithm doesn't exist"
//	@Router			/search [post]
func SearchInLicense(c *gin.Context) {
	var input models.SearchLicense

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

	var license []models.LicenseDB
	query := db.DB.Model(&license)

	if input.Search == "fuzzy" {
		query = query.Where(fmt.Sprintf("%s ILIKE ?", input.Field), fmt.Sprintf("%%%s%%", input.SearchTerm))
	} else if input.Search == "" || input.Search == "full_text_search" {
		query = query.Where(input.Field+" @@ plainto_tsquery(?)", input.SearchTerm)
	} else {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   "search algorithm doesn't exist",
			Error:     "search algorithm with such name doesn't exists",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}
	err := query.Find(&license).Error
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Query failed because of error",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	res := models.LicenseResponse{
		Data:   license,
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: len(license),
		},
	}
	c.JSON(http.StatusOK, res)
}
