// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-License-Identifier: GPL-2.0-only
// SPDX-FileCopyrightText: 2025 Chayan Das <01chayandas@gmail.com>

package api

import (
	"bytes"
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/golang-migrate/migrate/v4"
	_ "github.com/golang-migrate/migrate/v4/database/postgres"
	_ "github.com/golang-migrate/migrate/v4/source/file"
	_ "github.com/lib/pq"
	"golang.org/x/crypto/bcrypt"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/fossology/LicenseDb/pkg/validations"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"github.com/stretchr/testify/assert"
)

// TestMain is the main testing function for the application. It sets up the testing environment,
// including configuring the Gin web framework for testing, connecting to a database,
// running the tests, and exiting with the appropriate exit code.

var baseURL string   // global variable
var AuthToken string // Global reusable token

func TestMain(m *testing.M) {
	gin.SetMode(gin.TestMode)

	const envFile = "../../.env.test"

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
	serverPort := os.Getenv("PORT")
	if serverPort == "" {
		port = "8080"
	}
	baseURL = fmt.Sprintf("http://localhost:%s/api/v1", serverPort)
	exitcode := m.Run()
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
	Router().ServeHTTP(w, req)
	return w
}

func ptr[T any](v T) *T {
	return &v
}

func TestLoginUser(t *testing.T) {

	t.Run("success", func(t *testing.T) {
		logindata := models.UserLogin{
			Username:     "fossy",
			Userpassword: "fossy",
		}

		w := makeRequest("POST", "/login", logindata, false)

		if w.Code != http.StatusOK {
			log.Fatalf(" Login failed with status: %d", w.Code)
		}

		var resp map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		if err != nil {
			log.Fatalf(" Failed to parse login response: %v", err)
		}

		token, ok := resp["token"].(string)
		if !ok || token == "" {
			log.Fatalf(" Token not found in login response. Got: %v", resp)
		}

		AuthToken = token
	})
	t.Run("wrong password", func(t *testing.T) {
		logindata := models.UserLogin{
			Username:     "fossy",
			Userpassword: "fossy-wrong",
		}

		w := makeRequest("POST", "/login", logindata, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)

	})

}

func TestCreateUser(t *testing.T) {
	t.Run("Success", func(t *testing.T) {
		password := "abc123"
		username := "fossy1"
		displayname := "fossy1"
		userlevel := "ADMIN"
		useremail := "fossy1@gmail.com"
		user := models.UserCreate{
			UserName:     &username,
			UserPassword: &password,
			UserLevel:    &userlevel,
			DisplayName:  &displayname,
			UserEmail:    &useremail,
		}
		w := makeRequest("POST", "/users", user, true)
		assert.Equal(t, http.StatusCreated, w.Code)

		var res models.UserResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, *user.UserName, *res.Data[0].UserName)
		assert.Equal(t, *user.UserLevel, *res.Data[0].UserLevel)
	})

	t.Run("MissingFields", func(t *testing.T) {
		user := models.UserCreate{}
		w := makeRequest("POST", "/users", user, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
	t.Run("DuplicateUser", func(t *testing.T) {
		password := "abc123"
		username := "fossy2"
		displayname := "fossy2"
		userlevel := "ADMIN"
		useremail := "fossy2@gmail.com"
		user := models.UserCreate{
			UserName:     &username,
			UserPassword: &password,
			UserLevel:    &userlevel,
			DisplayName:  &displayname,
			UserEmail:    &useremail,
		}

		// First request should succeed
		w1 := makeRequest("POST", "/users", user, true)
		assert.Equal(t, http.StatusCreated, w1.Code)

		// Second request with same user should fail
		w2 := makeRequest("POST", "/users", user, true)
		assert.Equal(t, http.StatusConflict, w2.Code)
	})

	t.Run("Unauthorized", func(t *testing.T) {
		password := "abc123"
		username := "fossy2"
		displayname := "fossy2"
		userlevel := "ADMIN"
		useremail := "fossy2@gmail.com"
		user := models.UserCreate{
			UserName:     &username,
			UserPassword: &password,
			UserLevel:    &userlevel,
			DisplayName:  &displayname,
			UserEmail:    &useremail,
		}
		w := makeRequest("POST", "/users", user, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestCreateLicense(t *testing.T) {
	license := models.LicenseCreateDTO{
		Shortname: "MIT",
		Fullname:  "MIT License",
		Text:      `MIT License copyright (c) <year> <copyright holders> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.`,
		Url:       "https://opensource.org/licenses/MIT",
		Notes:     "This license is OSI approved.",
		Source:    "spdx",
		SpdxId:    "MIT",
		Risk:      int64(2),
	}

	t.Run("success", func(t *testing.T) {
		w := makeRequest("POST", "/licenses", license, true)
		assert.Equal(t, http.StatusCreated, w.Code)
		var res models.LicenseResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling response: %v", err)
			return
		}
		if len(res.Data) == 0 {
			t.Fatal("Response data is empty, cannot validate fields")
		}
		assert.Equal(t, license.Shortname, res.Data[0].Shortname)
		assert.Equal(t, license.Fullname, res.Data[0].Fullname)
		assert.Equal(t, license.Text, res.Data[0].Text)
		assert.Equal(t, license.SpdxId, res.Data[0].SpdxId)
	})
	t.Run("missingFields", func(t *testing.T) {
		invalidLicense := models.LicenseCreateDTO{
			Shortname: "",
			Fullname:  "",
			Text:      "",
			Url:       "",
			SpdxId:    "",
			Notes:     "This license is OSI approved.",
			Risk:      int64(2),
		}
		w := makeRequest("POST", "/licenses", invalidLicense, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
	t.Run("unauthorized", func(t *testing.T) {
		license := models.LicenseCreateDTO{
			Shortname: "UnauthorizedLicense",
			Fullname:  "Unauthorized License",
			Text:      "This license should not be created without authentication.",
			Url:       "https://licenses.org/unauthorized",
			SpdxId:    "UNAUTHORIZED",
			Notes:     "This license is OSI approved.",
			Risk:      int64(2),
		}
		w := makeRequest("POST", "/licenses", license, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
	t.Run("duplicateLicense", func(t *testing.T) {
		license := models.LicenseCreateDTO{
			Shortname: "Test1",
			Fullname:  "Blank ExternalRef License",
			Text:      "Test license with blank ExternalRef",
			Url:       "https://licenses.org/blankref",
			SpdxId:    "MIT",
			Source:    "spdx",
			Notes:     "This license is OSI approved.",
			Risk:      int64(2),
		}
		w1 := makeRequest("POST", "/licenses", license, true)
		assert.Equal(t, http.StatusCreated, w1.Code)

		w2 := makeRequest("POST", "/licenses", license, true)
		assert.Equal(t, http.StatusConflict, w2.Code)
	})

}

func TestGetLicense(t *testing.T) {
	license := models.LicenseResponseDTO{
		Shortname:     "MIT",
		Fullname:      "MIT License",
		Text:          "MIT License\n\nCopyright (c) <year> <copyright holders>\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n",
		Url:           "https://opensource.org/licenses/MIT",
		TextUpdatable: false,
		Active:        true,
		SpdxId:        "MIT",
	}
	t.Run("existingLicense", func(t *testing.T) {
		w := makeRequest("GET", "/licenses/MIT", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.LicenseResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}

		assert.Equal(t, license.Shortname, res.Data[0].Shortname)
	})
	t.Run("nonExistingLicense", func(t *testing.T) {
		w := makeRequest("GET", "/licenses/NonExistentLicense", nil, true)
		assert.Equal(t, http.StatusNotFound, w.Code)

		var res models.LicenseResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}

		assert.Empty(t, res.Data)

	})

}

func TestUpdateLicense(t *testing.T) {

	expectedLicense := models.LicenseResponseDTO{
		Fullname:      "MIT License updated",
		Text:          "MIT License\n\nCopyright (c) <year> <copyright holders>\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n",
		Url:           "https://opensource.org/licenses/MIT",
		TextUpdatable: true,
		Active:        true,
		SpdxId:        "MIT",
	}
	t.Run("updatetextwithoutpermission", func(t *testing.T) {
		license := models.LicenseUpdateDTO{
			TextUpdatable: ptr(false),
		}
		// Attempt to update text without permission
		licenseToUpdate := models.LicenseUpdateDTO{
			Fullname:      ptr("MIT License updated"),
			Text:          ptr("updated text for MIT License"),
			Url:           ptr("https://opensource.org/licenses/MIT"),
			TextUpdatable: ptr(false),
			Active:        ptr(true),
			SpdxId:        ptr("MIT"),
		}
		w1 := makeRequest("PATCH", "/licenses/MIT", license, true)
		assert.Equal(t, http.StatusOK, w1.Code)

		w2 := makeRequest("PATCH", "/licenses/MIT", licenseToUpdate, true)
		assert.Equal(t, http.StatusBadRequest, w2.Code)

	})
	t.Run("UpdateExistingLicense", func(t *testing.T) {
		license := models.LicenseUpdateDTO{
			TextUpdatable: ptr(true),
		}
		w1 := makeRequest("PATCH", "/licenses/MIT", license, true)
		assert.Equal(t, http.StatusOK, w1.Code)

		w := makeRequest("PATCH", "/licenses/MIT", expectedLicense, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.LicenseResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}

		assert.Equal(t, expectedLicense.Fullname, res.Data[0].Fullname)
		assert.Equal(t, expectedLicense.TextUpdatable, res.Data[0].TextUpdatable)
	})

	t.Run("UpdateNonExistingLicense", func(t *testing.T) {
		nonExistingLicense := models.LicenseUpdateDTO{
			Fullname:      ptr("Non Existent License"),
			Text:          ptr("This license does not exist."),
			Url:           ptr("https://licenses.org/nonexistent"),
			TextUpdatable: ptr(false),
			Active:        ptr(true),
			SpdxId:        ptr("NONEXISTENT"),
		}
		w := makeRequest("PATCH", "/licenses/NonExistentLicense", nonExistingLicense, true)
		assert.Equal(t, http.StatusNotFound, w.Code)

		var res models.LicenseError
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}

		assert.Equal(t, "record not found", res.Error)
		assert.Equal(t, http.StatusNotFound, res.Status)
	})

}

// func TestSearchInLicense(t *testing.T) {
// 	expectLicense := models.LicenseDB{
// 		Shortname:     func(s string) *string { return &s }("PostgreSQL"),
// 		Fullname:      func(s string) *string { return &s }("PostgreSQL License"),
// 		Text:          func(s string) *string { return &s }("PostgreSQL Database Management System\n(formerly known as Postgres, then as Postgres95)\n\nPortions Copyright (c) 1996-2010, The PostgreSQL Global Development Group\n\nPortions Copyright (c) 1994, The Regents of the University of California\n\nPermission to use, copy, modify, and distribute this software and its documentation for any purpose, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and this paragraph and the following two paragraphs appear in all copies.\n\nIN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF THE UNIVERSITY OF CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.\n\nTHE UNIVERSITY OF CALIFORNIA SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS ON AN \"AS IS\" BASIS, AND THE UNIVERSITY OF CALIFORNIA HAS NO OBLIGATIONS TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.\n"),
// 		Url:           func(s string) *string { return &s }("http://www.postgresql.org/about/licence"),
// 		TextUpdatable: func(b bool) *bool { return &b }(false),
// 		DetectorType:  func(i int64) *int64 { return &i }(1),
// 		Active:        func(b bool) *bool { return &b }(true),
// 		Flag:          func(i int64) *int64 { return &i }(1),
// 		Marydone:      func(b bool) *bool { return &b }(false),
// 		SpdxId:        func(s string) *string { return &s }("PostgreSQL"),
// 	}
// 	search := models.SearchLicense{
// 		Field:      "fullname",
// 		SearchTerm: "Postgresql",
// 		Search:     "",
// 	}
// 	w := makeRequest("POST", "/api/search", search, false)
// 	assert.Equal(t, http.StatusOK, w.Code)

// 	var res models.LicenseResponse
// 	if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
// 		t.Errorf("Error unmarshalling JSON: %v", err)
// 		return
// 	}

// 	assert.Equal(t, expectLicense, res.Data[0])

// }

// func TestSearchInLicense2(t *testing.T) {
// 	expectLicense := []models.LicenseDB{
// 		{
// 			Shortname:     func(s string) *string { return &s }("GPL-2.0-with-autoconf-exception"),
// 			Fullname:      func(s string) *string { return &s }("GNU General Public License v2.0 w/Autoconf exception"),
// 			Text:          func(s string) *string { return &s }("insert GPL v2 license text here\n\nAutoconf Exception\n\nAs a special exception, the Free Software Foundation gives unlimited permission to copy, distribute and modify the configure scripts that are the output of Autoconf. You need not follow the terms of the GNU General Public License when using or distributing such scripts, even though portions of the text of Autoconf appear in them. The GNU General Public License (GPL) does govern all other use of the material that constitutes the Autoconf program.\n\nCertain portions of the Autoconf source text are designed to be copied (in certain cases, depending on the input) into the output of Autoconf. We call these the \"data\" portions. The rest of the Autoconf source text consists of comments plus executable code that decides which of the data portions to output in any given case. We call these comments and executable code the \"non-data\" portions. Autoconf never copies any of the non-data portions into its output.\n\nThis special exception to the GPL applies to versions of Autoconf released by the Free Software Foundation. When you make and distribute a modified version of Autoconf, you may extend this special exception to the GPL to apply to your modified version as well, *unless* your modified version has the potential to copy into its output some of the text that was the non-data portion of the version that you started with. (In other words, unless your change moves or copies text from the non-data portions to the data portions.) If your modification has such potential, you must delete any notice of this special exception to the GPL from your modified version.\n\n"),
// 			Url:           func(s string) *string { return &s }("http://ac-archive.sourceforge.net/doc/copyright.html"),
// 			Notes:         func(s string) *string { return &s }("DEPRECATED: Use license expression including main license, \"WITH\" operator, and identifier: Autoconf-exception-2.0"),
// 			TextUpdatable: func(b bool) *bool { return &b }(false),
// 			DetectorType:  func(i int64) *int64 { return &i }(1),
// 			Active:        func(b bool) *bool { return &b }(true),
// 			Flag:          func(i int64) *int64 { return &i }(1),
// 			Marydone:      func(b bool) *bool { return &b }(false),
// 			SpdxId:        func(s string) *string { return &s }("LicenseRef-fossology-GPL-2.0-with-autoconf-exception"),
// 		},
// 		{
// 			Shortname:     func(s string) *string { return &s }("Autoconf-exception-2.0"),
// 			Fullname:      func(s string) *string { return &s }("Autoconf exception 2.0"),
// 			Text:          func(s string) *string { return &s }("As a special exception, the Free Software Foundation gives unlimited permission to copy, distribute and modify the configure scripts that are the output of Autoconf. You need not follow the terms of the GNU General Public License when using or distributing such scripts, even though portions of the text of Autoconf appear in them. The GNU General Public License (GPL) does govern all other use of the material that constitutes the Autoconf program.\n\nCertain portions of the Autoconf source text are designed to be copied (in certain cases, depending on the input) into the output of Autoconf. We call these the \"data\" portions. The rest of the Autoconf source text consists of comments plus executable code that decides which of the data portions to output in any given case. We call these comments and executable code the \"non-data\" portions. Autoconf never copies any of the non-data portions into its output.\n\nThis special exception to the GPL applies to versions of Autoconf released by the Free Software Foundation. When you make and distribute a modified version of Autoconf, you may extend this special exception to the GPL to apply to your modified version as well, *unless* your modified version has the potential to copy into its output some of the text that was the non-data portion of the version that you started with. (In other words, unless your change moves or copies text from the non-data portions to the data portions.) If your modification has such potential, you must delete any notice of this special exception to the GPL from your modified version.\n"),
// 			Url:           func(s string) *string { return &s }("http://ac-archive.sourceforge.net/doc/copyright.html"),
// 			Notes:         func(s string) *string { return &s }("Typically used with GPL-2.0"),
// 			TextUpdatable: func(b bool) *bool { return &b }(false),
// 			DetectorType:  func(i int64) *int64 { return &i }(1),
// 			Active:        func(b bool) *bool { return &b }(true),
// 			Flag:          func(i int64) *int64 { return &i }(1),
// 			Marydone:      func(b bool) *bool { return &b }(false),
// 			SpdxId:        func(s string) *string { return &s }("Autoconf-exception-2.0"),
// 		},
// 	}
// 	search := models.SearchLicense{
// 		Field:      "url",
// 		SearchTerm: "http://ac-archive.sourceforge.net/doc/copyright.html",
// 		Search:     "",
// 	}
// 	w := makeRequest("POST", "/api/search", search, false)
// 	assert.Equal(t, http.StatusOK, w.Code)

// 	var res models.LicenseResponse
// 	if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
// 		t.Errorf("Error unmarshalling JSON: %v", err)
// 		return
// 	}

// 	assert.Equal(t, expectLicense, res.Data)
// }

// func TestGetUser(t *testing.T) {
// 	password := "fossy"
// 	username := "fossy"
// 	userlevel := "ADMIN"
// 	expectUser := models.User{
// 		Username:     &username,
// 		Userpassword: &password,
// 		Userlevel:    &userlevel,
// 	}
// 	w := makeRequest("GET", "/api/user/fossy", nil, false)
// 	assert.Equal(t, http.StatusOK, w.Code)

// 	var res models.UserResponse
// 	if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
// 		t.Errorf("Error unmarshalling JSON: %v", err)
// 		return
// 	}

// 	assert.Equal(t, expectUser, res.Data[0])

// }

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
		"file://../../pkg/db/migrations",
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

	user := models.User{
		UserName:     ptr("fossy"),
		DisplayName:  ptr("display_name"),
		UserEmail:    ptr("test@gmail.com"),
		UserPassword: ptr(string(hashedPassword)),
		UserLevel:    ptr("SUPER_ADMIN"),
	}

	return db.DB.Create(&user).Error
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
