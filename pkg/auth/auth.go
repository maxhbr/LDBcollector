// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
// SPDX-FileCopyrightText: 2024 Dearsh Oberoi <oberoidearsh@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package auth

import (
	"context"
	"errors"
	"fmt"
	"html"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/go-playground/validator/v10"
	"github.com/google/uuid"
	"github.com/lestrrat-go/jwx/v3/jwa"
	"github.com/lestrrat-go/jwx/v3/jwk"
	"github.com/lestrrat-go/jwx/v3/jws"
	"github.com/lestrrat-go/jwx/v3/jwt"
	"go.uber.org/zap"
	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"

	"github.com/gin-gonic/gin"

	"github.com/fossology/LicenseDb/pkg/db"
	logger "github.com/fossology/LicenseDb/pkg/log"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/fossology/LicenseDb/pkg/validations"
)

var Jwks *jwk.Cache

// CreateUser creates a new user
//
//	@Summary		Create new user
//	@Description	Create a new service user
//	@Id				CreateUser
//	@Tags			Users
//	@Accept			json
//	@Produce		json
//	@Param			user	body		models.UserCreate	true	"User to create"
//	@Success		201		{object}	models.UserResponse
//	@Failure		400		{object}	models.LicenseError	"Invalid json body"
//	@Failure		409		{object}	models.LicenseError	"User already exists"
//	@Security		ApiKeyAuth
//	@Router			/users [post]
func CreateUser(c *gin.Context) {
	var input models.UserCreate
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
			Message:   "can not create user with these field values",
			Error:     fmt.Sprintf("field '%s' failed validation: %s\n", err.(validator.ValidationErrors)[0].Field(), err.(validator.ValidationErrors)[0].Tag()),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return
	}

	_ = db.DB.Transaction(func(tx *gorm.DB) error {

		userId := c.MustGet("userId").(uuid.UUID)
		user := models.User(input)
		*user.UserName = html.EscapeString(strings.TrimSpace(*user.UserName))
		*user.DisplayName = html.EscapeString(strings.TrimSpace(*user.DisplayName))
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
			return nil
		}

		result := tx.Where(models.User{UserName: user.UserName}).FirstOrCreate(&user)
		if result.Error != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Failed to create the new user",
				Error:     result.Error.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return nil
		} else if result.RowsAffected == 0 {
			errMessage := fmt.Sprintf("Error: User with username '%s' already exists", *user.UserName)
			if !*user.Active {
				errMessage = fmt.Sprintf("Error: User with username '%s' already exists, but is deactivated", *user.UserName)
			}
			er := models.LicenseError{
				Status:    http.StatusConflict,
				Message:   "can not create user",
				Error:     errMessage,
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusConflict, er)
			return nil
		}

		if err := utils.AddChangelogsForUser(tx, userId, &user, &models.User{}); err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Failed to update changelogs",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return err
		}

		res := models.UserResponse{
			Data:   []models.User{user},
			Status: http.StatusCreated,
			Meta: &models.PaginationMeta{
				ResourceCount: 1,
			},
		}

		c.JSON(http.StatusCreated, res)

		return nil
	})
}

// CreateOidcUser creates a new user via oidc id token
//
//	@Summary		Create new user via oidc id token
//	@Description	Create a new service user via oidc id token
//	@Id				CreateOidcUser
//	@Tags			Users
//	@Accept			json
//	@Produce		json
//	@Success		201	{object}	models.UserResponse
//	@Failure		400	{object}	models.LicenseError	"Invalid json body"
//	@Failure		409	{object}	models.LicenseError	"User already exists"
//	@Router			/users/oidc [post]
func CreateOidcUser(c *gin.Context) {
	if os.Getenv("OIDC_ISSUER") == "" || os.Getenv("OIDC_EMAIL_KEY") == "" || os.Getenv("OIDC_DISPLAYNAME_KEY") == "" ||
		os.Getenv("OIDC_USERNAME_KEY") == "" || Jwks == nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Something went wrong, try again",
			Error:     "internal server error",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		log.Print("\033[31mError: OIDC environment variables not configured properly\033[0m")
		return
	}

	authHeader := c.GetHeader("Authorization")

	if authHeader == "" {
		er := models.LicenseError{
			Status:    http.StatusUnauthorized,
			Message:   "Please check your credentials and try again",
			Error:     "no credentials were passed",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusUnauthorized, er)
		c.Abort()
		return
	}

	parts := strings.Split(authHeader, " ")
	if len(parts) != 2 || strings.ToLower(parts[0]) != "bearer" {
		er := models.LicenseError{
			Status:    http.StatusUnauthorized,
			Message:   "Please check your credentials and try again",
			Error:     "no credentials were passed",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusUnauthorized, er)
		c.Abort()
		return
	}

	tokenString := parts[1]

	keyset, err := Jwks.Lookup(context.Background(), os.Getenv("JWKS_URI"))
	if err != nil {
		log.Print("\033[31mError: Failed jwk.Cache lookup from the oidc provider's URL\033[0m")
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Something went wrong",
			Error:     "internal server error",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	keyOptions := jws.WithKeySet(keyset)
	keyError := true
	if kid, err := utils.GetKid(tokenString); err == nil {
		if key, ok := keyset.LookupKeyID(kid); ok {
			if os.Getenv("OIDC_SIGNING_ALG") != "" {
				if alg, ok := jwa.LookupSignatureAlgorithm(os.Getenv("OIDC_SIGNING_ALG")); ok {
					if err = key.Set("alg", alg); err == nil {
						keyError = false
					}
				}
			} else if _, ok := key.Algorithm(); ok {
				keyError = false
			}
		}
	}

	if keyError {
		log.Printf("\033[31mError: Token verification failed due to invalid alg header key field \033[0m")
		er := models.LicenseError{
			Status:    http.StatusUnauthorized,
			Message:   "Please check your credentials and try again",
			Error:     "token verification failed",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusUnauthorized, er)
		return
	}

	if _, err = jws.Verify([]byte(tokenString), keyOptions); err != nil {
		er := models.LicenseError{
			Status:    http.StatusUnauthorized,
			Message:   "Please check your credentials and try again",
			Error:     "token verification failed",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusUnauthorized, er)
		log.Printf("\033[31mError: Token verification failed \033[0m")
		return
	}

	parsedToken, err := jwt.Parse([]byte(tokenString), jwt.WithValidate(true), jwt.WithVerify(false))
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusUnauthorized,
			Message:   "Please check your credentials and try again",
			Error:     "token parsing failed",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusUnauthorized, er)
		return
	}

	iss, _ := parsedToken.Issuer()
	if iss != os.Getenv("OIDC_ISSUER") {
		er := models.LicenseError{
			Status:    http.StatusUnauthorized,
			Message:   "Please check your credentials and try again",
			Error:     "internal server error",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusUnauthorized, er)
		log.Printf("\033[31mError: Issuer '%s' not supported\033[0m", iss)
		return
	}

	var email, username, displayname, errMessage string
	if err = parsedToken.Get(os.Getenv("OIDC_EMAIL_KEY"), &email); err != nil {
		errMessage = err.Error()
	}
	if err = parsedToken.Get(os.Getenv("OIDC_USERNAME_KEY"), &username); err != nil {
		errMessage = err.Error()
	}
	if err = parsedToken.Get(os.Getenv("OIDC_DISPLAYNAME_KEY"), &displayname); err != nil {
		errMessage = err.Error()
	}
	if errMessage != "" {
		er := models.LicenseError{
			Status:    http.StatusUnauthorized,
			Message:   "Please check your credentials and try again",
			Error:     "incompatible token format",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusUnauthorized, er)
		log.Printf("\033[31mError: %s\033[0m", errMessage)
		return
	}
	level := "USER"

	user := models.User{
		UserName:    &username,
		UserEmail:   &email,
		UserLevel:   &level,
		DisplayName: &displayname,
	}

	result := db.DB.
		Where(&models.User{UserName: user.UserName}).
		FirstOrCreate(&user)
	if result.Error != nil {
		errMessage := "Something went wrong. Try again."
		if errors.Is(result.Error, gorm.ErrDuplicatedKey) {
			errMessage = "User with same display name or email exists"
			er := models.LicenseError{
				Status:    http.StatusConflict,
				Message:   "Failed to create user",
				Error:     errMessage,
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusConflict, er)
			return
		}
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Failed to create the new user",
			Error:     errMessage,
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusInternalServerError, er)
		return
	}

	if result.RowsAffected == 0 {
		errMessage := fmt.Sprintf("Error: User with username '%s' already exists", *user.UserName)
		if !*user.Active {
			errMessage = fmt.Sprintf("Error: User with username '%s' already exists, but is deactivated", *user.UserName)
		}
		er := models.LicenseError{
			Status:    http.StatusConflict,
			Message:   "Failed to create user",
			Error:     errMessage,
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

// UpdateUser updates a user, requires admin rights
//
//	@Summary		Update user, requires admin rights
//	@Description	Update a service user, requires admin rights
//	@Id				UpdateUser
//	@Tags			Users
//	@Accept			json
//	@Produce		json
//	@Param			username	path		string				true	"username of the user to be updated"
//	@Param			user		body		models.UserUpdate	true	"User to update"
//	@Success		200			{object}	models.UserResponse
//	@Failure		400			{object}	models.LicenseError	"Invalid json body"
//	@Failure		403			{object}	models.LicenseError	"This resource requires elevated access rights"
//	@Security		ApiKeyAuth
//	@Router			/users/{username} [patch]
func UpdateUser(c *gin.Context) {
	userId := c.MustGet("userId").(uuid.UUID)
	_ = db.DB.Transaction(func(tx *gorm.DB) error {
		var olduser models.User
		var updates models.UserUpdate
		username := c.Param("username")

		if err := tx.Where(models.User{UserName: &username}).First(&olduser).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusNotFound,
				Message:   "no user with such username exists",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusNotFound, er)
			return nil
		}

		// var input models.UserUpdate
		if err := c.ShouldBindJSON(&updates); err != nil {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "invalid json body",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusBadRequest, er)
			return nil
		}

		if err := validations.Validate.Struct(&updates); err != nil {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "can not update user with these field values",
				Error:     fmt.Sprintf("field '%s' failed validation: %s\n", err.(validator.ValidationErrors)[0].Field(), err.(validator.ValidationErrors)[0].Tag()),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusBadRequest, er)
			return nil
		}

		updatedUser := models.User(updates)
		if updatedUser.UserName != nil {
			*updatedUser.UserName = html.EscapeString(strings.TrimSpace(*updatedUser.UserName))
		}
		if updatedUser.DisplayName != nil {
			*updatedUser.DisplayName = html.EscapeString(strings.TrimSpace(*updatedUser.DisplayName))
		}
		if updatedUser.UserPassword != nil {
			err := utils.HashPassword(&updatedUser)
			if err != nil {
				er := models.LicenseError{
					Status:    http.StatusBadRequest,
					Message:   "password hashing failed",
					Error:     err.Error(),
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				}
				c.JSON(http.StatusBadRequest, er)
				return nil
			}
		}
		updatedUser.Id = olduser.Id
		// update the user in the database
		if err := tx.Updates(&updatedUser).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Failed to update user",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return nil
		}
		// fetch the updated user to return
		if err := tx.First(&updatedUser, updatedUser.Id).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Failed to fetch updated user",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return nil
		}
		if err := utils.AddChangelogsForUser(tx, userId, &updatedUser, &olduser); err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Failed to update user",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return err
		}

		res := models.UserResponse{
			Data:   []models.User{updatedUser},
			Status: http.StatusCreated,
			Meta: &models.PaginationMeta{
				ResourceCount: 1,
			},
		}

		c.JSON(http.StatusOK, res)

		return nil
	})
}

// UpdateProfile updates one's user profile
//
//	@Summary		Users can update their profile using this endpoint
//	@Description	Users can update their profile using this endpoint
//	@Id				UpdateProfile
//	@Tags			Users
//	@Accept			json
//	@Produce		json
//	@Param			user	body		models.ProfileUpdate	true	"Profile fields to update"
//	@Success		200		{object}	models.UserResponse
//	@Failure		400		{object}	models.LicenseError	"Invalid json body"
//	@Security		ApiKeyAuth
//	@Router			/users [patch]
func UpdateProfile(c *gin.Context) {
	_ = db.DB.Transaction(func(tx *gorm.DB) error {
		var olduser models.User
		var changes models.ProfileUpdate

		userId := c.MustGet("userId").(uuid.UUID)

		if err := tx.Where(models.User{Id: userId}).First(&olduser).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusNotFound,
				Message:   "no user with such username exists",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusNotFound, er)
			return nil
		}

		if err := c.ShouldBindJSON(&changes); err != nil {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "invalid json body",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusBadRequest, er)
			return nil
		}

		if err := validations.Validate.Struct(&changes); err != nil {
			er := models.LicenseError{
				Status:    http.StatusBadRequest,
				Message:   "can not update profile with these field values",
				Error:     fmt.Sprintf("field '%s' failed validation: %s\n", err.(validator.ValidationErrors)[0].Field(), err.(validator.ValidationErrors)[0].Tag()),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusBadRequest, er)
			return nil
		}

		updatedUser := models.User(changes)
		if updatedUser.DisplayName != nil {
			*updatedUser.DisplayName = html.EscapeString(strings.TrimSpace(*updatedUser.DisplayName))
		}
		if updatedUser.UserPassword != nil {
			err := utils.HashPassword(&updatedUser)
			if err != nil {
				er := models.LicenseError{
					Status:    http.StatusBadRequest,
					Message:   "password hashing failed",
					Error:     err.Error(),
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				}
				c.JSON(http.StatusBadRequest, er)
				return nil
			}
		}

		updatedUser.Id = olduser.Id
		if err := tx.Clauses(clause.Returning{}).Updates(&updatedUser).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Failed to update user",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return nil
		}
		if err := utils.AddChangelogsForUser(tx, userId, &updatedUser, &olduser); err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Failed to update profile",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return err
		}

		res := models.UserResponse{
			Data:   []models.User{updatedUser},
			Status: http.StatusCreated,
			Meta: &models.PaginationMeta{
				ResourceCount: 1,
			},
		}

		c.JSON(http.StatusOK, res)

		return nil
	})
}

// DeleteUser marks an existing user record as inactive
//
//	@Summary		Deactivate user
//	@Description	Deactivate an user
//	@Id				DeleteUser
//	@Tags			Users
//	@Accept			json
//	@Produce		json
//	@Param			username	path	string	true	"Username of the user to be marked as inactive"
//	@Success		204
//	@Failure		404	{object}	models.LicenseError	"No user with given username found"
//	@Security		ApiKeyAuth
//	@Router			/users/{username} [delete]
func DeleteUser(c *gin.Context) {
	_ = db.DB.Transaction(func(tx *gorm.DB) error {
		var olduser models.User
		userId := c.MustGet("userId").(uuid.UUID)
		active := true
		if err := tx.Where(models.User{Id: userId, Active: &active}).First(&olduser).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusNotFound,
				Message:   "no user with such username exists",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusNotFound, er)
			return nil
		}
		updatedUser := olduser
		updateActive := false
		updatedUser.Active = &updateActive

		if err := tx.Updates(&updatedUser).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "failed to delete user",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusNotFound, er)
			return nil
		}

		if err := tx.Where(&models.OidcClient{UserId: updatedUser.Id}).Delete(&models.OidcClient{}).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "failed to delete user",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return err
		}

		if err := utils.AddChangelogsForUser(tx, userId, &updatedUser, &olduser); err != nil {
			er := models.LicenseError{
				Status:    http.StatusInternalServerError,
				Message:   "Failed to update profile",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusInternalServerError, er)
			return err
		}

		c.Status(http.StatusNoContent)
		return nil
	})
}

// GetAllUser retrieves a list of all users from the database.
//
//	@Summary		Get users
//	@Description	Get all service users
//	@Id				GetAllUsers
//	@Tags			Users
//	@Accept			json
//	@Produce		json
//	@Param			active	query		bool	false	"Active user only"
//	@Param			page	query		int		false	"Page number"
//	@Param			limit	query		int		false	"Number of records per page"
//	@Success		200		{object}	models.UserResponse
//	@Failure		404		{object}	models.LicenseError	"Users not found"
//	@Security		ApiKeyAuth
//	@Router			/users [get]
func GetAllUser(c *gin.Context) {
	active, err := strconv.ParseBool(c.Query("active"))
	if err != nil {
		active = false
	}

	var users []models.User
	query := db.DB.Model(&models.User{})
	_ = utils.PreparePaginateResponse(c, query, &models.UserResponse{})
	if err := query.Where(&models.User{Active: &active}).Find(&users).Error; err != nil {
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
//	@Description	Get a single user by username
//	@Id				GetUser
//	@Tags			Users
//	@Accept			json
//	@Produce		json
//	@Param			username	path		string	true	"Username"
//	@Success		200			{object}	models.UserResponse
//	@Failure		400			{object}	models.LicenseError	"Invalid user id"
//	@Failure		404			{object}	models.LicenseError	"User not found"
//	@Security		ApiKeyAuth
//	@Router			/users/{username} [get]
func GetUser(c *gin.Context) {
	var user models.User
	username := c.Param("username")

	active := true
	if err := db.DB.Where(models.User{UserName: &username, Active: &active}).First(&user).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   "no user with such username exists",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

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
//	@Param			user	body		models.UserLogin	true	"Login credentials"
//	@Success		200		{object}	models.TokenResonse	"JWT token"
//	@Failure		401		{object}	models.LicenseError	"Incorrect username or password"
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
	active := true
	var user models.User
	result := db.DB.Where(models.User{UserName: &username, Active: &active}).First(&user)
	if result.Error != nil {
		er := models.LicenseError{
			Status:    http.StatusUnauthorized,
			Message:   "Incorrect username or password",
			Error:     "Incorrect username or password",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}

		c.JSON(http.StatusUnauthorized, er)
		return
	}

	if user.UserPassword == nil {
		er := models.LicenseError{
			Status:    http.StatusUnauthorized,
			Message:   "Incorrect username or password",
			Error:     "Incorrect username or password",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}

		c.JSON(http.StatusUnauthorized, er)
		return
	}

	err := EncryptUserPassword(&user)
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusInternalServerError,
			Message:   "Failed to encrypt user password",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}

		c.JSON(http.StatusInternalServerError, er)
		return
	}

	// Check if the password matches
	err = utils.VerifyPassword(password, *user.UserPassword)
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusUnauthorized,
			Message:   "Incorrect username or password",
			Error:     "Incorrect username or password",
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}

		c.JSON(http.StatusUnauthorized, er)
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
	res := models.TokenResonse{
		Status: http.StatusOK,
		Data:   *token,
	}

	c.JSON(http.StatusOK, res)
}

// GetUserProfile retrieves the user's own profile.
//
//	@Summary		Get user's own profile
//	@Description	Get user's own profile
//	@Id				GetUserProfile
//	@Tags			Users
//	@Accept			json
//	@Produce		json
//	@Success		200	{object}	models.UserResponse
//	@Failure		400	{object}	models.LicenseError	"Invalid user"
//	@Failure		404	{object}	models.LicenseError	"User not found"
//	@Security		ApiKeyAuth
//	@Router			/users/profile [get]
func GetUserProfile(c *gin.Context) {
	var user models.User
	userId := c.MustGet("userId").(uuid.UUID)

	active := true
	if err := db.DB.Where(models.User{Id: userId, Active: &active}).First(&user).Error; err != nil {
		er := models.LicenseError{
			Status:    http.StatusNotFound,
			Message:   "no user with such username exists",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusNotFound, er)
		return
	}

	res := models.UserResponse{
		Data:   []models.User{user},
		Status: http.StatusOK,
		Meta: &models.PaginationMeta{
			ResourceCount: 1,
		},
	}

	c.JSON(http.StatusOK, res)
}

// VerifyRefreshToken verifies a refresh token and issues a new access token
//
//	@Summary		Verify refresh token
//	@Description	verify refresh token and get new access token
//	@Id				RefreshToken
//	@Tags			Users
//	@Accept			json
//	@Produce		json
//	@Param			user	body		models.RefreshToken	true	"Refresh token payload"
//	@Success		200		{object}	models.TokenResonse	" JWT token"
//	@Failure		401		{object}	models.LicenseError	"Invalid or expired refresh token"
//	@Router			/refresh-token [post]
func VerifyRefreshToken(c *gin.Context) {
	logger.LogInfo("VerifyRefreshToken called")

	var input models.RefreshToken
	if err := c.ShouldBindJSON(&input); err != nil {
		logger.LogWarn("Invalid JSON body", zap.Error(err))
		c.JSON(http.StatusBadRequest, models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   "invalid json body",
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		})
		return
	}

	refreshToken := input.RefreshToken

	unverifiedToken, err := jwt.Parse(
		[]byte(refreshToken),
		jwt.WithVerify(false),
		jwt.WithValidate(true),
	)
	if err != nil {
		logger.LogError("Token parsing failed", zap.Error(err))
		unauthorized(c, "token parsing failed")
		return
	}

	iss, ok := unverifiedToken.Issuer()
	if !ok || iss != os.Getenv("DEFAULT_ISSUER") {
		logger.LogWarn("Invalid token issuer", zap.String("issuer", iss))
		unauthorized(c, "invalid issuer")
		return
	}

	if _, err := jws.Verify(
		[]byte(refreshToken),
		jws.WithKey(jwa.HS256(), []byte(os.Getenv("REFRESH_TOKEN_SECRET"))),
	); err != nil {
		logger.LogError("Token signature verification failed", zap.Error(err))
		unauthorized(c, "token verification failed")
		return
	}

	var typeStr string
	if err := unverifiedToken.Get("type", &typeStr); err != nil || typeStr != "refresh" {
		logger.LogWarn("Invalid token type", zap.String("type", typeStr))
		unauthorized(c, "invalid token type (expected 'refresh')")
		return
	}

	var sub string
	if err := unverifiedToken.Get("sub", &sub); err != nil {
		logger.LogError("Missing subject claim", zap.Error(err))
		unauthorized(c, "missing subject claim")
		return
	}

	userID, err := uuid.Parse(sub)
	if err != nil {
		logger.LogError("Invalid user ID in token", zap.Error(err), zap.String("sub", sub))
		unauthorized(c, "invalid user ID in token")
		return
	}

	active := true
	var user models.User
	if err := db.DB.Where(models.User{Id: userID, Active: &active}).First(&user).Error; err != nil {
		logger.LogWarn("User not found or inactive", zap.String("userID", userID.String()))
		unauthorized(c, "user not found")
		return
	}

	tokens, err := generateToken(user)
	if err != nil {
		logger.LogError("Failed to generate access token", zap.Error(err))
		c.JSON(http.StatusInternalServerError, gin.H{"error": "could not generate access token"})
		return
	}

	logger.LogInfo("VerifyRefreshToken completed successfully", zap.String("userID", userID.String()))

	c.JSON(http.StatusOK, models.TokenResonse{
		Status: http.StatusOK,
		Data:   *tokens,
	})
}

// EncryptUserPassword checks if the password is already encrypted or not. If
// not, it encrypts the password.
func EncryptUserPassword(user *models.User) error {
	_, err := bcrypt.Cost([]byte(*user.UserPassword))
	if err == nil {
		return nil
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(*user.UserPassword), bcrypt.DefaultCost)

	if err != nil {
		return err
	}
	*user.UserPassword = string(hashedPassword)

	db.DB.Model(&user).Updates(user)

	return nil
}

func generateToken(user models.User) (*models.Tokens, error) {
	logger.LogInfo("generateToken called",
		zap.String("userID", user.Id.String()),
		zap.String("username", *user.UserName),
	)

	accessTokenLifespan, err := strconv.Atoi(os.Getenv("TOKEN_HOUR_LIFESPAN"))
	if err != nil {
		logger.LogError("Invalid access token lifespan", zap.Error(err))
		return nil, fmt.Errorf("invalid access token lifespan: %w", err)
	}
	refreshTokenLifespan, err := strconv.Atoi(os.Getenv("REFRESH_TOKEN_HOUR_LIFESPAN"))
	if err != nil {
		logger.LogError("Invalid refresh token lifespan", zap.Error(err))
		return nil, fmt.Errorf("invalid refresh token lifespan: %w", err)
	}

	issuer := os.Getenv("DEFAULT_ISSUER")
	accessSecret := []byte(os.Getenv("API_SECRET"))
	refreshSecret := []byte(os.Getenv("REFRESH_TOKEN_SECRET"))
	now := time.Now().UTC()
	safeClaim := models.UserClaim{
		Id:          user.Id,
		UserName:    user.UserName,
		DisplayName: user.DisplayName,
		UserEmail:   user.UserEmail,
		UserLevel:   user.UserLevel,
	}
	// Build Access Token
	accessToken, err := jwt.NewBuilder().
		Issuer(issuer).
		IssuedAt(now).
		NotBefore(now).
		Expiration(now.Add(time.Hour*time.Duration(accessTokenLifespan))).
		Claim("user", safeClaim).
		Build()
	if err != nil {
		logger.LogError("Failed to build access token", zap.Error(err))
		return nil, fmt.Errorf("failed to build access token: %w", err)
	}

	signedAccessToken, err := jwt.Sign(accessToken, jwt.WithKey(jwa.HS256(), accessSecret))
	if err != nil {
		logger.LogError("Failed to sign access token", zap.Error(err))
		return nil, fmt.Errorf("failed to sign access token: %w", err)
	}
	// build refresh token
	refreshToken, err := jwt.NewBuilder().
		Issuer(issuer).
		IssuedAt(now).
		NotBefore(now).
		Expiration(now.Add(time.Hour*time.Duration(refreshTokenLifespan))).
		Claim("sub", fmt.Sprintf("%d", user.Id)).
		Claim("type", "refresh").
		Claim("user", safeClaim).
		Build()
	if err != nil {
		logger.LogError("Failed to build refresh token", zap.Error(err))
		return nil, fmt.Errorf("failed to build refresh token: %w", err)
	}

	signedRefreshToken, err := jwt.Sign(refreshToken, jwt.WithKey(jwa.HS256(), refreshSecret))
	if err != nil {
		logger.LogError("Failed to sign refresh token", zap.Error(err))
		return nil, fmt.Errorf("failed to sign refresh token: %w", err)
	}

	tokens := &models.Tokens{
		AccessToken:          string(signedAccessToken),
		RefreshToken:         string(signedRefreshToken),
		AccessTokenExpiresIn: int64(accessTokenLifespan * 3600), // in seconds
	}
	logger.LogInfo("generateToken completed successfully", zap.String("userID", user.Id.String()))
	return tokens, nil
}

func unauthorized(c *gin.Context, msg string) {
	c.JSON(http.StatusUnauthorized, models.LicenseError{
		Status:    http.StatusUnauthorized,
		Message:   "Please check your credentials and try again",
		Error:     msg,
		Path:      c.Request.URL.Path,
		Timestamp: time.Now().Format(time.RFC3339),
	})
	c.Abort()
}
