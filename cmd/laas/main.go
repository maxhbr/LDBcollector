// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
// SPDX-FileContributor: 2025 Chayan Das <01chayandas@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package main

import (
	"context"
	"flag"
	"os"
	"strconv"

	"github.com/joho/godotenv"
	"github.com/lestrrat-go/httprc/v3"
	"github.com/lestrrat-go/jwx/v3/jwk"
	"go.uber.org/zap"

	_ "github.com/dave/jennifer/jen"
	_ "github.com/fossology/LicenseDb/cmd/laas/docs"
	"github.com/fossology/LicenseDb/pkg/api"
	"github.com/fossology/LicenseDb/pkg/auth"
	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/email"
	logger "github.com/fossology/LicenseDb/pkg/log"
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/fossology/LicenseDb/pkg/validations"
)

var (
	datafile   = flag.String("datafile", "licenseRef.json", "datafile path")
	populatedb = flag.Bool("populatedb", false, "boolean variable to update database")
)

func main() {
	if err := godotenv.Load(".env"); err != nil {
		logger.LogFatal("Error loading .env file", zap.Error(err))
	}
	flag.Parse()

	// Check for mandatory environment variables
	if os.Getenv("TOKEN_HOUR_LIFESPAN") == "" ||
		os.Getenv("API_SECRET") == "" ||
		os.Getenv("DEFAULT_ISSUER") == "" ||
		os.Getenv("REFRESH_TOKEN_HOUR_LIFESPAN") == "" ||
		os.Getenv("REFRESH_TOKEN_SECRET") == "" {
		logger.LogFatal("Mandatory environment variables not configured")
	}

	if os.Getenv("JWKS_URI") != "" {
		cache, err := jwk.NewCache(context.Background(), httprc.NewClient())
		if err != nil {
			logger.LogFatal("Failed to create jwk.Cache", zap.Error(err))
		}
		if err := cache.Register(context.Background(), os.Getenv("JWKS_URI")); err != nil {
			logger.LogFatal("Failed to register JWKS URI", zap.Error(err))
		}
		auth.Jwks = cache
	}

	dbhost := os.Getenv("DB_HOST")
	port := os.Getenv("DB_PORT")
	user := os.Getenv("DB_USER")
	dbname := os.Getenv("DB_NAME")
	password := os.Getenv("DB_PASSWORD")

	// initialize email service
	enableSMTP, _ := strconv.ParseBool(os.Getenv("ENABLE_SMTP"))
	if enableSMTP {
		if err := email.Init(); err != nil {
			logger.LogFatal("Failed to initialize email service", zap.Error(err))
		}
	}
	// connect to database
	db.Connect(&dbhost, &port, &user, &dbname, &password)

	if err := validations.RegisterValidations(); err != nil {
		logger.LogFatal("Failed to set up validations", zap.Error(err))
	}

	if *populatedb {
		utils.Populatedb(*datafile)
	}

	r := api.Router()
	if err := r.Run(); err != nil {
		logger.LogFatal("Error while running the server", zap.Error(err))
	}
}
