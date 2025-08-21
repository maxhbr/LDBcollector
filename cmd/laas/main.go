// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package main

import (
	"context"
	"flag"
	"log"
	"os"

	"github.com/joho/godotenv"
	"github.com/lestrrat-go/httprc/v3"
	"github.com/lestrrat-go/jwx/v3/jwk"

	_ "github.com/dave/jennifer/jen"
	_ "github.com/fossology/LicenseDb/cmd/laas/docs"
	"github.com/fossology/LicenseDb/pkg/api"
	"github.com/fossology/LicenseDb/pkg/auth"
	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/fossology/LicenseDb/pkg/validations"
)

// declare flags to input the basic requirement of database connection and the path of the data file
var (
	datafile = flag.String("datafile", "licenseRef.json", "datafile path")
	// auto-update the database
	populatedb = flag.Bool("populatedb", false, "boolean variable to update database")
)

func main() {
	err := godotenv.Load(".env")

	if err != nil {
		log.Fatalf("Error loading .env file")
	}

	flag.Parse()

	if os.Getenv("TOKEN_HOUR_LIFESPAN") == "" || os.Getenv("API_SECRET") == "" || os.Getenv("DEFAULT_ISSUER") == "" {
		log.Fatal("Mandatory environment variables not configured")
	}

	if os.Getenv("JWKS_URI") != "" {
		cache, err := jwk.NewCache(context.Background(), httprc.NewClient())
		if err != nil {
			log.Fatalf("Failed to create a jwk.Cache from the oidc provider's URL: %s", err)
		}

		if err := cache.Register(context.Background(), os.Getenv("JWKS_URI")); err != nil {
			log.Fatalf("Failed to create a jwk.Cache from the oidc provider's URL: %s", err)
		}

		auth.Jwks = cache
	}
	// database infoget from the .env
	dbhost := os.Getenv("DB_HOST")
	port := os.Getenv("DB_PORT")
	user := os.Getenv("DB_USER")
	dbname := os.Getenv("DB_NAME")
	password := os.Getenv("DB_PASSWORD")

	db.Connect(&dbhost, &port, &user, &dbname, &password)

	if err := validations.RegisterValidations(); err != nil {
		log.Fatalf("Failed to set up validations: %s", err)
	}

	if *populatedb {
		utils.Populatedb(*datafile)
	}

	r := api.Router()

	if err := r.Run(); err != nil {
		log.Fatalf("Error while running the server: %v", err)
	}
}
