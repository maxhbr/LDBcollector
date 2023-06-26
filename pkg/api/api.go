// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"fmt"
	"net/http"
	"time"

	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

var DB *gorm.DB

func HandleInvalidUrl(c *gin.Context) {

	er := models.LicenseError{
		Status:    http.StatusNotFound,
		Message:   "No such path exists please check URL",
		Error:     "invalid path",
		Path:      c.Request.URL.Path,
		Timestamp: time.Now().Format(time.RFC3339),
	}
	c.JSON(http.StatusNotFound, er)
}
func GetAllLicense(c *gin.Context) {
	var licenses []models.LicenseDB

	err := DB.Find(&licenses).Error
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
		Meta: models.Meta{
			ResourceCount: len(licenses),
		},
	}

	c.JSON(http.StatusOK, res)
}

func GetLicense(c *gin.Context) {
	var license models.LicenseDB

	queryParam := c.Param("shortname")
	if queryParam == "" {
		return
	}

	err := DB.Where("shortname = ?", queryParam).First(&license).Error

	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("no license with shortname '%s' exists", queryParam),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	res := models.LicenseResponse{
		Data:   []models.LicenseDB{license},
		Status: http.StatusOK,
		Meta: models.Meta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusOK, res)
}

func CreateLicense(c *gin.Context) {
	var input models.LicenseInput

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

	if input.Active == "" {
		input.Active = "t"
	}
	license := models.LicenseDB(input)

	result := DB.FirstOrCreate(&license)
	if result.RowsAffected == 0 {

		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "can not create license with same shortname",
			Error:     fmt.Sprintf("Error: License with shortname '%s' already exists", input.Shortname),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
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
		Meta: models.Meta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusCreated, res)
}

func UpdateLicense(c *gin.Context) {
	var update models.LicenseDB
	var license models.LicenseDB
	shortname := c.Param("shortname")
	if err := DB.Where("shortname = ?", shortname).First(&license).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("license with shortname '%s' not found", shortname),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}
	if err := c.ShouldBindJSON(&update); err != nil {
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
	if err := DB.Model(&license).Updates(update).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Failed to update license",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}
	res := models.LicenseResponse{
		Data:   []models.LicenseDB{license},
		Status: http.StatusOK,
		Meta: models.Meta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusOK, res)

}

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
	var license []models.LicenseDB
	query := DB.Model(&license)

	if SpdxId == "" && GPLv2compatible == "" && GPLv3compatible == "" && DetectorType == "" && marydone == "" && active == "" && fsffree == "" && OSIapproved == "" && copyleft == "" {
		GetAllLicense(c)
		return
	}
	if active != "" {
		query = query.Where("active=?", active)
	}

	if fsffree != "" {
		query = query.Where("fs_ffree=?", fsffree)
	}

	if OSIapproved != "" {
		query = query.Where("os_iapproved=?", OSIapproved)
	}

	if copyleft != "" {
		query = query.Where("copyleft=?", copyleft)
	}

	if SpdxId != "" {
		query = query.Where("spdx_id=?", SpdxId)
	}

	if DetectorType != "" {
		query = query.Where("detector_type=?", DetectorType)
	}

	if GPLv2compatible != "" {
		query = query.Where("gp_lv2compatible=?", GPLv2compatible)
	}

	if GPLv3compatible != "" {
		query = query.Where("gp_lv3compatible=?", GPLv3compatible)
	}

	if marydone != "" {
		query = query.Where("marydone=?", marydone)
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
	query.Find(&license)

	res := models.LicenseResponse{
		Data:   license,
		Status: http.StatusOK,
		Meta: models.Meta{
			ResourceCount: len(license),
		},
	}
	c.JSON(http.StatusOK, res)

}

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
	query := DB.Model(&license)

	if input.SearchType == "fuzzy" {
		query = query.Where(fmt.Sprintf("%s ILIKE ?", input.Field), fmt.Sprintf("%%%s%%", input.SearchTerm))
	} else if input.SearchType == "" || input.SearchType == "full_text_search" {
		query = query.Where(input.Field+" @@ plainto_tsquery(?)", input.SearchTerm)

	} else {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "search algorithm doesn't exist",
			Error:     "search algorithm with such name doesn't exists",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}
	query.Find(&license)

	res := models.LicenseResponse{
		Data:   license,
		Status: http.StatusOK,
		Meta: models.Meta{
			ResourceCount: len(license),
		},
	}
	c.JSON(http.StatusOK, res)

}
