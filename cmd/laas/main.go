// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-License-Identifier: GPL-2.0-only

package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"

	"github.com/fossology/LicenseDb/pkg/models"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

// declare flags to input the basic requirement of database connection and the path of the data file
var (
	// argument to enter the name of database host
	dbhost = flag.String("host", "localhost", "host name")
	// argument to enter the port number of the host
	port = flag.String("port", "5432", "port number")
	// argument to enter the name of database user
	user = flag.String("user", "fossy", "user name")
	// argument to enter the name to database to be connected
	dbname = flag.String("dbname", "fossology", "database name")
	// argument to enter the password of the user
	password = flag.String("password", "fossy", "password")
	// argument to enter the path of data file
	datafile = flag.String("datafile", "licenseRef.json", "datafile path")
)

func main() {
	flag.Parse()

	dburi := fmt.Sprintf("host=%s port=%s user=%s dbname=%s password=%s", *dbhost, *port, *user, *dbname, *password)
	gormConfig := &gorm.Config{}
	database, err := gorm.Open(postgres.Open(dburi), gormConfig)
	if err != nil {
		panic("Failed to connect to database!")
	}

	err = database.AutoMigrate(&models.License{})
	if err != nil {
		return
	}

	var licenses []models.License
	// read the file of data
	byteResult, _ := ioutil.ReadFile(*datafile)
	// unmarshal the json file and make it into the struct format
	json.Unmarshal(byteResult, &licenses)
	for _, license := range licenses {
		// populate the data in the database table
		database.Create(&license)
	}
}
