// SPDX-FileCopyrightText: 2025 Siemens AG
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"log"
	"net/http"
	"time"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/gin-gonic/gin"
)

// GetDashboardData fetches data to be displayed on the dashboard
//
//	@Summary		Fetches data to be displayed on the dashboard
//	@Description	Fetches data to be displayed on the dashboard
//	@Id				GetDashboardData
//	@Tags			Dashboard
//	@Accept			json
//	@Produce		json
//	@Success		200	{object}	models.DashboardResponse
//	@Failure		500	{object}	models.LicenseError	"Something went wrong"
//	@Security		ApiKeyAuth || {}
//	@Router			/dashboard [get]
func GetDashboardData(c *gin.Context) {
	var licensesCount, obligationsCount, usersCount, licenseChangesSinceLastMonth int64
	var licenseFrequency []models.RiskLicenseCount
	var categoryFrequency []models.CategoryObligationCount

	var active = true
	if err := db.DB.Model(&models.LicenseDB{}).Where(&models.LicenseDB{Active: &active}).Count(&licensesCount).Error; err != nil {
		log.Printf("\033[31mError: error fetching licenses count: %s\033[0m", err.Error())
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "something went wrong",
			Error:     "error fetching licenses count",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	if err := db.DB.Model(&models.Obligation{}).Where(&models.Obligation{Active: &active}).Count(&obligationsCount).Error; err != nil {
		log.Printf("\033[31mError: error fetching obligations count: %s\033[0m", err.Error())
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "something went wrong",
			Error:     "error fetching obligations count",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	if err := db.DB.Model(&models.User{}).Where(&models.User{Active: &active}).Count(&usersCount).Error; err != nil {
		log.Printf("\033[31mError: error fetching users count: %s\033[0m", err.Error())
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "something went wrong",
			Error:     "error fetching users count",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	now := time.Now()
	startOfMonth := time.Date(now.Year(), now.Month(), 1, 0, 0, 0, 0, time.UTC)
	iso8601StartOfMonth := startOfMonth.Format(time.RFC3339)
	if err := db.DB.Model(&models.Audit{}).Where("timestamp > ? AND type='license'", iso8601StartOfMonth).Count(&licenseChangesSinceLastMonth).Error; err != nil {
		log.Printf("\033[31mError: error fetching audits count: %s\033[0m", err.Error())
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "something went wrong",
			Error:     "error fetching audits count",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	if err := db.DB.Model(&models.LicenseDB{}).Select("rf_risk as risk, count(*) as count").Group("rf_risk").Scan(&licenseFrequency).Error; err != nil {
		log.Printf("\033[31mError: error fetching risk license frequencies: %s\033[0m", err.Error())
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "something went wrong",
			Error:     "error fetching risk liicense frequencies",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	if err := db.DB.Model(&models.Obligation{}).Select("category, count(*) as count").Group("category").Scan(&categoryFrequency).Error; err != nil {
		log.Printf("\033[31mError: error fetching category obligation frequencies: %s\033[0m", err.Error())
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "something went wrong",
			Error:     "error fetching category obligation frequencies",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	res := models.DashboardResponse{
		Data: models.Dashboard{
			LicensesCount:                licensesCount,
			ObligationsCount:             obligationsCount,
			LicenseChangesSinceLastMonth: licenseChangesSinceLastMonth,
			UsersCount:                   usersCount,
			RiskLicenseFrequency:         licenseFrequency,
			CategoryObligationFrequency:  categoryFrequency,
		},
		Status: http.StatusOK,
	}

	c.JSON(http.StatusOK, res)
}
