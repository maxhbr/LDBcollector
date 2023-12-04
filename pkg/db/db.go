// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-License-Identifier: GPL-2.0-only

package db

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"

	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
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

// Populatedb populates the database with license data from a JSON file if 'populatedb' is true.
func Populatedb(populatedb bool, datafile string) {
	if populatedb {
		var licenses []models.LicenseJson
		// Read the content of the data file.
		byteResult, _ := ioutil.ReadFile(datafile)
		// Unmarshal the JSON file data into a slice of LicenseJson structs.
		if err := json.Unmarshal(byteResult, &licenses); err != nil {
			log.Fatalf("error reading from json file: %v", err)
		}
		for _, license := range licenses {
			// populate the data in the database table
			result := utils.Converter(license)
			DB.Create(&result)
		}
	}
}
