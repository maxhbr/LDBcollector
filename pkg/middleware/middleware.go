// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2024 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package middleware

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v4"
)

// AuthenticationMiddleware is a middleware function for user authentication.
func AuthenticationMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		tokenString := c.GetHeader("Authorization")

		if tokenString == "" {
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

		token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
			}
			return []byte(os.Getenv("API_SECRET")), nil
		})

		if err != nil {
			er := models.LicenseError{
				Status:    http.StatusUnauthorized,
				Message:   "Please check your credentials and try again",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}

			c.JSON(http.StatusUnauthorized, er)
			c.Abort()
			return
		}

		claims, ok := token.Claims.(jwt.MapClaims)
		if !ok || !token.Valid {
			er := models.LicenseError{
				Status:    http.StatusUnauthorized,
				Message:   "Invalid token",
				Error:     "Invalid token",
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}

			c.JSON(http.StatusUnauthorized, er)
			c.Abort()
			return
		}

		userId := int64(claims["user"].(map[string]interface{})["id"].(float64))

		var user models.User
		if err := db.DB.Where(models.User{Id: userId}).First(&user).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusUnauthorized,
				Message:   "User not found",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}

			c.JSON(http.StatusUnauthorized, er)
			c.Abort()
			return
		}

		c.Set("username", user.Username)
		c.Next()
	}
}

// CORSMiddleware is a middleware function for CORS.
func CORSMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Writer.Header().Set("Access-Control-Expose-Headers", "Content-Disposition")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, PATCH, DELETE")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}

// PaginationMiddleware handles pagination requests and responses.
func PaginationMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		var page models.PaginationInput
		parsedPage, err := strconv.ParseInt(c.Query("page"), 10, 64)
		if err == nil {
			page.Page = parsedPage
		}
		parsedLimit, err := strconv.ParseInt(c.Query("limit"), 10, 64)
		if err == nil {
			page.Limit = parsedLimit
		}

		if page.Page == 0 {
			page.Page = utils.DefaultPage
		}

		if page.Limit == 0 {
			page.Limit = utils.DefaultLimit
		}

		// Create a custom writer to capture and process response body
		buffer := new(bytes.Buffer)
		writer := &bodyWriter{body: buffer, ResponseWriter: c.Writer}
		c.Writer = writer

		// Set the pagination information for routes who need it
		c.Set("page", page)
		c.Next()

		// Get the pagination information from route after processing
		metaValue, paginationExists := c.Get("paginationMeta")

		// Handle only 200 responses with paginationMeta
		if paginationExists && c.Writer.Status() == 200 {
			originalBody := writer.body.Bytes()
			var metaObject *models.PaginationMeta

			// Try the body with different possible unmarshalling before failing
			var licenseRes models.LicenseResponse
			var obligationRes models.ObligationResponse
			var auditRes models.AuditResponse
			var userRes models.UserResponse
			isLicenseRes := false
			isObligationRes := false
			isAuditRes := false
			isUserRes := false
			responseModel, _ := c.Get("responseModel")
			switch responseModel.(type) {
			case *models.LicenseResponse:
				err = json.Unmarshal(originalBody, &licenseRes)
				isLicenseRes = true
				metaObject = licenseRes.Meta
			case *models.ObligationResponse:
				err = json.Unmarshal(originalBody, &obligationRes)
				isObligationRes = true
				metaObject = obligationRes.Meta
			case *models.AuditResponse:
				err = json.Unmarshal(originalBody, &auditRes)
				isAuditRes = true
				metaObject = auditRes.Meta
			case *models.UserResponse:
				err = json.Unmarshal(originalBody, &userRes)
				isUserRes = true
				metaObject = userRes.Meta
			default:
				err = fmt.Errorf("unknown response model type")
			}
			if err != nil {
				log.Fatalf("Error marshalling new body: %s", err)
			}

			paginationMeta := metaValue.(models.PaginationMeta)

			// Get the query params from the request
			params := c.Request.URL.Query()

			metaObject.Page = page.Page
			metaObject.Limit = page.Limit
			metaObject.ResourceCount = paginationMeta.ResourceCount
			metaObject.TotalPages = int64(math.Ceil(float64(paginationMeta.ResourceCount) / float64(page.Limit)))
			// Can go next
			if metaObject.Page < metaObject.TotalPages {
				params.Set("page", strconv.FormatInt(int64(metaObject.Page+1), 10))
				c.Request.URL.RawQuery = params.Encode()

				metaObject.Next = c.Request.URL.String()
			}
			// Can go previous
			if metaObject.Page > 1 {
				params.Set("page", strconv.FormatInt(int64(metaObject.Page-1), 10))
				c.Request.URL.RawQuery = params.Encode()

				metaObject.Previous = c.Request.URL.String()
			}

			// Marshal the new body
			var newBody []byte
			var err error
			if isLicenseRes {
				newBody, err = json.Marshal(licenseRes)
			} else if isObligationRes {
				newBody, err = json.Marshal(obligationRes)
			} else if isAuditRes {
				newBody, err = json.Marshal(auditRes)
			} else if isUserRes {
				newBody, err = json.Marshal(userRes)
			}
			if err != nil {
				log.Fatalf("Error marshalling new body: %s", err.Error())
			}
			_, err = c.Writer.WriteString(string(newBody))
			if err != nil {
				log.Fatalf("Error writing new body: %s", err.Error())
			}
		} else {
			// Write the original body for non-paginated responses
			_, err := c.Writer.WriteString(writer.body.String())
			if err != nil {
				log.Fatalf("Error writing new body: %s", err.Error())
			}
		}
	}
}

// bodyWriter is a custom writer to capture and process response body.
type bodyWriter struct {
	gin.ResponseWriter
	body *bytes.Buffer
}

// Write is a custom write function to capture and process response body.
func (w bodyWriter) Write(b []byte) (int, error) {
	return w.body.Write(b)
}
