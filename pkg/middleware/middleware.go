// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2024 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
// SPDX-FileCopyrightText: 2025 Chayan Das <01chayandas@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package middleware

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/fossology/LicenseDb/pkg/auth"
	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/gin-gonic/gin"
	"github.com/lestrrat-go/jwx/v3/jwa"
	"github.com/lestrrat-go/jwx/v3/jws"
	"github.com/lestrrat-go/jwx/v3/jwt"
)

// AuthenticationMiddleware is a middleware function for user authentication.
func AuthenticationMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			unauthorized(c, "no credentials were passed")
			return
		}
		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 {
			unauthorized(c, "no credentials were passed")
			return
		}
		tokenString := parts[1]
		unverfiedParsedToken, err := jwt.Parse([]byte(tokenString), jwt.WithVerify(false), jwt.WithValidate(true))
		if err != nil {
			unauthorized(c, "token parsing failed")
			return
		}

		iss, _ := unverfiedParsedToken.Issuer()
		if iss == os.Getenv("DEFAULT_ISSUER") {
			_, err := jws.Verify([]byte(tokenString), jws.WithKey(jwa.HS256(), []byte(os.Getenv("API_SECRET"))))
			if err != nil {
				log.Printf("\033[31mError: %s\033[0m", err.Error())
				unauthorized(c, "token verification failed")
				return
			}

			var userData map[string]interface{}
			if err = unverfiedParsedToken.Get("user", &userData); err != nil {
				log.Printf("\033[31mError: %s\033[0m", err.Error())
				unauthorized(c, "incompatible token format")
				return
			}

			userDataBytes, err := json.Marshal(userData)
			if err != nil {
				log.Printf("\033[31mError: %s\033[0m", err.Error())
				unauthorized(c, "failed to marshal user data")
				return
			}

			// Unmarshal the JSON bytes into the models.User struct
			var user models.User
			err = json.Unmarshal(userDataBytes, &user)
			if err != nil {
				log.Printf("\033[31mError: %s\033[0m", err.Error())
				unauthorized(c, "incompatible token format")
				return
			}

			active := true
			if err := db.DB.Where(models.User{Id: user.Id, Active: &active}).First(&user).Error; err != nil {
				log.Printf("\033[31mError: %s\033[0m", err.Error())
				unauthorized(c, "User not found. Please check your credentials.")
				return
			}
			c.Set("userId", user.Id)
			c.Set("role", *user.UserLevel)
		} else if iss == os.Getenv("OIDC_ISSUER") {

			if auth.Jwks == nil {
				log.Print("\033[31mError: OIDC environment variables not configured properly\033[0m")
				er := models.LicenseError{
					Status:    http.StatusInternalServerError,
					Message:   "Something went wrong",
					Error:     "internal server error",
					Path:      c.Request.URL.Path,
					Timestamp: time.Now().Format(time.RFC3339),
				}
				c.JSON(http.StatusInternalServerError, er)
				c.Abort()
				return
			}

			keyset, err := auth.Jwks.Lookup(context.Background(), os.Getenv("JWKS_URI"))
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
				c.Abort()
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
				unauthorized(c, "token verification failed")
				c.Abort()
				return
			}

			if _, err = jws.Verify([]byte(tokenString), keyOptions); err != nil {
				log.Printf("\033[31mError: Token verification failed \033[0m")
				unauthorized(c, "token verification failed")
				c.Abort()
				return
			}

			isClientCredentialsFlow := false

			var oidcClienToUserMapper string
			if os.Getenv("OIDC_CLIENT_TO_USER_MAPPER_CLAIM") != "" {
				if err := unverfiedParsedToken.Get(os.Getenv("OIDC_CLIENT_TO_USER_MAPPER_CLAIM"), &oidcClienToUserMapper); err == nil {
					isClientCredentialsFlow = true
				}
			}

			var user models.User

			if isClientCredentialsFlow {
				var oidcClient models.OidcClient
				if err := db.DB.Preload("User").Where(&models.OidcClient{ClientId: oidcClienToUserMapper}).First(&oidcClient).Error; err != nil {
					log.Printf("\033[31mError: %s\033[0m", err.Error())
					unauthorized(c, "oidc client not set up")
					return
				}

				user = oidcClient.User
			} else {
				if os.Getenv("OIDC_USERNAME_KEY") == "" {
					log.Print("\033[31mError: OIDC environment variables not configured properly\033[0m")
					er := models.LicenseError{
						Status:    http.StatusInternalServerError,
						Message:   "Something went wrong",
						Error:     "internal server error",
						Path:      c.Request.URL.Path,
						Timestamp: time.Now().Format(time.RFC3339),
					}
					c.JSON(http.StatusInternalServerError, er)
					c.Abort()
					return
				}

				var username string
				if err = unverfiedParsedToken.Get(os.Getenv("OIDC_USERNAME_KEY"), &username); err != nil {
					log.Printf("\033[31mError: %s\033[0m", err.Error())
					unauthorized(c, "incompatible token format")
					return
				}

				if err := db.DB.Where(models.User{UserName: &username}).First(&user).Error; err != nil {
					log.Printf("\033[31mError: %s\033[0m", err.Error())
					unauthorized(c, "User not found")
					return
				}
			}

			c.Set("userId", user.Id)
			c.Set("role", *user.UserLevel)
		} else {
			log.Printf("\033[31mError: Issuer '%s' not supported or not configured in .env\033[0m", iss)
			unauthorized(c, "internal server error")
			return
		}
		c.Next()
	}
}

// RoleBasedAccessMiddleware is a middleware function for giving role based access to apis.
func RoleBasedAccessMiddleware(roles []string) gin.HandlerFunc {
	return func(c *gin.Context) {
		role := c.GetString("role")
		found := false
		for _, r := range roles {
			if role == r {
				found = true
				break
			}
		}
		if !found {
			log.Print("\033[31mError: access denied due to insufficient role permissions\033[0m")
			er := models.LicenseError{
				Status:    http.StatusForbidden,
				Message:   "You do not have the necessary permissions to access this resource",
				Error:     "access denied due to insufficient role permissions",
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusForbidden, er)
			c.Abort()
			return
		}
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
				metaObject = &obligationRes.Meta
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
