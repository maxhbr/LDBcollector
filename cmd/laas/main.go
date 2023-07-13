// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-License-Identifier: GPL-2.0-only

package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"log"

	"github.com/fossology/LicenseDb/pkg/api"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/gin-gonic/gin"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

// declare flags to input the basic requirement of database connection and the path of the data file
var (
	// argument to enter the name of database host
	dbhost = flag.String("host", "localhost", "host name")
	// port number of the host
	port = flag.String("port", "5432", "port number")
	// argument to enter the database user
	user = flag.String("user", "fossy", "user name")
	// name of database to be connected
	dbname = flag.String("dbname", "fossology", "database name")
	// password of the database
	password = flag.String("password", "fossy", "password")
	// path of data file
	datafile = flag.String("datafile", "licenseRef.json", "datafile path")
	// auto-update the database
	populatedb = flag.Bool("populatedb", false, "boolean variable to update database")
)

func main() {
	flag.Parse()

	dburi := fmt.Sprintf("host=%s port=%s user=%s dbname=%s password=%s", *dbhost, *port, *user, *dbname, *password)
	gormConfig := &gorm.Config{}
	database, err := gorm.Open(postgres.Open(dburi), gormConfig)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	if err := database.AutoMigrate(&models.LicenseDB{}); err != nil {
		log.Fatalf("Failed to automigrate database: %v", err)
	}

	if *populatedb {
		var licenses []models.LicenseJson
		// read the file of data
		byteResult, _ := ioutil.ReadFile(*datafile)
		// unmarshal the json file and it into the struct format
		if err := json.Unmarshal(byteResult, &licenses); err != nil {
			log.Fatalf("error reading from json file: %v", err)
		}
		for _, license := range licenses {
			// populate the data in the database table
			result := utils.Converter(license)
			database.Create(&result)
		}
	}
	api.DB = database

	r := gin.Default()
	r.NoRoute(api.HandleInvalidUrl)
	r.GET("/api/licenses", api.GetAllLicense)
	r.GET("/api/license/:shortname", api.GetLicense)
	r.POST("/api/license", api.CreateLicense)
	r.PATCH("/api/license/:shortname", api.UpdateLicense)
	r.Run()
}
