// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-License-Identifier: GPL-2.0-only

package db

import (
	"fmt"

	logger "github.com/fossology/LicenseDb/pkg/log"
	"go.uber.org/zap"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

// DB is a global variable to store the GORM database connection.
var DB *gorm.DB

// Connect establishes a connection to the database using the provided parameters.
func Connect(dbhost, port, user, dbname, password *string) {

	dburi := fmt.Sprintf("host=%s port=%s user=%s dbname=%s password=%s", *dbhost, *port, *user, *dbname, *password)
	gormConfig := &gorm.Config{TranslateError: true}
	database, err := gorm.Open(postgres.Open(dburi), gormConfig)
	if err != nil {
		logger.LogFatal("Failed to connect to database", zap.Error(err))
	}

	DB = database
}
