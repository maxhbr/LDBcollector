// SPDX-FileCopyrightText: 2025 Chayan Das <01chayandas@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package test

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/fossology/LicenseDb/pkg/api"
	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/utils"
	"github.com/fossology/LicenseDb/pkg/validations"
	"github.com/gin-gonic/gin"
	"github.com/golang-migrate/migrate/v4"
	_ "github.com/golang-migrate/migrate/v4/database/postgres"
	_ "github.com/golang-migrate/migrate/v4/source/file"
	"github.com/joho/godotenv"
	_ "github.com/lib/pq"
	"golang.org/x/crypto/bcrypt"
)

var baseURL string   // global variable
var AuthToken string // Global reusable token
const testDataFile = "../licenseRef.json"

func TestMain(m *testing.M) {
	gin.SetMode(gin.TestMode)

	const envFile = "../.env.test"

	err := godotenv.Load(envFile)
	if err != nil {
		log.Fatalf("Error loading .env file: %v", err)
	}
	dbname := os.Getenv("DB_NAME")
	user := os.Getenv("DB_USER")
	password := os.Getenv("DB_PASSWORD")
	port := os.Getenv("DB_PORT")
	dbhost := os.Getenv("DB_HOST")

	createTestDB(user, password, port, dbhost, dbname)    // create the test db
	runMigrations(user, password, port, dbhost, dbname)   // migrate the test db
	db.Connect(&dbhost, &port, &user, &dbname, &password) // connnect to the test db
	if err := seedFirstUser(); err != nil {               // create fisrt user to the test db
		log.Fatalf(" Failed to seed user: %v", err)
	}
	log.Println("First user created")
	if err := validations.RegisterValidations(); err != nil {
		log.Fatalf("Failed to set up validations: %s", err)
	}
	utils.Populatedb(testDataFile) // populate the nessesary tables with data from the file
	serverPort := os.Getenv("PORT")
	if serverPort == "" {
		port = "8080"
	}
	baseURL = fmt.Sprintf("http://localhost:%s/api/v1", serverPort)
	exitcode := m.Run()

	if db.DB != nil {
		sqlDB, _ := db.DB.DB()
		sqlDB.Close()
	}

	dropTestDB(user, password, port, dbhost, dbname) // drop the test db
	os.Exit(exitcode)
}

// makeRequest is a utility function for creating and sending HTTP requests during testing.
func makeRequest(method, path string, body interface{}, isAuthenticated bool) *httptest.ResponseRecorder {
	reqBody, _ := json.Marshal(body)
	fullPath := baseURL + path
	req := httptest.NewRequest(method, fullPath, bytes.NewBuffer(reqBody))
	req.Header.Set("Content-Type", "application/json")
	if isAuthenticated {
		req.Header.Set("Authorization", "Bearer "+AuthToken)
	}
	w := httptest.NewRecorder()
	api.Router().ServeHTTP(w, req)
	return w
}

func ptr[T any](v T) *T {
	return &v
}

// utility functions

func createTestDB(user, password, port, host, dbname string) {
	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=postgres sslmode=disable", host, port, user, password)
	db, err := sql.Open("postgres", dsn)
	if err != nil {
		log.Fatalf(" Failed to connect to postgres: %v", err)
	}
	defer db.Close()

	_, err = db.Exec("CREATE DATABASE " + dbname)
	if err != nil && !isAlreadyExistsError(err) {
		log.Fatalf(" Failed to create test DB: %v", err)
	}

	log.Println(" Test DB created")
}

func isAlreadyExistsError(err error) bool {
	return err != nil && (err.Error() == fmt.Sprintf("pq: database \"%s\" already exists", "licensedb_test"))
}

func runMigrations(user, password, port, host, dbname string) {
	dsn := fmt.Sprintf("postgres://%s:%s@%s:%s/%s?sslmode=disable", user, password, host, port, dbname)

	m, err := migrate.New(
		"file://../pkg/db/migrations",
		dsn,
	)
	if err != nil {
		log.Fatalf(" Failed to create migration instance: %v", err)
	}

	if err := m.Up(); err != nil && err != migrate.ErrNoChange {
		log.Fatalf(" Migration failed: %v", err)
	}

	log.Println("Migrations applied")
}

func seedFirstUser() error {
	password := "fossy"
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return err
	}

	superadmin := models.User{
		UserName:     ptr("fossy_superadmin"),
		DisplayName:  ptr("fossy_superadmin"),
		UserEmail:    ptr("test@gmail.com"),
		UserPassword: ptr(string(hashedPassword)),
		UserLevel:    ptr("SUPER_ADMIN"),
	}

	admin := models.User{
		UserName:     ptr("fossy_admin"),
		DisplayName:  ptr("fossy_admin"),
		UserEmail:    ptr("test2@gmail.com"),
		UserPassword: ptr(string(hashedPassword)),
		UserLevel:    ptr("ADMIN"),
	}

	if err := db.DB.Where("user_name = ?", *superadmin.UserName).
		FirstOrCreate(&superadmin).Error; err != nil {
		return err
	}

	// Create admin if not exists
	if err := db.DB.Where("user_name = ?", *admin.UserName).
		FirstOrCreate(&admin).Error; err != nil {
		return err
	}

	return nil
}
func dropTestDB(user, password, port, host, dbname string) {
	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=postgres sslmode=disable", host, port, user, password)
	db, err := sql.Open("postgres", dsn)
	if err != nil {
		log.Printf(" Error opening connection to drop DB: %v", err)
		return
	}
	defer db.Close()

	_, _ = db.Exec(fmt.Sprintf(`
		SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '%s' AND pid <> pg_backend_pid()`, dbname))

	_, err = db.Exec("DROP DATABASE IF EXISTS " + dbname)
	if err != nil {
		log.Printf(" Error dropping test DB: %v", err)
	} else {
		log.Println(" Dropped test DB:", dbname)
	}
}
