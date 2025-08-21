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
	"io"
	"net/http"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/fossology/LicenseDb/pkg/validations"
	"github.com/gin-gonic/gin"
	"github.com/go-playground/validator/v10"

	"gorm.io/gorm"
)

// FilterLicense Get licenses from service based on different filters.
//
//	@Summary		Filter licenses
//	@Description	Filter licenses based on different parameters
//	@Id				FilterLicense
//	@Tags			Licenses
//	@Accept			json
//	@Produce		json
//	@Param			spdxid		query		string					false	"SPDX ID of the license"
//	@Param			active		query		bool					false	"Active license only"
//	@Param			osiapproved	query		bool					false	"OSI Approved flag status of license"
//	@Param			copyleft	query		bool					false	"Copyleft flag status of license"
//	@Param			page		query		int						false	"Page number"
//	@Param			limit		query		int						false	"Limit of responses per page"
//	@Param			externalRef	query		string					false	"External reference parameters"
//	@Param			sort_by		query		string					false	"Sort by field"			Enums(spdx_id, shortname, fullname)	default(shortname)
//	@Param			order_by	query		string					false	"Asc or desc ordering"	Enums(asc, desc)					default(asc)
//	@Success		200			{object}	models.LicenseResponse	"Filtered licenses"
//	@Failure		400			{object}	models.LicenseError		"Invalid value"
//	@Security		ApiKeyAuth || {}
//	@Router			/licenses [get]
func FilterLicense(c *gin.Context) {
	SpdxId := c.Query("spdxid")
	active := c.Query("active")
	OSIapproved := c.Query("osiapproved")
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
	query := db.DB.Model(&licenses).Preload("User").Preload("Obligations")

	if active != "" {
		parsedActive, err := strconv.ParseBool(active)
		if err != nil {
			parsedActive = false
		}
		query = query.Where(models.LicenseDB{Active: &parsedActive})
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

	var licensedtos []models.LicenseResponseDTO

	for _, l := range licenses {
		licensedtos = append(licensedtos, l.ConvertToLicenseResponseDTO())
	}

	res := models.LicenseResponse{
		Data:   licensedtos,
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

	err := db.DB.Where(models.LicenseDB{Shortname: &queryParam}).Preload("User").First(&license).Error
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
		Data:   []models.LicenseResponseDTO{license.ConvertToLicenseResponseDTO()},
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
//	@Param			license	body		models.LicenseCreateDTO	true	"New license to be created"
//	@Success		201		{object}	models.LicenseResponse	"New license created successfully"
//	@Failure		400		{object}	models.LicenseError		"Invalid request body"
//	@Failure		409		{object}	models.LicenseError		"License with same shortname already exists"
//	@Failure		500		{object}	models.LicenseError		"Failed to create license"
//	@Security		ApiKeyAuth
//	@Router			/licenses [post]
func CreateLicense(c *gin.Context) {
	var input models.LicenseCreateDTO

	userId := c.MustGet("userId").(int64)

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

	if err := validations.Validate.Struct(&input); err != nil {
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

	lic, err := input.ConvertToLicenseDB()
	if err != nil {
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
	lic.UserId = userId

	_ = db.DB.Transaction(func(tx *gorm.DB) error {
		result := tx.
			Where(&models.LicenseDB{Shortname: lic.Shortname}).
			FirstOrCreate(&lic)

		if result.Error != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Failed to create license",
				Error:     result.Error.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return result.Error
		}
		if result.RowsAffected == 0 {
			er := models.LicenseError{
				Status:    http.StatusConflict,
				Message:   "can not create license with same shortname",
				Error:     fmt.Sprintf("Error: License with shortname '%s' already exists", *lic.Shortname),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusConflict, er)
			return errors.New("can not create license with same shortname")
		}

		if err := tx.Preload("User").First(&lic).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Failed to create license",
				Error:     result.Error.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return result.Error
		}

		if err := utils.AddChangelogsForLicense(tx, userId, &lic, &models.LicenseDB{}); err != nil {
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
			Data:   []models.LicenseResponseDTO{lic.ConvertToLicenseResponseDTO()},
			Status: http.StatusCreated,
			Meta: &models.PaginationMeta{
				ResourceCount: 1,
			},
		}

		c.JSON(http.StatusCreated, res)

		return nil
	})
}

// UpdateLicense Update license with given shortname and create audit and changelog entries.
//
//	@Summary		Update a license
//	@Description	Update a license in the service
//	@Id				UpdateLicense
//	@Tags			Licenses
//	@Accept			json
//	@Produce		json
//	@Param			shortname	path		string					true	"Shortname of the license to be updated"
//	@Param			license		body		models.LicenseUpdateDTO	true	"Update license body (requires only the fields to be updated)"
//	@Success		200			{object}	models.LicenseResponse	"License updated successfully"
//	@Failure		400			{object}	models.LicenseError		"Invalid license body"
//	@Failure		404			{object}	models.LicenseError		"License with shortname not found"
//	@Failure		409			{object}	models.LicenseError		"License with same shortname already exists"
//	@Failure		500			{object}	models.LicenseError		"Failed to update license"
//	@Security		ApiKeyAuth
//	@Router			/licenses/{shortname} [patch]
func UpdateLicense(c *gin.Context) {
	_ = db.DB.Transaction(func(tx *gorm.DB) error {
		var updates models.LicenseUpdateDTO
		var oldLicense models.LicenseDB

		userId := c.MustGet("userId").(int64)

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

		if err := validations.Validate.Struct(&updates); err != nil {
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

		newLicense := updates.ConvertToLicenseDB()
		if newLicense.Text != nil && *oldLicense.Text != *newLicense.Text {
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
			textSetBy := int64(models.TEXT_SET_VIA_MANUAL_UPDATE)
			newLicense.TextSetBy = &textSetBy
		}

		// Overwrite values of existing keys, add new key value pairs and remove keys with null values.
		if err := tx.Model(&models.LicenseDB{}).Where(models.LicenseDB{Id: oldLicense.Id}).UpdateColumn("external_ref", gorm.Expr("jsonb_strip_nulls(COALESCE(external_ref, '{}'::jsonb) || ?)", updates.ExternalRef)).Error; err != nil {
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

		if err := tx.Omit("ExternalRef", "Obligations", "User", "Shortname").Where(models.LicenseDB{Id: oldLicense.Id}).Updates(&newLicense).Error; err != nil {
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

		if err := tx.Preload("User").Preload("Obligations").Where(models.LicenseDB{Id: oldLicense.Id}).First(&newLicense).Error; err != nil {
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

		if err := utils.AddChangelogsForLicense(tx, userId, &newLicense, &oldLicense); err != nil {
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
			Data:   []models.LicenseResponseDTO{newLicense.ConvertToLicenseResponseDTO()},
			Status: http.StatusOK,
			Meta: &models.PaginationMeta{
				ResourceCount: 1,
			},
		}

		c.JSON(http.StatusOK, res)

		return nil
	})
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

	var licenses []models.LicenseDB
	query := db.DB.Model(&licenses)

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
	err := query.Preload("User").Preload("Obligations").Find(&licenses).Error
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

	licensedtos := []models.LicenseResponseDTO{}

	for _, l := range licenses {
		licensedtos = append(licensedtos, l.ConvertToLicenseResponseDTO())
	}

	res := models.LicenseResponse{
		Data:   licensedtos,
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: len(licenses),
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

	decoder := json.NewDecoder(file)

	var licenses []models.LicenseCreateDTO
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
		lic, err := licenses[i].ConvertToLicenseDB()
		if err != nil {
			res.Data = append(res.Data, models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   err.Error(),
				Error:     licenses[i].Shortname,
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			})
		}
		errMessage, importStatus := utils.InsertOrUpdateLicenseOnImport(&lic, &externalRefs[i], userId)

		if importStatus == utils.IMPORT_FAILED {
			res.Data = append(res.Data, models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   errMessage,
				Error:     licenses[i].Shortname,
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			})
		} else if importStatus == utils.IMPORT_LICENSE_CREATED {
			res.Data = append(res.Data, models.LicenseImportStatus{
				Shortname: licenses[i].Shortname,
				Status:    http.StatusCreated,
			})
		} else if importStatus == utils.IMPORT_LICENSE_UPDATED {
			res.Data = append(res.Data, models.LicenseImportStatus{
				Shortname: licenses[i].Shortname,
				Status:    http.StatusOK,
			})
		} else if importStatus == utils.IMPORT_LICENSE_UPDATED_EXCEPT_TEXT {
			res.Data = append(res.Data, models.LicenseError{
				Status:    http.StatusConflict,
				Message:   errMessage,
				Error:     licenses[i].Shortname,
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			})
			// error is not returned here as it will rollback the transaction
		}
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
//	@Success		200	{array}		models.LicenseResponseDTO
//	@Failure		500	{object}	models.LicenseError	"Failed to fetch Licenses"
//	@Security		ApiKeyAuth || {}
//	@Router			/licenses/export [get]
func ExportLicenses(c *gin.Context) {
	var licenses []models.LicenseDB
	query := db.DB.Model(&models.LicenseDB{}).Preload("User").Preload("Obligations")
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

	var licensedtos []models.LicenseResponseDTO

	for _, l := range licenses {
		licensedtos = append(licensedtos, l.ConvertToLicenseResponseDTO())
	}

	fileName := strings.Map(func(r rune) rune {
		if r == '+' || r == ':' {
			return '_'
		}
		return r
	}, fmt.Sprintf("license-export-%s.json", time.Now().Format(time.RFC3339)))

	c.Header("Content-Disposition", fmt.Sprintf("attachment; filename=%s", fileName))
	c.JSON(http.StatusOK, &licensedtos)
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

// getSimilarLicense finds similar license texts using trigram similarity
//
//	@Summary		Find similar license texts
//	@Description	Compares input license text with existing ones using pg_trgm similarity
//	@ID				getSimilarLicense
//	@Tags			Licenses
//	@Accept			json
//	@Produce		json
//	@Param			license	body		models.SimilarityRequest	true	"Input license text to compare"
//	@Success		200		{object}	[]models.SimilarLicense		"List of similar licenses"
//	@Failure		400		{object}	models.LicenseError			"Invalid request or query failed"
//	@Failure		500		{object}	models.LicenseError			"Internal server error"
//	@Security		ApiKeyAuth
//	@Router			/licenses/similarity [post]
func getSimilarLicenses(c *gin.Context) {
	var req models.SimilarityRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Text field is required",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		})
		return
	}
	var results []models.SimilarLicense
	utils.SetSimilarityThreshold()
	query := `
		SELECT rf_id, rf_shortname, rf_text, similarity(rf_text, ?) AS similarity
		FROM license_dbs
		WHERE rf_text % ?
		ORDER BY similarity DESC
	`
	if err := db.DB.Raw(query, req.Text, req.Text).Scan(&results).Error; err != nil {
		c.JSON(http.StatusBadRequest, models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "Database query failed",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		})
		return
	}
	c.JSON(http.StatusOK, models.ApiResponse[[]models.SimilarLicense]{
		Status: http.StatusOK,
		Data:   results,
		Meta: &models.PaginationMeta{
			ResourceCount: len(results),
		},
	})
}
