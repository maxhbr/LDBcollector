// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"

	"github.com/fossology/LicenseDb/pkg/auth"
	"github.com/fossology/LicenseDb/pkg/models"
)

// Router Get the gin router with all the routes defined
//
//	@title						laas (License as a Service) API
//	@version					0.0.9
//	@description				Service to host license information for other services to query over REST API.
//
//	@contact.name				FOSSology
//	@contact.url				https://fossology.org
//	@contact.email				fossology@fossology.org
//
//	@license.name				GPL-2.0-only
//	@license.url				https://github.com/fossology/LicenseDb/blob/main/LICENSE
//
//	@host						localhost:8080
//	@BasePath					/api/v1
//
//	@securityDefinitions.basic	BasicAuth
func Router() *gin.Engine {
	// r is a default instance of gin engine
	r := gin.Default()

	// return error for invalid routes
	r.NoRoute(HandleInvalidUrl)

	unAuthorizedv1 := r.Group("/api/v1")
	{
		licenses := unAuthorizedv1.Group("/licenses")
		{
			licenses.GET("", FilterLicense)
			licenses.GET(":shortname", GetLicense)
		}
		search := unAuthorizedv1.Group("/search")
		{
			search.POST("", SearchInLicense)
		}
		obligations := unAuthorizedv1.Group("/obligations")
		{
			obligations.GET("", GetAllObligation)
			obligations.GET(":topic", GetObligation)
		}
	}

	authorizedv1 := r.Group("/api/v1")
	authorizedv1.Use(auth.AuthenticationMiddleware())
	{
		licenses := authorizedv1.Group("/licenses")
		{
			licenses.POST("", CreateLicense)
			licenses.PATCH(":shortname", UpdateLicense)
		}
		users := authorizedv1.Group("/users")
		{
			users.GET("", auth.GetAllUser)
			users.GET(":id", auth.GetUser)
			users.POST("", auth.CreateUser)
		}
		audit := authorizedv1.Group("/audits")
		{
			audit.GET("", GetAllAudit)
			audit.GET(":audit_id", GetAudit)
			audit.GET(":audit_id/changes", GetChangeLogs)
			audit.GET(":audit_id/changes/:id", GetChangeLogbyId)
		}
		obligations := authorizedv1.Group("/obligations")
		{
			obligations.POST("", CreateObligation)
			obligations.PATCH(":topic", UpdateObligation)
			obligations.DELETE(":topic", DeleteObligation)
		}
	}

	// Host the swagger UI at /swagger/index.html
	r.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	return r
}

// The HandleInvalidUrl function returns the error when an invalid url is entered
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
