// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package auth

import (
	"fmt"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/golang-jwt/jwt/v4"
	"golang.org/x/crypto/bcrypt"

	"github.com/gin-gonic/gin"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
)

// CreateUser creates a new user
//
//	@Summary		Create new user
//	@Description	Create a new service user
//	@Id				CreateUser
//	@Tags			Users
//	@Accept			json
//	@Produce		json
//	@Param			user	body		models.UserInput	true	"User to create"
//	@Success		201		{object}	models.UserResponse
//	@Failure		400		{object}	models.LicenseError	"Invalid json body"
//	@Failure		409		{object}	models.LicenseError	"User already exists"
//	@Security		ApiKeyAuth
//	@Router			/users [post]
func CreateUser(c *gin.Context) {
	var input models.UserInput
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

	user := models.User{
		Username:     input.Username,
		Userlevel:    input.Userlevel,
		Userpassword: input.Userpassword,
	}

	err := utils.HashPassword(&user)
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "password hashing failed",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	result := db.DB.Where(models.User{Username: user.Username}).FirstOrCreate(&user)
	if result.Error != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Failed to create the new user",
			Error:     result.Error.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	} else if result.RowsAffected == 0 {
		er := models.LicenseError{
			Status:    http.StatusConflict,
			Message:   "can not create user with same username",
			Error:     fmt.Sprintf("Error: User with username '%s' already exists", user.Username),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusConflict, er)
		return
	}

	res := models.UserResponse{
		Data:   []models.User{user},
		Status: http.StatusCreated,
		Meta: &models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusCreated, res)
}

// GetAllUser retrieves a list of all users from the database.
//
//	@Summary		Get users
//	@Description	Get all service users
//	@Id				GetAllUsers
//	@Tags			Users
//	@Accept			json
//	@Produce		json
//	@Param			page	query		int	false	"Page number"
//	@Param			limit	query		int	false	"Number of records per page"
//	@Success		200		{object}	models.UserResponse
//	@Failure		404		{object}	models.LicenseError	"Users not found"
//	@Security		ApiKeyAuth
//	@Router			/users [get]
func GetAllUser(c *gin.Context) {
	var users []models.User

	query := db.DB.Model(&models.User{})
	_ = utils.PreparePaginateResponse(c, query, &models.UserResponse{})

	if err := query.Find(&users).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   "Users not found",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}
	for i := 0; i < len(users); i++ {
		users[i].Userpassword = nil
	}
	res := models.UserResponse{
		Data:   users,
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: len(users),
		},
	}

	c.JSON(http.StatusOK, res)
}

// GetUser retrieves a user by their user ID from the database.
//
//	@Summary		Get a user
//	@Description	Get a single user by ID
//	@Id				GetUser
//	@Tags			Users
//	@Accept			json
//	@Produce		json
//	@Param			id	path		int	true	"User ID"
//	@Success		200	{object}	models.UserResponse
//	@Failure		400	{object}	models.LicenseError	"Invalid user id"
//	@Failure		404	{object}	models.LicenseError	"User not found"
//	@Security		ApiKeyAuth
//	@Router			/users/{id} [get]
func GetUser(c *gin.Context) {
	var user models.User
	id := c.Param("id")
	parsedId, err := utils.ParseIdToInt(c, id, "user")
	if err != nil {
		return
	}

	if err := db.DB.Where(models.User{Id: parsedId}).First(&user).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   "no user with such user id exists",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}
	user.Userpassword = nil
	res := models.UserResponse{
		Data:   []models.User{user},
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusOK, res)
}

// Login user and get JWT tokens
//
//	@Summary		Login
//	@Description	Login to get JWT token
//	@Id				Login
//	@Tags			Users
//	@Accept			json
//	@Produce		json
//	@Param			user	body		models.UserLogin		true	"Login credentials"
//	@Success		200		{object}	object{token=string}	"JWT token"
//	@Router			/login [post]
func Login(c *gin.Context) {
	var input models.UserLogin
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

	username := input.Username
	password := input.Userpassword

	var user models.User
	result := db.DB.Where(models.User{Username: username}).First(&user)
	if result.Error != nil {
		er := models.LicenseError{
			Status:    http.StatusUnauthorized,
			Message:   "User name not found",
			Error:     "",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}

		c.JSON(http.StatusUnauthorized, er)
		c.Abort()
		return
	}

	err := encryptUserPassword(&user)
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Failed to encrypt user password",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}

		c.JSON(http.StatusInternalServerError, er)
		c.Abort()
		return
	}

	// Check if the password matches
	err = utils.VerifyPassword(password, *user.Userpassword)
	if err != nil {
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

	token, err := generateToken(user)
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Failed to generate token",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}
	c.JSON(http.StatusOK, gin.H{"token": token})
}

// encryptUserPassword checks if the password is already encrypted or not. If
// not, it encrypts the password.
func encryptUserPassword(user *models.User) error {
	_, err := bcrypt.Cost([]byte(*user.Userpassword))
	if err == nil {
		return nil
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(*user.Userpassword), bcrypt.DefaultCost)

	if err != nil {
		return err
	}
	*user.Userpassword = string(hashedPassword)

	db.DB.Model(&user).Updates(user)

	return nil
}

// generateToken generates a JWT token for the user.
func generateToken(user models.User) (string, error) {
	tokenLifespan, err := strconv.Atoi(os.Getenv("TOKEN_HOUR_LIFESPAN"))
	if err != nil {
		return "", err
	}

	claims := jwt.MapClaims{}
	claims["user"] = user
	claims["nbf"] = time.Now().Unix()
	claims["exp"] = time.Now().Add(time.Hour * time.Duration(tokenLifespan)).Unix()
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

	return token.SignedString([]byte(os.Getenv("API_SECRET")))
}
