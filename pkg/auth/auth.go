// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-License-Identifier: GPL-2.0-only

package auth

import (
	"encoding/base64"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/fossology/LicenseDb/pkg/api"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/gin-gonic/gin"
)

func CreateUser(c *gin.Context) {
	var user models.User
	if err := c.ShouldBindJSON(&user); err != nil {
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
	result := api.DB.FirstOrCreate(&user)
	if result.RowsAffected == 0 {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "can not create user with same userid",
			Error:     fmt.Sprintf("Error: License with userid '%s' already exists", user.Userid),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}
	if result.Error != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Failed to create user",
			Error:     result.Error.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}
	res := models.UserResponse{
		Data:   []models.User{user},
		Status: http.StatusCreated,
		Meta: models.Meta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusCreated, res)
}

func GetAllUser(c *gin.Context) {
	var users []models.User
	if err := api.DB.Find(&users).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "can not create user",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
	}
	res := models.UserResponse{
		Data:   users,
		Status: http.StatusOK,
		Meta: models.Meta{
			ResourceCount: len(users),
		},
	}

	c.JSON(http.StatusOK, res)
}

func GetUser(c *gin.Context) {
	var user models.User
	id := c.Param("id")

	if err := api.DB.Where("userid = ?", id).First(&user).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "no user with such user id exists",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
	}
	res := models.UserResponse{
		Data:   []models.User{user},
		Status: http.StatusOK,
		Meta: models.Meta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusOK, res)
}

func AuthenticationMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "Please check your credentials and try again",
				Error:     "no credentials were passed",
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}

			c.JSON(http.StatusUnauthorized, er)
			c.Abort()
			return
		}

		decodedAuth, err := base64.StdEncoding.DecodeString(strings.TrimPrefix(authHeader, "Basic "))
		if err != nil {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "Please check your credentials and try again",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}

			c.JSON(http.StatusBadRequest, er)
			c.Abort()
			return
		}

		auth := strings.SplitN(string(decodedAuth), ":", 2)
		if len(auth) != 2 {
			c.AbortWithStatus(http.StatusBadRequest)
			return
		}

		username := auth[0]
		password := auth[1]

		var user models.User

		err = api.DB.Where("username = ?", username).First(&user).Error
		if err != nil {
			er := models.LicenseError{
				Status:    http.StatusUnauthorized,
				Message:   "User name not found",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}

			c.JSON(http.StatusUnauthorized, er)
			c.Abort()
			return
		}

		// Check if the password matches
		if user.Userpassword != password {
			er := models.LicenseError{
				Status:    http.StatusUnauthorized,
				Message:   "Incorrect password",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}

			c.JSON(http.StatusUnauthorized, er)
			c.Abort()
			return
		}

		c.Next()
	}
}
