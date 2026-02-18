// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package utils

import (
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
	"github.com/google/uuid"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/validations"
)

var (
	// DefaultPage Set default page to 1
	DefaultPage int64 = 1
	// DefaultLimit Set default max limit to 20
	DefaultLimit int64 = 20
)

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
)

func InsertOrUpdateLicenseOnImport(lic *models.LicenseImportDTO, userId uuid.UUID) (string, LicenseImportStatusCode) {
	var message string
	var importStatus LicenseImportStatusCode

	if err := validations.Validate.Struct(lic); err != nil {
		message = fmt.Sprintf("field '%s' failed validation: %s\n", err.(validator.ValidationErrors)[0].Field(), err.(validator.ValidationErrors)[0].Tag())
		importStatus = IMPORT_FAILED
		return message, importStatus
	}

	_ = db.DB.Transaction(func(tx *gorm.DB) error {
		license := lic.ConvertToLicenseDB()
		license.UserId = userId

		if lic.Id != nil {
			var newLicense, oldLicense models.LicenseDB
			if err := tx.Where(models.LicenseDB{Id: *lic.Id}).First(&oldLicense).Error; err != nil {
				message = fmt.Sprintf("cannot find license: %s", err.Error())
				importStatus = IMPORT_FAILED
				return errors.New(message)
			}
			newLicense = license

			if *oldLicense.Text != *newLicense.Text {
				if !*oldLicense.TextUpdatable {
					message = "Field `text_updatable` needs to be true to update the text"
					importStatus = IMPORT_FAILED
					return errors.New("Field `text_updatable` needs to be true to update the text")
				}
			}

			// Overwrite values of existing keys, add new key value pairs and remove keys with null values.
			if err := tx.Model(&models.LicenseDB{}).Where(models.LicenseDB{Id: oldLicense.Id}).UpdateColumn("external_ref", gorm.Expr("jsonb_strip_nulls(COALESCE(external_ref, '{}'::jsonb) || ?)", &lic.ExternalRef)).Error; err != nil {
				message = fmt.Sprintf("failed to update license: %s", err.Error())
				importStatus = IMPORT_FAILED
				return errors.New(message)
			}

			// Update all other fields except external_ref and rf_shortname
			query := tx.Where(&models.LicenseDB{Id: oldLicense.Id}).Omit("ExternalRef", "Obligations", "User")

			if err := query.Clauses(clause.Returning{}).Updates(&newLicense).Scan(&newLicense).Error; err != nil {
				message = fmt.Sprintf("failed to update license: %s", err.Error())
				importStatus = IMPORT_FAILED
				return errors.New(message)
			}

			// for setting api response
			lic.Id = &newLicense.Id
			lic.Shortname = newLicense.Shortname

			if err := AddChangelogsForLicense(tx, userId, &newLicense, &oldLicense); err != nil {
				message = fmt.Sprintf("failed to update license: %s", err.Error())
				importStatus = IMPORT_FAILED
				return errors.New(message)
			}

			importStatus = IMPORT_LICENSE_UPDATED
		} else {
			// case when license doesn't exist in database and is inserted
			if err := tx.Create(&license).Error; err != nil {
				message = fmt.Sprintf("failed to import license: %s", err.Error())
				importStatus = IMPORT_FAILED
				return errors.New(message)
			}

			// for setting api response
			lic.Id = &license.Id
			lic.Shortname = license.Shortname

			if err := AddChangelogsForLicense(tx, userId, &license, &models.LicenseDB{}); err != nil {
				message = fmt.Sprintf("failed to create license: %s", err.Error())
				importStatus = IMPORT_FAILED
				return errors.New(message)
			}

			importStatus = IMPORT_LICENSE_CREATED
		}

		return nil
	})

	if importStatus == IMPORT_FAILED {
		erroredElem := ""
		if lic.Id != nil {
			erroredElem = (*lic.Id).String()
		} else if lic.Shortname != nil {
			erroredElem = *lic.Shortname
		}
		red := "\033[31m"
		reset := "\033[0m"
		log.Printf("%s%s: %s%s", red, erroredElem, message, reset)
	} else {
		green := "\033[32m"
		reset := "\033[0m"
		log.Printf("%sImport for license '%s' successful%s", green, (*lic.Id).String(), reset)
	}
	return message, importStatus
}

// GenerateDiffForReplacingLicenses creates list of license associations to be created and deleted such that the list of currently associated
// licenses to a obligation is overwritten by the list provided in the param newLicenseAssociations
func GenerateDiffForReplacingLicenses(obligation *models.Obligation, newLicenseAssociations []uuid.UUID, removeLicenses, insertLicenses *[]uuid.UUID) {
	// if license in currently associated with the obligation but isn't in newLicenseAssociations, remove it
	for _, lic := range obligation.Licenses {
		found := false
		for _, id := range newLicenseAssociations {
			if id == lic.Id {
				found = true
				break
			}
		}
		if !found {
			*removeLicenses = append(*removeLicenses, lic.Id)
		}
	}

	// if license in newLicenseAssociations but not currently associated with the obligation, insert it
	for _, id := range newLicenseAssociations {
		found := false
		for _, lic := range obligation.Licenses {
			if id == lic.Id {
				found = true
				break
			}
		}
		if !found {
			*insertLicenses = append(*insertLicenses, id)
		}
	}
}

// PerformObligationMapActions created associations for licenses in insertLicenses and deletes
// associations for licenses in removeLicenses. It also calculates changelog for the changes.
// It returns the final list of associated licenses.
func PerformObligationMapActions(tx *gorm.DB, userId uuid.UUID, obligation *models.Obligation,
	removeLicenses, insertLicenses []uuid.UUID) ([]models.ObligationMapLicenseFormat, []error) {
	createLicenseAssociations := []models.LicenseDB{}
	deleteLicenseAssociations := []models.LicenseDB{}
	var oldLicenseAssociations, newLicenseAssociations []models.ObligationMapLicenseFormat
	var errs []error

	for _, lic := range obligation.Licenses {
		oldLicenseAssociations = append(oldLicenseAssociations, models.ObligationMapLicenseFormat{Id: lic.Id, Shortname: *lic.Shortname})
	}

	for _, licId := range insertLicenses {
		var license models.LicenseDB
		if err := tx.Where(models.LicenseDB{Id: licId}).First(&license).Error; err != nil {
			errs = append(errs, fmt.Errorf("unable to associate license '%s' to obligation '%s': %s", licId, obligation.Id, err.Error()))
		} else {
			createLicenseAssociations = append(createLicenseAssociations, license)
		}
	}

	for _, licId := range removeLicenses {
		var license models.LicenseDB
		if err := tx.Where(models.LicenseDB{Id: licId}).First(&license).Error; err != nil {
			errs = append(errs, fmt.Errorf("unable to remove license '%s' from obligation '%s': %s", licId, obligation.Id, err.Error()))
		} else {
			deleteLicenseAssociations = append(deleteLicenseAssociations, license)
		}
	}

	if err := tx.Transaction(func(tx1 *gorm.DB) error {

		if len(createLicenseAssociations) != 0 || len(deleteLicenseAssociations) != 0 {
			if err := tx1.Model(obligation).Association("Licenses").Append(createLicenseAssociations); err != nil {
				return err
			}
			if err := tx1.Model(obligation).Association("Licenses").Delete(deleteLicenseAssociations); err != nil {
				return err
			}
		}

		if err := tx.
			Preload("Licenses").
			Joins("Type").
			Joins("Classification").
			Where(&models.Obligation{Id: obligation.Id}).
			First(&obligation).Error; err != nil {
			return err
		}

		for _, lic := range obligation.Licenses {
			newLicenseAssociations = append(newLicenseAssociations, models.ObligationMapLicenseFormat{Id: lic.Id, Shortname: *lic.Shortname})
		}

		return createObligationMapChangelog(tx, userId, newLicenseAssociations, oldLicenseAssociations, obligation)
	}); err != nil {
		errs = append(errs, err)
	}
	return newLicenseAssociations, errs
}

// createObligationMapChangelog creates the changelog for the obligation map changes.
func createObligationMapChangelog(
	tx *gorm.DB,
	userId uuid.UUID,
	newLicenseAssociations, oldLicenseAssociations []models.ObligationMapLicenseFormat,
	obligation *models.Obligation,
) error {
	uuidsToStr := func(ids []models.ObligationMapLicenseFormat) string {
		if len(ids) == 0 {
			return ""
		}
		s := make([]string, 0, len(ids))
		for _, lic := range ids {
			s = append(s, lic.Id.String())
		}
		return strings.Join(s, ", ")
	}

	oldVal := uuidsToStr(oldLicenseAssociations)
	newVal := uuidsToStr(newLicenseAssociations)

	var changes []models.ChangeLog
	AddChangelog("Licenses", &oldVal, &newVal, &changes)

	audit := models.Audit{
		UserId:     userId,
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

func AddChangelogForObligationType(tx *gorm.DB, userId uuid.UUID, oldObType, newObType *models.ObligationType) error {
	var changes []models.ChangeLog
	AddChangelog("Active", oldObType.Active, newObType.Active, &changes)
	AddChangelog("Type", &oldObType.Type, &newObType.Type, &changes)

	if len(changes) != 0 {
		audit := models.Audit{
			UserId:     userId,
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

func ToggleObligationTypeActiveStatus(userId uuid.UUID, tx *gorm.DB, obType *models.ObligationType) error {
	newObType := *obType
	newActive := !*obType.Active
	newObType.Active = &newActive
	if err := tx.Clauses(clause.Returning{}).Updates(&newObType).Error; err != nil {
		return errors.New("unable to change 'active' status of obligation type")
	}

	return AddChangelogForObligationType(tx, userId, obType, &newObType)
}

func AddChangelogForObligationClassification(tx *gorm.DB, userId uuid.UUID, oldObClassification, newObClassification *models.ObligationClassification) error {
	var changes []models.ChangeLog
	AddChangelog("Active", oldObClassification.Active, newObClassification.Active, &changes)
	AddChangelog("Classification", &oldObClassification.Classification, &newObClassification.Classification, &changes)

	if len(changes) != 0 {
		audit := models.Audit{
			UserId:     userId,
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

func ToggleObligationClassificationActiveStatus(userId uuid.UUID, tx *gorm.DB, obClassification *models.ObligationClassification) error {
	newObClassification := *obClassification
	newActive := !*obClassification.Active
	newObClassification.Active = &newActive
	if err := tx.Clauses(clause.Returning{}).Updates(&newObClassification).Error; err != nil {
		return errors.New("unable to change 'active' status of obligation classification")
	}

	return AddChangelogForObligationClassification(tx, userId, obClassification, &newObClassification)
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

func CreateObType(obType *models.ObligationType, userId uuid.UUID) (error, ObligationFieldCreateStatusCode) {
	if err := validations.Validate.Struct(obType); err != nil {
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
			if err := ToggleObligationTypeActiveStatus(userId, tx, obType); err != nil {
				status = CONFLICT_ACTIVATION_FAILED
				return err
			}
		} else {
			if err := AddChangelogForObligationType(tx, userId, &models.ObligationType{}, obType); err != nil {
				status = CREATE_FAILED
				return err
			}
		}

		status = CREATED
		return nil
	})

	return err, status
}

func CreateObClassification(obClassification *models.ObligationClassification, userId uuid.UUID) (error, ObligationFieldCreateStatusCode) {
	if err := validations.Validate.Struct(obClassification); err != nil {
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
			if err := ToggleObligationClassificationActiveStatus(userId, tx, obClassification); err != nil {
				status = CONFLICT_ACTIVATION_FAILED
				return err
			}
		} else {
			if err := AddChangelogForObligationClassification(tx, userId, &models.ObligationClassification{}, obClassification); err != nil {
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
		result := license.Converter()
		if err := validations.Validate.Struct(&result); err != nil {
			red := "\033[31m"
			reset := "\033[0m"
			log.Printf("%s%s: %s%s", red, *result.Shortname, fmt.Sprintf("field '%s' failed validation: %s\n", err.(validator.ValidationErrors)[0].Field(), err.(validator.ValidationErrors)[0].Tag()), reset)
			continue
		}
		_, _ = InsertOrUpdateLicenseOnImport(&result, user.Id)
	}

	DEFAULT_OBLIGATION_TYPES := []*models.ObligationType{
		{Type: "OBLIGATION"},
		{Type: "RISK"},
		{Type: "RESTRICTION"},
		{Type: "RIGHT"},
	}

	for _, obType := range DEFAULT_OBLIGATION_TYPES {
		err, status := CreateObType(obType, user.Id)

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
		err, status := CreateObClassification(obClassification, user.Id)

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

// SetSimilarityThreshold parses the env var and sets the threshold in Postgres.
func SetSimilarityThreshold() {
	defaultThreshold := 0.7
	thresholdStr := os.Getenv("SIMILARITY_THRESHOLD")

	threshold := defaultThreshold
	if thresholdStr != "" {
		if parsed, err := strconv.ParseFloat(thresholdStr, 64); err == nil {
			threshold = parsed
		} else {
			log.Printf("Invalid SIMILARITY_THRESHOLD '%s', using default %.1f", thresholdStr, defaultThreshold)
		}
	} else {
		log.Printf("SIMILARITY_THRESHOLD not set, using default %.1f", defaultThreshold)
	}

	query := fmt.Sprintf("SET pg_trgm.similarity_threshold = %f", threshold)
	if err := db.DB.Exec(query).Error; err != nil {
		log.Println("Failed to set similarity threshold:", err)
	}
}

// GetAuditEntity is an utility function to fetch obligation or license associated with an audit
func GetAuditEntity(c *gin.Context, audit *models.Audit) error {
	switch audit.Type {
	case "LICENSE":
		var lic models.LicenseDB
		if err := db.DB.Where(&models.LicenseDB{Id: audit.TypeId}).First(&lic).Error; err != nil {
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
		audit.Entity = lic.ConvertToLicenseResponseDTO()
	case "OBLIGATION":
		var ob models.Obligation
		if err := db.DB.Joins("Type").Joins("Classification").Where(&models.Obligation{Id: audit.TypeId}).First(&ob).Error; err != nil {
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
		audit.Entity = ob.ConvertToObligationResponseDTO()
	case "TYPE":
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
	case "CLASSIFICATION":
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
	case "USER":
		audit.Entity = &models.User{}
		if err := db.DB.Where(&models.User{Id: audit.TypeId}).First(&audit.Entity).Error; err != nil {
			er := models.LicenseError{
				Status:    http.StatusNotFound,
				Message:   "user corresponding with this audit does not exist",
				Error:     err.Error(),
				Path:      c.Request.URL.Path,
				Timestamp: time.Now().Format(time.RFC3339),
			}
			c.JSON(http.StatusNotFound, er)
			return err
		}
	default:
		// no action
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
func AddChangelogsForLicense(tx *gorm.DB, userId uuid.UUID,
	newLicense, oldLicense *models.LicenseDB) error {
	var changes []models.ChangeLog

	AddChangelog("Fullname", oldLicense.Fullname, newLicense.Fullname, &changes)
	AddChangelog("Url", oldLicense.Url, newLicense.Url, &changes)
	AddChangelog("Active", oldLicense.Active, newLicense.Active, &changes)
	AddChangelog("Copyleft", oldLicense.Copyleft, newLicense.Copyleft, &changes)
	AddChangelog("OSI Approved", oldLicense.OSIapproved, newLicense.OSIapproved, &changes)
	AddChangelog("Text", oldLicense.Text, newLicense.Text, &changes)
	AddChangelog("Text Updatable", oldLicense.TextUpdatable, newLicense.TextUpdatable, &changes)
	AddChangelog("Notes", oldLicense.Notes, newLicense.Notes, &changes)
	AddChangelog("Source", oldLicense.Source, newLicense.Source, &changes)
	AddChangelog("Spdx Id", oldLicense.SpdxId, newLicense.SpdxId, &changes)
	AddChangelog("Risk", oldLicense.Risk, newLicense.Risk, &changes)

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
		if err := tx.Where(models.User{Id: userId}).First(&user).Error; err != nil {
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
func AddChangelogsForUser(tx *gorm.DB, userId uuid.UUID,
	newUser, oldUser *models.User) error {
	var changes []models.ChangeLog

	AddChangelog("UserName", oldUser.UserName, newUser.UserName, &changes)
	AddChangelog("DisplayName", oldUser.DisplayName, newUser.DisplayName, &changes)
	AddChangelog("UserEmail", oldUser.UserEmail, newUser.UserEmail, &changes)
	AddChangelog("UserLevel", oldUser.UserLevel, newUser.UserLevel, &changes)
	AddChangelog("Active", oldUser.Active, newUser.Active, &changes)

	if len(changes) != 0 {
		var user models.User
		if err := tx.Where(models.User{Id: userId}).First(&user).Error; err != nil {
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
