// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package main

import (
	"flag"
	"log"

	_ "github.com/fossology/LicenseDb/cmd/laas/docs"
	"github.com/fossology/LicenseDb/pkg/api"
	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
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

	db.Connect(dbhost, port, user, dbname, password)

	if err := db.DB.AutoMigrate(&models.LicenseDB{}); err != nil {
		log.Fatalf("Failed to automigrate database: %v", err)
	}

	if err := db.DB.AutoMigrate(&models.User{}); err != nil {
		log.Fatalf("Failed to automigrate database: %v", err)
	}

	if err := db.DB.AutoMigrate(&models.Audit{}); err != nil {
		log.Fatalf("Failed to automigrate database: %v", err)
	}

	if err := db.DB.AutoMigrate(&models.ChangeLog{}); err != nil {
		log.Fatalf("Failed to automigrate database: %v", err)
	}

	if err := db.DB.AutoMigrate(&models.Obligation{}); err != nil {
		log.Fatalf("Failed to automigrate database: %v", err)
	}

	if err := db.DB.AutoMigrate(&models.ObligationMap{}); err != nil {
		log.Fatalf("Failed to automigrate database: %v", err)
	}

	if *populatedb == true {
		db.Populatedb(*datafile)
	}

	r := api.Router()

	r.Run()
}
