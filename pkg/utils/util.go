// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package utils

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"net/http"
	"os"
	"reflect"
	"strconv"
	"strings"
	"time"

	"gorm.io/gorm"
	"gorm.io/gorm/clause"

	"golang.org/x/crypto/bcrypt"

	"github.com/gin-gonic/gin"
	"github.com/go-playground/validator/v10"

	"github.com/fossology/LicenseDb/pkg/db"
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
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(*user.UserPassword), bcrypt.DefaultCost)

	if err != nil {
		return err
	}
	*user.UserPassword = string(hashedPassword)

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

func InsertOrUpdateLicenseOnImport(license *models.LicenseDB, externalRefs *models.UpdateExternalRefsJSONPayload, username string) (string, LicenseImportStatusCode) {
	var message string
	var importStatus LicenseImportStatusCode
	var newLicense, oldLicense models.LicenseDB

	validate := validator.New(validator.WithRequiredStructEnabled())

	if err := validate.Struct(license); err != nil {
		message = fmt.Sprintf("field '%s' failed validation: %s\n", err.(validator.ValidationErrors)[0].Field(), err.(validator.ValidationErrors)[0].Tag())
		importStatus = IMPORT_FAILED
		return message, importStatus
	}

	_ = db.DB.Transaction(func(tx *gorm.DB) error {
		ctx := context.WithValue(context.Background(), models.ContextKey("user"), username)
		result := tx.WithContext(ctx).
			Where(&models.LicenseDB{Shortname: license.Shortname}).
			Attrs(license).
			FirstOrCreate(&oldLicense)
		if result.Error != nil {
			message = fmt.Sprintf("failed to import license: %s", result.Error.Error())
			importStatus = IMPORT_FAILED
			return errors.New(message)
		} else if result.RowsAffected == 0 {
			// case when license exists in database and is updated

			// Overwrite values of existing keys, add new key value pairs and remove keys with null values.
			if err := tx.Model(&models.LicenseDB{}).Where(models.LicenseDB{Id: oldLicense.Id}).UpdateColumn("external_ref", gorm.Expr("jsonb_strip_nulls(COALESCE(external_ref, '{}'::jsonb) || ?)", &externalRefs.ExternalRef)).Error; err != nil {
				message = fmt.Sprintf("failed to update license: %s", err.Error())
				importStatus = IMPORT_FAILED
				return errors.New(message)
			}

			// https://github.com/go-gorm/gorm/issues/3938: BeforeSave hook is called on the struct passed in .Model()
			// Cannot pass empty newLicense struct in .Model() as all fields will be empty and no validation will happen
			newLicense = *license

			// Update all other fields except external_ref and rf_shortname
			query := tx.Model(&newLicense).Where(&models.LicenseDB{Id: oldLicense.Id}).Omit("external_ref", "rf_shortname", "User")

			// Do not update text in import if it was modified manually
			if *oldLicense.Flag == 2 {
				query = query.Omit("rf_text")
			}

			if err := query.Clauses(clause.Returning{}).Updates(&newLicense).Error; err != nil {
				message = fmt.Sprintf("failed to update license: %s", err.Error())
				importStatus = IMPORT_FAILED
				return errors.New(message)
			}

			if err := AddChangelogsForLicense(tx, username, &newLicense, &oldLicense); err != nil {
				message = fmt.Sprintf("failed to update license: %s", err.Error())
				importStatus = IMPORT_FAILED
				return errors.New(message)
			}

			if *newLicense.Flag == 2 {
				message = "all fields except text were updated. text was updated manually and cannot be overwritten in an import."
				importStatus = IMPORT_LICENSE_UPDATED_EXCEPT_TEXT
				// error is not returned here as it will rollback the transaction
			} else {
				importStatus = IMPORT_LICENSE_UPDATED
			}
		} else {
			// case when license doesn't exist in database and is inserted

			if err := AddChangelogsForLicense(tx, username, &oldLicense, &models.LicenseDB{}); err != nil {
				message = fmt.Sprintf("failed to create license: %s", err.Error())
				importStatus = IMPORT_FAILED
				return errors.New(message)
			}

			importStatus = IMPORT_LICENSE_CREATED
		}

		return nil
	})

	if importStatus == IMPORT_FAILED {
		red := "\033[31m"
		reset := "\033[0m"
		log.Printf("%s%s: %s%s", red, *license.Shortname, message, reset)
	} else {
		green := "\033[32m"
		reset := "\033[0m"
		log.Printf("%sImport for license '%s' successful%s", green, *license.Shortname, reset)
	}
	return message, importStatus
}

// GenerateDiffForReplacingLicenses creates list of license associations to be created and deleted such that the list of currently associated
// licenses to a obligation is overwritten by the list provided in the param newLicenseAssociations
func GenerateDiffForReplacingLicenses(obligation *models.Obligation, newLicenseAssociations []string, removeLicenses, insertLicenses *[]string) {
	// if license in currently associated with the obligation but isn't in newLicenseAssociations, remove it
	for _, lic := range obligation.Licenses {
		found := false
		for _, shortname := range newLicenseAssociations {
			if shortname == *lic.Shortname {
				found = true
				break
			}
		}
		if !found {
			*removeLicenses = append(*removeLicenses, *lic.Shortname)
		}
	}

	// if license in newLicenseAssociations but not currently associated with the obligation, insert it
	for _, shortname := range newLicenseAssociations {
		found := false
		for _, lic := range obligation.Licenses {
			if shortname == *lic.Shortname {
				found = true
				break
			}
		}
		if !found {
			*insertLicenses = append(*insertLicenses, shortname)
		}
	}
}

// PerformObligationMapActions created associations for licenses in insertLicenses and deletes
// associations for licenses in removeLicenses. It also calculates changelog for the changes.
// It returns the final list of associated licenses.
func PerformObligationMapActions(username string, obligation *models.Obligation,
	removeLicenses, insertLicenses []string) ([]string, []error) {
	createLicenseAssociations := []models.LicenseDB{}
	deleteLicenseAssociations := []models.LicenseDB{}
	var oldLicenseAssociations, newLicenseAssociations []string
	var errs []error

	for _, lic := range obligation.Licenses {
		oldLicenseAssociations = append(oldLicenseAssociations, *lic.Shortname)
	}

	for _, lic := range insertLicenses {
		var license models.LicenseDB
		if err := db.DB.Where(models.LicenseDB{Shortname: &lic}).First(&license).Error; err != nil {
			errs = append(errs, fmt.Errorf("unable to associate license '%s' to obligation '%s': %s", lic, *obligation.Topic, err.Error()))
		} else {
			createLicenseAssociations = append(createLicenseAssociations, license)
		}
	}

	for _, lic := range removeLicenses {
		var license models.LicenseDB
		if err := db.DB.Where(models.LicenseDB{Shortname: &lic}).First(&license).Error; err != nil {
			errs = append(errs, fmt.Errorf("unable to remove license '%s' from obligation '%s': %s", lic, *obligation.Topic, err.Error()))
		} else {
			deleteLicenseAssociations = append(deleteLicenseAssociations, license)
		}
	}

	if err := db.DB.Transaction(func(tx *gorm.DB) error {

		if len(createLicenseAssociations) == 0 && len(deleteLicenseAssociations) == 0 {
			for _, lic := range obligation.Licenses {
				newLicenseAssociations = append(newLicenseAssociations, *lic.Shortname)
			}
			return nil
		}

		if err := tx.Session(&gorm.Session{SkipHooks: true}).Model(obligation).Association("Licenses").Append(createLicenseAssociations); err != nil {
			return err
		}
		if err := tx.Session(&gorm.Session{SkipHooks: true}).Model(obligation).Association("Licenses").Delete(deleteLicenseAssociations); err != nil {
			return err
		}

		for _, lic := range obligation.Licenses {
			newLicenseAssociations = append(newLicenseAssociations, *lic.Shortname)
		}

		return createObligationMapChangelog(tx, username, newLicenseAssociations, oldLicenseAssociations, obligation)
	}); err != nil {
		errs = append(errs, err)
	}
	return newLicenseAssociations, errs
}

// createObligationMapChangelog creates the changelog for the obligation map changes.
func createObligationMapChangelog(tx *gorm.DB, username string,
	newLicenseAssociations, oldLicenseAssociations []string, obligation *models.Obligation) error {
	oldVal := strings.Join(oldLicenseAssociations, ", ")
	newVal := strings.Join(newLicenseAssociations, ", ")

	var changes []models.ChangeLog
	AddChangelog("Licenses", &oldVal, &newVal, &changes)

	var user models.User
	if err := tx.Where(models.User{UserName: &username}).First(&user).Error; err != nil {
		return err
	}

	audit := models.Audit{
		UserId:     user.Id,
		TypeId:     obligation.Id,
		Timestamp:  time.Now(),
		Type:       "OBLIGATION",
		ChangeLogs: changes,
	}

	if err := tx.Create(&audit).Error; err != nil {
		return err
	}

	return nil
}

func AddChangelogForObligationType(tx *gorm.DB, username string, oldObType, newObType *models.ObligationType) error {
	var user models.User
	if err := tx.Where(models.User{UserName: &username}).First(&user).Error; err != nil {
		return errors.New("unable to update obligation type")
	}

	var changes []models.ChangeLog
	AddChangelog("Active", oldObType.Active, newObType.Active, &changes)
	AddChangelog("Type", &oldObType.Type, &newObType.Type, &changes)

	if len(changes) != 0 {
		audit := models.Audit{
			UserId:     user.Id,
			TypeId:     newObType.Id,
			Timestamp:  time.Now(),
			Type:       "TYPE",
			ChangeLogs: changes,
		}

		if err := tx.Create(&audit).Error; err != nil {
			return errors.New("unable to update obligation type")
		}
	}

	return nil
}

func ToggleObligationTypeActiveStatus(username string, tx *gorm.DB, obType *models.ObligationType) error {
	newObType := *obType
	newActive := !*obType.Active
	newObType.Active = &newActive
	if err := tx.Clauses(clause.Returning{}).Updates(&newObType).Error; err != nil {
		return errors.New("unable to change 'active' status of obligation type")
	}

	return AddChangelogForObligationType(tx, username, obType, &newObType)
}

func AddChangelogForObligationClassification(tx *gorm.DB, username string, oldObClassification, newObClassification *models.ObligationClassification) error {
	var user models.User
	if err := tx.Where(models.User{UserName: &username}).First(&user).Error; err != nil {
		return errors.New("unable to update obligation classification")
	}

	var changes []models.ChangeLog
	AddChangelog("Active", oldObClassification.Active, newObClassification.Active, &changes)
	AddChangelog("Classification", &oldObClassification.Classification, &newObClassification.Classification, &changes)

	if len(changes) != 0 {
		audit := models.Audit{
			UserId:     user.Id,
			TypeId:     newObClassification.Id,
			Timestamp:  time.Now(),
			Type:       "CLASSIFICATION",
			ChangeLogs: changes,
		}

		if err := tx.Create(&audit).Error; err != nil {
			return errors.New("unable to update obligation classification")
		}
	}

	return nil
}

func ToggleObligationClassificationActiveStatus(username string, tx *gorm.DB, obClassification *models.ObligationClassification) error {
	newObClassification := *obClassification
	newActive := !*obClassification.Active
	newObClassification.Active = &newActive
	if err := tx.Clauses(clause.Returning{}).Updates(&newObClassification).Error; err != nil {
		return errors.New("unable to change 'active' status of obligation classification")
	}

	return AddChangelogForObligationClassification(tx, username, obClassification, &newObClassification)
}

// ObligationTypeStatusCode is internally used for checking status of a obligation type creation
type ObligationFieldCreateStatusCode int

// Status codes covering various scenarios that can occur on a license import
const (
	CREATE_FAILED ObligationFieldCreateStatusCode = iota + 1
	VALIDATION_FAILED
	CONFLICT
	CONFLICT_ACTIVATION_FAILED
	CREATED
)

func CreateObType(obType *models.ObligationType, username string) (error, ObligationFieldCreateStatusCode) {
	validate := validator.New(validator.WithRequiredStructEnabled())
	if err := validate.Struct(obType); err != nil {
		return err, VALIDATION_FAILED
	}

	var status ObligationFieldCreateStatusCode
	err := db.DB.Transaction(func(tx *gorm.DB) error {
		result := tx.Where(&models.ObligationType{Type: obType.Type}).FirstOrCreate(&obType)
		if result.Error != nil {
			status = CREATE_FAILED
			return result.Error
		}
		if result.RowsAffected == 0 {
			if *obType.Active {
				status = CONFLICT
				return errors.New("obligation type already exists")
			}
			if err := ToggleObligationTypeActiveStatus(username, tx, obType); err != nil {
				status = CONFLICT_ACTIVATION_FAILED
				return err
			}
		} else {
			if err := AddChangelogForObligationType(tx, username, &models.ObligationType{}, obType); err != nil {
				status = CREATE_FAILED
				return err
			}
		}

		status = CREATED
		return nil
	})

	return err, status
}

func CreateObClassification(obClassification *models.ObligationClassification, username string) (error, ObligationFieldCreateStatusCode) {
	validate := validator.New(validator.WithRequiredStructEnabled())
	if err := validate.Struct(obClassification); err != nil {
		return err, VALIDATION_FAILED
	}

	var status ObligationFieldCreateStatusCode
	err := db.DB.Transaction(func(tx *gorm.DB) error {
		result := tx.Where(&models.ObligationClassification{Classification: obClassification.Classification}).FirstOrCreate(&obClassification)
		if result.Error != nil {
			status = CREATE_FAILED
			return result.Error
		}
		if result.RowsAffected == 0 {
			if *obClassification.Active {
				status = CONFLICT
				return errors.New("obligation classification already exists")
			}
			if err := ToggleObligationClassificationActiveStatus(username, tx, obClassification); err != nil {
				status = CONFLICT_ACTIVATION_FAILED
				return err
			}
		} else {
			if err := AddChangelogForObligationClassification(tx, username, &models.ObligationClassification{}, obClassification); err != nil {
				status = CREATE_FAILED
				return err
			}
		}

		status = CREATED
		return nil
	})

	return err, status
}

// Populatedb populates the database with license data from a JSON file.
func Populatedb(datafile string) {
	var licenses []models.LicenseJson
	// Read the content of the data file.
	byteResult, err := os.ReadFile(datafile)
	if err != nil {
		log.Fatalf("Unable to read JSON file: %v", err)
	}
	// Unmarshal the JSON file data into a slice of LicenseJson structs.
	if err := json.Unmarshal(byteResult, &licenses); err != nil {
		log.Fatalf("error reading from json file: %v", err)
	}

	user := models.User{}
	level := "SUPER_ADMIN"
	if err := db.DB.Where(&models.User{UserLevel: &level}).First(&user).Error; err != nil {
		log.Fatalf("Failed to find a super admin")
	}

	for _, license := range licenses {
		result := Converter(license)
		_, _ = InsertOrUpdateLicenseOnImport(&result, &models.UpdateExternalRefsJSONPayload{ExternalRef: make(map[string]interface{})}, *user.UserName)
	}

	DEFAULT_OBLIGATION_TYPES := []*models.ObligationType{
		{Type: "OBLIGATION"},
		{Type: "RISK"},
		{Type: "RESTRICTION"},
		{Type: "RIGHT"},
	}

	for _, obType := range DEFAULT_OBLIGATION_TYPES {
		err, status := CreateObType(obType, *user.UserName)

		if status == CREATED || status == CONFLICT {
			green := "\033[32m"
			reset := "\033[0m"
			log.Printf("%s%s: %s%s", green, obType.Type, "Obligation type created successfully", reset)
		} else {
			red := "\033[31m"
			reset := "\033[0m"
			log.Printf("%s%s: %s%s", red, obType.Type, err.Error(), reset)
		}
	}

	DEFAULT_OBLIGATION_CLASSIFICATIONS := []*models.ObligationClassification{
		{Classification: "GREEN", Color: "#00FF00"},
		{Classification: "WHITE", Color: "#FFFFFF"},
		{Classification: "YELLOW", Color: "#FFDE21"},
		{Classification: "RED", Color: "#FF0000"},
	}

	for _, obClassification := range DEFAULT_OBLIGATION_CLASSIFICATIONS {
		err, status := CreateObClassification(obClassification, *user.UserName)

		if status == CREATED || status == CONFLICT {
			green := "\033[32m"
			reset := "\033[0m"
			log.Printf("%s%s: %s%s", green, obClassification.Classification, "Obligation classification created successfully", reset)
		} else {
			red := "\033[31m"
			reset := "\033[0m"
			log.Printf("%s%s: %s%s", red, obClassification.Classification, err.Error(), reset)
		}
	}
}

// GetAuditEntity is an utility function to fetch obligation or license associated with an audit
func GetAuditEntity(c *gin.Context, audit *models.Audit) error {
	if audit.Type == "LICENSE" {
		audit.Entity = &models.LicenseDB{}
		if err := db.DB.Where(&models.LicenseDB{Id: audit.TypeId}).First(&audit.Entity).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusNotFound,
				Message:   "license corresponding with this audit does not exist",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusNotFound, er)
			return err
		}
	} else if audit.Type == "OBLIGATION" {
		audit.Entity = &models.Obligation{}
		if err := db.DB.Joins("Type").Joins("Classification").Where(&models.Obligation{Id: audit.TypeId}).First(&audit.Entity).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusNotFound,
				Message:   "obligation corresponding with this audit does not exist",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusNotFound, er)
			return err
		}
	} else if audit.Type == "TYPE" {
		audit.Entity = &models.ObligationType{}
		if err := db.DB.Where(&models.ObligationType{Id: audit.TypeId}).First(&audit.Entity).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusNotFound,
				Message:   "obligation type corresponding with this audit does not exist",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusNotFound, er)
			return err
		}
	} else if audit.Type == "CLASSIFICATION" {
		audit.Entity = &models.ObligationClassification{}
		if err := db.DB.Where(&models.ObligationClassification{Id: audit.TypeId}).First(&audit.Entity).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusNotFound,
				Message:   "obligation classification corresponding with this audit does not exist",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusNotFound, er)
			return err
		}
	}
	return nil
}

// https://github.com/lestrrat-go/jwx/discussions/547
// Get kid field value from JWS Header
func GetKid(token string) (string, error) {
	type JWSHeader struct {
		KeyID string `json:"kid"`
	}

	parts := strings.Split(token, ".")

	decodedBytes, err := base64.StdEncoding.DecodeString(parts[0])
	if err != nil {
		return "", err
	}

	var header JWSHeader
	err = json.Unmarshal(decodedBytes, &header)
	return header.KeyID, err
}

func AddChangelog[T any](fieldName string, oldValue, newValue *T, changes *[]models.ChangeLog) {
	var _oldValue, _newValue string
	if oldValue != nil {
		_oldValue = fmt.Sprintf("%v", *oldValue)
	} else {
		_oldValue = ""
	}
	if newValue != nil {
		_newValue = fmt.Sprintf("%v", *newValue)
	} else {
		_newValue = ""
	}
	if _oldValue != _newValue {
		*changes = append(*changes, models.ChangeLog{
			Field:        fieldName,
			OldValue:     &_oldValue,
			UpdatedValue: &_newValue,
		})
	}
}

// AddChangelogsForLicense adds changelogs for the updated fields on license update
func AddChangelogsForLicense(tx *gorm.DB, username string,
	newLicense, oldLicense *models.LicenseDB) error {
	var changes []models.ChangeLog

	AddChangelog("Fullname", oldLicense.Fullname, newLicense.Fullname, &changes)

	AddChangelog("Url", oldLicense.Url, newLicense.Url, &changes)

	oldVal := oldLicense.AddDate.Format(time.RFC3339)
	newVal := newLicense.AddDate.Format(time.RFC3339)
	AddChangelog("Add Date", &oldVal, &newVal, &changes)

	AddChangelog("Active", oldLicense.Active, newLicense.Active, &changes)
	AddChangelog("Copyleft", oldLicense.Copyleft, newLicense.Copyleft, &changes)
	AddChangelog("FSF Free", oldLicense.FSFfree, newLicense.FSFfree, &changes)
	AddChangelog("GPLv2 Compatible", oldLicense.GPLv2compatible, newLicense.GPLv2compatible, &changes)
	AddChangelog("GPLv3 Compatible", oldLicense.GPLv3compatible, newLicense.GPLv3compatible, &changes)
	AddChangelog("OSI Approved", oldLicense.OSIapproved, newLicense.OSIapproved, &changes)
	AddChangelog("Text", oldLicense.Text, newLicense.Text, &changes)
	AddChangelog("Text Updatable", oldLicense.TextUpdatable, newLicense.TextUpdatable, &changes)
	AddChangelog("Fedora", oldLicense.Fedora, newLicense.Fedora, &changes)
	AddChangelog("Flag", oldLicense.Flag, newLicense.Flag, &changes)
	AddChangelog("Notes", oldLicense.Notes, newLicense.Notes, &changes)
	AddChangelog("DetectorType", oldLicense.DetectorType, newLicense.DetectorType, &changes)
	AddChangelog("Source", oldLicense.Source, newLicense.Source, &changes)
	AddChangelog("Spdx Id", oldLicense.SpdxId, newLicense.SpdxId, &changes)
	AddChangelog("Risk", oldLicense.Risk, newLicense.Risk, &changes)
	AddChangelog("Marydone", oldLicense.Marydone, newLicense.Marydone, &changes)

	oldLicenseExternalRef := oldLicense.ExternalRef.Data()
	oldExternalRefVal := reflect.ValueOf(oldLicenseExternalRef)
	typesOf := oldExternalRefVal.Type()

	newLicenseExternalRef := newLicense.ExternalRef.Data()
	newExternalRefVal := reflect.ValueOf(newLicenseExternalRef)

	for i := 0; i < oldExternalRefVal.NumField(); i++ {
		fieldName := typesOf.Field(i).Name

		switch typesOf.Field(i).Type.String() {
		case "*boolean":
			oldFieldPtr, _ := oldExternalRefVal.Field(i).Interface().(*bool)
			newFieldPtr, _ := newExternalRefVal.Field(i).Interface().(*bool)
			AddChangelog(fmt.Sprintf("External Reference %s", fieldName), oldFieldPtr, newFieldPtr, &changes)
		case "*string":
			oldFieldPtr, _ := oldExternalRefVal.Field(i).Interface().(*string)
			newFieldPtr, _ := newExternalRefVal.Field(i).Interface().(*string)
			AddChangelog(fmt.Sprintf("External Reference %s", fieldName), oldFieldPtr, newFieldPtr, &changes)
		case "*int":
			oldFieldPtr, _ := oldExternalRefVal.Field(i).Interface().(*int)
			newFieldPtr, _ := newExternalRefVal.Field(i).Interface().(*int)
			AddChangelog(fmt.Sprintf("External Reference %s", fieldName), oldFieldPtr, newFieldPtr, &changes)
		}
	}

	if len(changes) != 0 {
		var user models.User
		if err := tx.Where(models.User{UserName: &username}).First(&user).Error; err != nil {
			return err
		}

		audit := models.Audit{
			UserId:     user.Id,
			TypeId:     newLicense.Id,
			Timestamp:  time.Now(),
			Type:       "LICENSE",
			ChangeLogs: changes,
		}

		if err := tx.Create(&audit).Error; err != nil {
			return err
		}
	}

	return nil
}

// AddChangelogsForUser adds changelogs for the updated fields on user update
func AddChangelogsForUser(tx *gorm.DB, username string,
	newUser, oldUser *models.User) error {
	var changes []models.ChangeLog

	AddChangelog("UserName", oldUser.UserName, newUser.UserName, &changes)
	AddChangelog("DisplayName", oldUser.DisplayName, newUser.DisplayName, &changes)
	AddChangelog("UserEmail", oldUser.UserEmail, newUser.UserEmail, &changes)
	AddChangelog("UserLevel", oldUser.UserLevel, newUser.UserLevel, &changes)
	AddChangelog("Active", oldUser.Active, newUser.Active, &changes)

	if len(changes) != 0 {
		var user models.User
		if err := tx.Where(models.User{UserName: &username}).First(&user).Error; err != nil {
			return err
		}

		audit := models.Audit{
			UserId:     user.Id,
			TypeId:     newUser.Id,
			Timestamp:  time.Now(),
			Type:       "USER",
			ChangeLogs: changes,
		}

		if err := tx.Create(&audit).Error; err != nil {
			return err
		}
	}

	return nil

}
