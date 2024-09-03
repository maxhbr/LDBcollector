// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-License-Identifier: GPL-2.0-only

package db

import (
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"os"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"

	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
)

// DB is a global variable to store the GORM database connection.
var DB *gorm.DB

// Connect establishes a connection to the database using the provided parameters.
func Connect(dbhost, port, user, dbname, password *string) {

	dburi := fmt.Sprintf("host=%s port=%s user=%s dbname=%s password=%s", *dbhost, *port, *user, *dbname, *password)
	gormConfig := &gorm.Config{}
	database, err := gorm.Open(postgres.Open(dburi), gormConfig)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	DB = database
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
	for _, license := range licenses {
		result := utils.Converter(license)
		_ = DB.Transaction(func(tx *gorm.DB) error {
			errMessage, importStatus, _, _ := utils.InsertOrUpdateLicenseOnImport(tx, &result, &models.UpdateExternalRefsJSONPayload{ExternalRef: make(map[string]interface{})})
			if importStatus == utils.IMPORT_FAILED {
				// ANSI escape code for red text
				red := "\033[31m"
				reset := "\033[0m"
				log.Printf("%s%s: %s%s", red, *result.Shortname, errMessage, reset)
				return errors.New(errMessage)
			}
			return nil
		})

	}
}
