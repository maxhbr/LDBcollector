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
	"io"
	"net/http"
	"path/filepath"
	"reflect"
	"strconv"
	"strings"
	"time"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/gin-gonic/gin"
	"github.com/gin-gonic/gin/binding"
	"github.com/go-playground/validator/v10"

	"gorm.io/gorm"
	"gorm.io/gorm/clause"
)

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
//	@Param			sort_by			query		string					false	"Sort by field"			Enums(spdx_id, shortname, fullname)	default(shortname)
//	@Param			order_by		query		string					false	"Asc or desc ordering"	Enums(asc, desc)					default(asc)
//	@Success		200				{object}	models.LicenseResponse	"Filtered licenses"
//	@Failure		400				{object}	models.LicenseError		"Invalid value"
//	@Security		ApiKeyAuth || {}
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

	var licenses []models.LicenseDB
	query := db.DB.Model(&licenses)

	if active != "" {
		parsedActive, err := strconv.ParseBool(active)
		if err != nil {
			parsedActive = false
		}
		query = query.Where(models.LicenseDB{Active: &parsedActive})
	}

	if fsffree != "" {
		parsedFsffree, err := strconv.ParseBool(fsffree)
		if err != nil {
			parsedFsffree = false
		}
		query = query.Where(models.LicenseDB{FSFfree: &parsedFsffree})
	}

	if OSIapproved != "" {
		parsedOsiApproved, err := strconv.ParseBool(OSIapproved)
		if err != nil {
			parsedOsiApproved = false
		}
		query = query.Where(models.LicenseDB{OSIapproved: &parsedOsiApproved})
	}

	if copyleft != "" {
		parsedCopyleft, err := strconv.ParseBool(copyleft)
		if err != nil {
			parsedCopyleft = false
		}
		query = query.Where(models.LicenseDB{Copyleft: &parsedCopyleft})
	}

	if SpdxId != "" {
		query = query.Where(models.LicenseDB{SpdxId: &SpdxId})
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
		query = query.Where(models.LicenseDB{DetectorType: &parsedDetectorType})
	}

	if GPLv2compatible != "" {
		parsedGPLv2compatible, err := strconv.ParseBool(GPLv2compatible)
		if err != nil {
			parsedGPLv2compatible = false
		}
		query = query.Where(models.LicenseDB{GPLv2compatible: &parsedGPLv2compatible})
	}

	if GPLv3compatible != "" {
		parsedGPLv3compatible, err := strconv.ParseBool(GPLv3compatible)
		if err != nil {
			parsedGPLv3compatible = false
		}
		query = query.Where(models.LicenseDB{GPLv3compatible: &parsedGPLv3compatible})
	}

	if marydone != "" {
		parsedMarydone, err := strconv.ParseBool(marydone)
		if err != nil {
			parsedMarydone = false
		}
		query = query.Where(models.LicenseDB{Marydone: &parsedMarydone})
	}

	for externalRefKey, externalRefValue := range externalRefData {
		query = query.Where(fmt.Sprintf("external_ref->>'%s' = ?", externalRefKey), externalRefValue)
	}

	sortBy := c.Query("sort_by")
	orderBy := c.Query("order_by")
	queryOrderString := ""
	if sortBy != "" && (sortBy == "spdx_id" || sortBy == "shortname" || sortBy == "fullname") {
		queryOrderString += "rf_" + sortBy
	} else {
		queryOrderString += "rf_shortname"
	}

	if orderBy != "" && orderBy == "desc" {
		queryOrderString += " desc"
	}

	query.Order(queryOrderString)

	_ = utils.PreparePaginateResponse(c, query, &models.LicenseResponse{})

	if err := query.Find(&licenses).Error; err != nil {
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

	res := models.LicenseResponse{
		Data:   licenses,
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: len(licenses),
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
//	@Security		ApiKeyAuth || {}
//	@Router			/licenses/{shortname} [get]
func GetLicense(c *gin.Context) {
	var license models.LicenseDB

	queryParam := c.Param("shortname")
	if queryParam == "" {
		return
	}

	err := db.DB.Where(models.LicenseDB{Shortname: &queryParam}).First(&license).Error

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
//	@Param			license	body		models.LicenseDB		true	"New license to be created"
//	@Success		201		{object}	models.LicenseResponse	"New license created successfully"
//	@Failure		400		{object}	models.LicenseError		"Invalid request body"
//	@Failure		409		{object}	models.LicenseError		"License with same shortname already exists"
//	@Failure		500		{object}	models.LicenseError		"Failed to create license"
//	@Security		ApiKeyAuth
//	@Router			/licenses [post]
func CreateLicense(c *gin.Context) {
	var input models.LicenseDB

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

	validate := validator.New(validator.WithRequiredStructEnabled())
	if err := validate.Struct(&input); err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "can not create license with these field values",
			Error:     fmt.Sprintf("field '%s' failed validation: %s\n", err.(validator.ValidationErrors)[0].Field(), err.(validator.ValidationErrors)[0].Tag()),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	result := db.DB.
		Where(&models.LicenseDB{Shortname: input.Shortname}).
		FirstOrCreate(&input)
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
	if result.RowsAffected == 0 {
		er := models.LicenseError{
			Status:    http.StatusConflict,
			Message:   "can not create license with same shortname",
			Error:     fmt.Sprintf("Error: License with shortname '%s' already exists", *input.Shortname),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusConflict, er)
		return
	}
	res := models.LicenseResponse{
		Data:   []models.LicenseDB{input},
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
//	@Param			shortname	path		string							true	"Shortname of the license to be updated"
//	@Param			license		body		models.LicenseUpdateJSONSchema	true	"Update license body (requires only the fields to be updated)"
//	@Success		200			{object}	models.LicenseResponse			"License updated successfully"
//	@Failure		400			{object}	models.LicenseError				"Invalid license body"
//	@Failure		404			{object}	models.LicenseError				"License with shortname not found"
//	@Failure		409			{object}	models.LicenseError				"License with same shortname already exists"
//	@Failure		500			{object}	models.LicenseError				"Failed to update license"
//	@Security		ApiKeyAuth
//	@Router			/licenses/{shortname} [patch]
func UpdateLicense(c *gin.Context) {
	_ = db.DB.Transaction(func(tx *gorm.DB) error {
		var updates models.LicenseUpdateJSONSchema
		var externalRefsPayload models.UpdateExternalRefsJSONPayload
		var oldLicense models.LicenseDB

		username := c.GetString("username")

		shortname := c.Param("shortname")
		if err := tx.Where(models.LicenseDB{Shortname: &shortname}).First(&oldLicense).Error; err != nil {
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

		validate := validator.New()
		if err := validate.Struct(&updates); err != nil {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "can not update license with these field values",
				Error:     fmt.Sprintf("field '%s' failed validation: %s\n", err.(validator.ValidationErrors)[0].Field(), err.(validator.ValidationErrors)[0].Tag()),
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

		if updates.Text != nil && *oldLicense.Text != *updates.Text {
			if !*oldLicense.TextUpdatable {
				er := models.LicenseError{
					Status:    http.StatusBadRequest,
					Message:   "Text is not updatable",
					Error:     "Field `text_updatable` needs to be true to update the text",
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				}
				c.JSON(http.StatusBadRequest, er)
				return errors.New("field `text_updatable` needs to be true to update the text")
			}

			// Update flag to indicate the license text was updated.
			*updates.Flag = 2
		}

		// Overwrite values of existing keys, add new key value pairs and remove keys with null values.
		if err := tx.Model(&models.LicenseDB{}).Where(models.LicenseDB{Id: oldLicense.Id}).UpdateColumn("external_ref", gorm.Expr("jsonb_strip_nulls(COALESCE(external_ref, '{}'::jsonb) || ?)", externalRefsPayload.ExternalRef)).Error; err != nil {
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

		// https://github.com/go-gorm/gorm/issues/3938: BeforeSave hook is called on the struct passed in .Model()
		// Cannot pass empty newLicense struct in .Model() as all fields will be empty and no validation will happen
		newLicense := models.LicenseDB(updates)

		// Update all other fields except external_ref and rf_shortname
		if err := tx.Model(&newLicense).Omit("external_ref", "rf_shortname", "Obligations").Clauses(clause.Returning{}).Where(models.LicenseDB{Id: oldLicense.Id}).Updates(newLicense).Error; err != nil {
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
	var changes []models.ChangeLog

	if *oldLicense.Fullname != *newLicense.Fullname {
		changes = append(changes, models.ChangeLog{
			Field:        "Fullname",
			OldValue:     oldLicense.Fullname,
			UpdatedValue: newLicense.Fullname,
		})
	}
	if *oldLicense.Url != *newLicense.Url {
		changes = append(changes, models.ChangeLog{
			Field:        "Url",
			OldValue:     oldLicense.Url,
			UpdatedValue: newLicense.Url,
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
	if *oldLicense.Active != *newLicense.Active {
		oldVal := strconv.FormatBool(*oldLicense.Active)
		newVal := strconv.FormatBool(*newLicense.Active)
		changes = append(changes, models.ChangeLog{
			Field:        "Active",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if *oldLicense.Copyleft != *newLicense.Copyleft {
		oldVal := strconv.FormatBool(*oldLicense.Copyleft)
		newVal := strconv.FormatBool(*newLicense.Copyleft)
		changes = append(changes, models.ChangeLog{
			Field:        "Copyleft",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if *oldLicense.FSFfree != *newLicense.FSFfree {
		oldVal := strconv.FormatBool(*oldLicense.FSFfree)
		newVal := strconv.FormatBool(*newLicense.FSFfree)
		changes = append(changes, models.ChangeLog{
			Field:        "FSFfree",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if *oldLicense.GPLv2compatible != *newLicense.GPLv2compatible {
		oldVal := strconv.FormatBool(*oldLicense.GPLv2compatible)
		newVal := strconv.FormatBool(*newLicense.GPLv2compatible)
		changes = append(changes, models.ChangeLog{
			Field:        "GPLv2compatible",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if *oldLicense.GPLv3compatible != *newLicense.GPLv3compatible {
		oldVal := strconv.FormatBool(*oldLicense.GPLv3compatible)
		newVal := strconv.FormatBool(*newLicense.GPLv3compatible)
		changes = append(changes, models.ChangeLog{
			Field:        "GPLv3compatible",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if *oldLicense.OSIapproved != *newLicense.OSIapproved {
		oldVal := strconv.FormatBool(*oldLicense.OSIapproved)
		newVal := strconv.FormatBool(*newLicense.OSIapproved)
		changes = append(changes, models.ChangeLog{
			Field:        "OSIapproved",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if *oldLicense.Text != *newLicense.Text {
		changes = append(changes, models.ChangeLog{
			Field:        "Text",
			OldValue:     oldLicense.Text,
			UpdatedValue: newLicense.Text,
		})
	}
	if *oldLicense.TextUpdatable != *newLicense.TextUpdatable {
		oldVal := strconv.FormatBool(*oldLicense.TextUpdatable)
		newVal := strconv.FormatBool(*newLicense.TextUpdatable)
		changes = append(changes, models.ChangeLog{
			Field:        "TextUpdatable",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if *oldLicense.Fedora != *newLicense.Fedora {
		changes = append(changes, models.ChangeLog{
			Field:        "Fedora",
			OldValue:     oldLicense.Fedora,
			UpdatedValue: newLicense.Fedora,
		})
	}
	if *oldLicense.Flag != *newLicense.Flag {
		oldVal := strconv.FormatInt(*oldLicense.Flag, 10)
		newVal := strconv.FormatInt(*newLicense.Flag, 10)
		changes = append(changes, models.ChangeLog{
			Field:        "Flag",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if *oldLicense.Notes != *newLicense.Notes {
		changes = append(changes, models.ChangeLog{
			Field:        "Notes",
			OldValue:     oldLicense.Notes,
			UpdatedValue: newLicense.Notes,
		})
	}
	if *oldLicense.DetectorType != *newLicense.DetectorType {
		oldVal := strconv.FormatInt(*oldLicense.DetectorType, 10)
		newVal := strconv.FormatInt(*newLicense.DetectorType, 10)
		changes = append(changes, models.ChangeLog{
			Field:        "DetectorType",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if *oldLicense.Source != *newLicense.Source {
		changes = append(changes, models.ChangeLog{
			Field:        "Source",
			OldValue:     oldLicense.Source,
			UpdatedValue: newLicense.Source,
		})
	}
	if *oldLicense.SpdxId != *newLicense.SpdxId {
		changes = append(changes, models.ChangeLog{
			Field:        "SpdxId",
			OldValue:     oldLicense.SpdxId,
			UpdatedValue: newLicense.SpdxId,
		})
	}
	if *oldLicense.Risk != *newLicense.Risk {
		oldVal := strconv.FormatInt(*oldLicense.Risk, 10)
		newVal := strconv.FormatInt(*newLicense.Risk, 10)
		changes = append(changes, models.ChangeLog{
			Field:        "Risk",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}
	if *oldLicense.Marydone != *newLicense.Marydone {
		oldVal := strconv.FormatBool(*oldLicense.Marydone)
		newVal := strconv.FormatBool(*newLicense.Marydone)
		changes = append(changes, models.ChangeLog{
			Field:        "Marydone",
			OldValue:     &oldVal,
			UpdatedValue: &newVal,
		})
	}

	oldLicenseExternalRef := oldLicense.ExternalRef.Data()
	oldExternalRefVal := reflect.ValueOf(oldLicenseExternalRef)
	typesOf := oldExternalRefVal.Type()

	newLicenseExternalRef := newLicense.ExternalRef.Data()
	newExternalRefVal := reflect.ValueOf(newLicenseExternalRef)

	for i := 0; i < oldExternalRefVal.NumField(); i++ {
		fieldName := typesOf.Field(i).Name

		switch typesOf.Field(i).Type.String() {
		case "*boolean":
			oldFieldPtr, _ := oldExternalRefVal.Field(i).Interface().(*bool)
			newFieldPtr, _ := newExternalRefVal.Field(i).Interface().(*bool)
			if (oldFieldPtr == nil && newFieldPtr != nil) || (oldFieldPtr != nil && newFieldPtr == nil) ||
				((oldFieldPtr != nil && newFieldPtr != nil) && (*oldFieldPtr != *newFieldPtr)) {
				var oldVal, newVal *string
				oldVal, newVal = nil, nil

				if oldFieldPtr != nil {
					_oldVal := fmt.Sprintf("%t", *oldFieldPtr)
					oldVal = &_oldVal
				}

				if newFieldPtr != nil {
					_newVal := fmt.Sprintf("%t", *newFieldPtr)
					newVal = &_newVal
				}

				changes = append(changes, models.ChangeLog{
					Field:        fmt.Sprintf("ExternalRef.%s", fieldName),
					OldValue:     oldVal,
					UpdatedValue: newVal,
				})
			}
		case "*string":
			oldFieldPtr, _ := oldExternalRefVal.Field(i).Interface().(*string)
			newFieldPtr, _ := newExternalRefVal.Field(i).Interface().(*string)
			if (oldFieldPtr == nil && newFieldPtr != nil) || (oldFieldPtr != nil && newFieldPtr == nil) ||
				((oldFieldPtr != nil && newFieldPtr != nil) && (*oldFieldPtr != *newFieldPtr)) {
				changes = append(changes, models.ChangeLog{
					Field:        fmt.Sprintf("ExternalRef.%s", fieldName),
					OldValue:     oldFieldPtr,
					UpdatedValue: newFieldPtr,
				})
			}
		case "*int":
			oldFieldPtr, _ := oldExternalRefVal.Field(i).Interface().(*int)
			newFieldPtr, _ := newExternalRefVal.Field(i).Interface().(*int)
			if (oldFieldPtr == nil && newFieldPtr != nil) || (oldFieldPtr != nil && newFieldPtr == nil) ||
				((oldFieldPtr != nil && newFieldPtr != nil) && (*oldFieldPtr != *newFieldPtr)) {
				var oldVal, newVal *string
				oldVal, newVal = nil, nil

				if oldFieldPtr != nil {
					_oldVal := fmt.Sprintf("%d", *oldFieldPtr)
					oldVal = &_oldVal
				}

				if newFieldPtr != nil {
					_newVal := fmt.Sprintf("%d", *newFieldPtr)
					newVal = &_newVal
				}

				changes = append(changes, models.ChangeLog{
					Field:        fmt.Sprintf("ExternalRef.%s", fieldName),
					OldValue:     oldVal,
					UpdatedValue: newVal,
				})
			}
		}
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
//	@Security		ApiKeyAuth || {}
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

	input.Field = "rf_" + input.Field

	var license []models.LicenseDB
	query := db.DB.Model(&license)

	if !db.DB.Migrator().HasColumn(&models.LicenseDB{}, input.Field) {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("invalid field name '%s'", input.Field),
			Error:     "field does not exist in the database",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	if input.Search == "fuzzy" {
		query = query.Where(fmt.Sprintf("%s ILIKE ?", input.Field),
			fmt.Sprintf("%%%s%%", input.SearchTerm))
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

// ImportLicenses creates new licenses records via a json file.
//
//	@Summary		Import licenses by uploading a json file
//	@Description	Import licenses by uploading a json file
//	@Id				ImportLicenses
//	@Tags			Licenses
//	@Accept			multipart/form-data
//	@Produce		json
//	@Param			file	formData	file	true	"licenses json file list"
//	@Success		200		{object}	models.ImportLicensesResponse{data=[]models.LicenseImportStatus}
//	@Failure		400		{object}	models.LicenseError	"input file must be present"
//	@Failure		500		{object}	models.LicenseError	"Internal server error"
//	@Security		ApiKeyAuth
//	@Router			/licenses/import [post]
func ImportLicenses(c *gin.Context) {
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

	decoder := json.NewDecoder(file)

	var licenses []models.LicenseDB
	if err := decoder.Decode(&licenses); err != nil {
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

	if _, err = file.Seek(0, io.SeekStart); err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "error parsing json",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}
	var externalRefs []models.UpdateExternalRefsJSONPayload
	if err := decoder.Decode(&externalRefs); err != nil {
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

	res := models.ImportLicensesResponse{
		Status: http.StatusOK,
	}

	for i := range licenses {
		_ = db.DB.Transaction(func(tx *gorm.DB) error {
			errMessage, importStatus, oldLicense, newLicense := utils.InsertOrUpdateLicenseOnImport(tx, &licenses[i], &externalRefs[i])

			if importStatus == utils.IMPORT_FAILED {
				erroredLicense := ""
				if licenses[i].Shortname != nil {
					erroredLicense = *licenses[i].Shortname
				}
				res.Data = append(res.Data, models.LicenseError{
					Status:    http.StatusInternalServerError,
					Message:   errMessage,
					Error:     erroredLicense,
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				})
				return errors.New(errMessage)
			} else if importStatus == utils.IMPORT_LICENSE_CREATED {
				res.Data = append(res.Data, models.LicenseImportStatus{
					Data:   models.LicenseId{Id: oldLicense.Id, Shortname: *oldLicense.Shortname},
					Status: http.StatusCreated,
				})
			} else if importStatus == utils.IMPORT_LICENSE_UPDATED {
				if err := addChangelogsForLicenseUpdate(tx, username, newLicense, oldLicense); err != nil {
					res.Data = append(res.Data, models.LicenseError{
						Status:    http.StatusInternalServerError,
						Message:   "Failed to update license",
						Error:     *newLicense.Shortname,
						Path:      c.Request.URL.Path,
						Timestamp: time.Now().Format(time.RFC3339),
					})
					return err
				}
				res.Data = append(res.Data, models.LicenseImportStatus{
					Data:   models.LicenseId{Id: newLicense.Id, Shortname: *newLicense.Shortname},
					Status: http.StatusOK,
				})
			} else if importStatus == utils.IMPORT_LICENSE_UPDATED_EXCEPT_TEXT {
				if err := addChangelogsForLicenseUpdate(tx, username, newLicense, oldLicense); err != nil {
					res.Data = append(res.Data, models.LicenseError{
						Status:    http.StatusInternalServerError,
						Message:   "Failed to update license",
						Error:     *newLicense.Shortname,
						Path:      c.Request.URL.Path,
						Timestamp: time.Now().Format(time.RFC3339),
					})
					return err
				}

				res.Data = append(res.Data, models.LicenseError{
					Status:    http.StatusConflict,
					Message:   errMessage,
					Error:     *newLicense.Shortname,
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				})
				// error is not returned here as it will rollback the transaction
			}

			return nil
		})
	}

	c.JSON(http.StatusOK, res)
}

// ExportLicenses gives users all licenses as a json file.
//
//	@Summary		Export all licenses as a json file
//	@Description	Export all licenses as a json file
//	@Id				ExportLicenses
//	@Tags			Licenses
//	@Produce		json
//	@Success		200	{array}		models.LicenseDB
//	@Failure		500	{object}	models.LicenseError	"Failed to fetch Licenses"
//	@Security		ApiKeyAuth || {}
//	@Router			/licenses/export [get]
func ExportLicenses(c *gin.Context) {
	var licenses []models.LicenseDB
	query := db.DB.Model(&models.LicenseDB{})
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
	fileName := strings.Map(func(r rune) rune {
		if r == '+' || r == ':' {
			return '_'
		}
		return r
	}, fmt.Sprintf("license-export-%s.json", time.Now().Format(time.RFC3339)))

	c.Header("Content-Disposition", fmt.Sprintf("attachment; filename=%s", fileName))
	c.JSON(http.StatusOK, &licenses)
}

// GetAllLicensePreviews retrieves a list of shortnames of all licenses
//
//	@Summary		Get shortnames of all active licenses
//	@Description	Get shortnames of all active licenses from the service
//	@Id				GetAllLicensePreviews
//	@Tags			Licenses
//	@Accept			json
//	@Produce		json
//	@Param			active	query		bool	true	"Active license only"
//	@Success		200		{object}	models.LicensePreviewResponse
//	@Failure		400		{object}	models.LicenseError	"Invalid active value"
//	@Failure		500		{object}	models.LicenseError	"Unable to fetch licenses"
//	@Security		ApiKeyAuth || {}
//	@Router			/licenses/preview [get]
func GetAllLicensePreviews(c *gin.Context) {
	var licenses []models.LicenseDB
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
	query := db.DB.Model(&models.LicenseDB{})
	query.Where("rf_active = ?", parsedActive)

	if err = query.Find(&licenses).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Unable to fetch licenses",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	var res models.LicensePreviewResponse
	for _, lic := range licenses {
		res.Shortnames = append(res.Shortnames, *lic.Shortname)
	}

	res.Status = http.StatusOK

	c.JSON(http.StatusOK, res)
}
