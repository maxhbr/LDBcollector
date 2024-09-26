// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package utils

import (
	"fmt"
	"html"
	"net/http"
	"strconv"
	"strings"
	"time"

	"gorm.io/gorm"
	"gorm.io/gorm/clause"

	"golang.org/x/crypto/bcrypt"

	"github.com/gin-gonic/gin"
	"github.com/go-playground/validator/v10"

	"github.com/fossology/LicenseDb/pkg/models"
)

var (
	// DefaultPage Set default page to 1
	DefaultPage int64 = 1
	// DefaultLimit Set default max limit to 20
	DefaultLimit int64 = 20
)

// The Converter function takes an input of type models.LicenseJson and converts it into a
// corresponding models.LicenseDB object.
// It performs several field assignments and transformations to create the LicenseDB object,
// including generating the SpdxId based on the SpdxCompatible field.
// The resulting LicenseDB object is returned as the output of this function.
func Converter(input models.LicenseJson) models.LicenseDB {
	spdxCompatible, err := strconv.ParseBool(input.SpdxCompatible)
	if err != nil {
		spdxCompatible = false
	}
	if spdxCompatible {
		input.SpdxCompatible = input.Shortname
	} else {
		input.SpdxCompatible = "LicenseRef-fossology-" + input.Shortname
	}

	copyleft, err := strconv.ParseBool(input.Copyleft)
	if err != nil {
		copyleft = false
	}
	fsfFree, err := strconv.ParseBool(input.FSFfree)
	if err != nil {
		fsfFree = false
	}
	osiApproved, err := strconv.ParseBool(input.OSIapproved)
	if err != nil {
		osiApproved = false
	}
	gplv2Compatible, err := strconv.ParseBool(input.GPLv2compatible)
	if err != nil {
		gplv2Compatible = false
	}
	gplv3Compatible, err := strconv.ParseBool(input.GPLv3compatible)
	if err != nil {
		gplv3Compatible = false
	}
	textUpdatable, err := strconv.ParseBool(input.TextUpdatable)
	if err != nil {
		textUpdatable = false
	}
	active, err := strconv.ParseBool(input.Active)
	if err != nil {
		active = false
	}
	marydone, err := strconv.ParseBool(input.Marydone)
	if err != nil {
		marydone = false
	}
	addDate, err := time.Parse(time.RFC3339, input.AddDate)
	if err != nil {
		addDate = time.Now()
	}
	detectorType := input.DetectorType
	risk, err := strconv.ParseInt(input.Risk, 10, 64)
	if err != nil {
		risk = 0
	}
	flag, err := strconv.ParseInt(input.Flag, 10, 64)
	if err != nil {
		flag = 1
	}

	result := models.LicenseDB{
		Shortname:       &input.Shortname,
		Fullname:        &input.Fullname,
		Text:            &input.Text,
		Url:             &input.Url,
		Copyleft:        &copyleft,
		AddDate:         addDate,
		FSFfree:         &fsfFree,
		OSIapproved:     &osiApproved,
		GPLv2compatible: &gplv2Compatible,
		GPLv3compatible: &gplv3Compatible,
		Notes:           &input.Notes,
		Fedora:          &input.Fedora,
		TextUpdatable:   &textUpdatable,
		DetectorType:    &detectorType,
		Active:          &active,
		Source:          &input.Source,
		SpdxId:          &input.SpdxCompatible,
		Risk:            &risk,
		Flag:            &flag,
		Marydone:        &marydone,
	}
	return result
}

// ParseIdToInt convert the string ID from gin.Context to an integer and throw error if conversion fails. Also,
// update the gin.Context with REST API error.
func ParseIdToInt(c *gin.Context, id string, idType string) (int64, error) {
	parsedId, err := strconv.ParseInt(id, 10, 64)
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("invalid %s id", idType),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return 0, err
	}
	return parsedId, nil
}

// HashPassword hashes the password of the user using bcrypt. It also trims the
// username and escapes the HTML characters.
func HashPassword(user *models.User) error {
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(*user.Userpassword), bcrypt.DefaultCost)

	if err != nil {
		return err
	}
	*user.Userpassword = string(hashedPassword)

	user.Username = html.EscapeString(strings.TrimSpace(user.Username))

	return nil
}

// VerifyPassword compares the input password with the password stored in the
// database. Returns nil on success, or an error on failure.
func VerifyPassword(inputPassword, dbPassword string) error {
	return bcrypt.CompareHashAndPassword([]byte(dbPassword), []byte(inputPassword))
}

// PreparePaginateResponse prepares the pagination response for the API.
// It gets the count of total rows and sets the pagination parameters, also
// updates the query limit and offset and update the "paginationMeta" and
// "responseModel" in gin.Context for middleware to process.
func PreparePaginateResponse(c *gin.Context, query *gorm.DB,
	responseModel interface{}) models.PaginationInput {
	var totalRows int64
	query.Count(&totalRows)

	pageVar, exists := c.Get("page")
	if !exists {
		pageVar = models.PaginationInput{
			Page:  DefaultPage,
			Limit: DefaultLimit,
		}
	}
	pagination := pageVar.(models.PaginationInput)

	query.Offset(int(pagination.GetOffset())).Limit(int(pagination.GetLimit()))

	var paginationMeta models.PaginationMeta
	paginationMeta.ResourceCount = int(totalRows)

	c.Set("paginationMeta", paginationMeta)
	c.Set("responseModel", responseModel)
	return pagination
}

// LicenseImportStatusCode is internally used for checking status of a license import
type LicenseImportStatusCode int

// Status codes covering various scenarios that can occur on a license import
const (
	IMPORT_FAILED LicenseImportStatusCode = iota + 1
	IMPORT_LICENSE_CREATED
	IMPORT_LICENSE_UPDATED
	IMPORT_LICENSE_UPDATED_EXCEPT_TEXT
)

func InsertOrUpdateLicenseOnImport(tx *gorm.DB, license *models.LicenseDB, externalRefs *models.UpdateExternalRefsJSONPayload) (string, LicenseImportStatusCode, *models.LicenseDB, *models.LicenseDB) {
	var message string
	var importStatus LicenseImportStatusCode
	var newLicense, oldLicense models.LicenseDB

	validate := validator.New(validator.WithRequiredStructEnabled())

	if err := validate.Struct(license); err != nil {
		message = fmt.Sprintf("field '%s' failed validation: %s\n", err.(validator.ValidationErrors)[0].Field(), err.(validator.ValidationErrors)[0].Tag())
		importStatus = IMPORT_FAILED
		return message, importStatus, &oldLicense, &newLicense
	}

	result := tx.
		Where(&models.LicenseDB{Shortname: license.Shortname}).
		Attrs(license).
		FirstOrCreate(&oldLicense)
	if result.Error != nil {
		message = fmt.Sprintf("failed to create license: %s", result.Error.Error())
		importStatus = IMPORT_FAILED
		return message, importStatus, &oldLicense, &newLicense
	} else if result.RowsAffected == 0 {
		// case when license exists in database and is updated

		// Overwrite values of existing keys, add new key value pairs and remove keys with null values.
		if err := tx.Model(&models.LicenseDB{}).Where(models.LicenseDB{Id: oldLicense.Id}).UpdateColumn("external_ref", gorm.Expr("jsonb_strip_nulls(COALESCE(external_ref, '{}'::jsonb) || ?)", &externalRefs.ExternalRef)).Error; err != nil {
			message = fmt.Sprintf("failed to update license: %s", err.Error())
			importStatus = IMPORT_FAILED
			return message, importStatus, &oldLicense, &newLicense
		}

		// https://github.com/go-gorm/gorm/issues/3938: BeforeSave hook is called on the struct passed in .Model()
		// Cannot pass empty newLicense struct in .Model() as all fields will be empty and no validation will happen
		newLicense = *license

		// Update all other fields except external_ref and rf_shortname
		query := tx.Model(&newLicense).Where(&models.LicenseDB{Id: oldLicense.Id}).Omit("external_ref", "rf_shortname")

		// Do not update text in import if it was modified manually
		if *oldLicense.Flag == 2 {
			query = query.Omit("rf_text")
		}

		if err := query.Clauses(clause.Returning{}).Updates(&newLicense).Error; err != nil {
			message = fmt.Sprintf("failed to update license: %s", err.Error())
			importStatus = IMPORT_FAILED
			return message, importStatus, &oldLicense, &newLicense
		}

		if *newLicense.Flag == 2 {
			message = "all fields except rf_text were updated. rf_text was updated manually and cannot be overwritten in an import."
			importStatus = IMPORT_LICENSE_UPDATED_EXCEPT_TEXT
			// error is not returned here as it will rollback the transaction
		} else {
			importStatus = IMPORT_LICENSE_UPDATED
		}
	} else {
		// case when license doesn't exist in database and is inserted
		importStatus = IMPORT_LICENSE_CREATED
	}

	return message, importStatus, &oldLicense, &newLicense
}
