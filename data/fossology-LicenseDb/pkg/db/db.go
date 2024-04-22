// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-License-Identifier: GPL-2.0-only

package db

import (
	"encoding/json"
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
		var existingLicense models.LicenseDB
		// Create the license if it does not already exist in the database.
		// Otherwise, update the license if flag is 1.
		result := utils.Converter(license)
		DB.Where(models.LicenseDB{Shortname: result.Shortname}).First(&existingLicense)
		// check if existingLicense found
		if existingLicense.Id != 0 && existingLicense.Flag == 2 {
			// Do not update the license where text was updated manually.
			continue
		}
		err := DB.Where(models.LicenseDB{Shortname: result.Shortname}).Assign(result).
			FirstOrCreate(&result).Error
		if err != nil {
			log.Fatalf("error creating license: %v", err)
		}
	}
}
