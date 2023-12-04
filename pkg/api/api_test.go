// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-License-Identifier: GPL-2.0-only

package api

import (
	"bytes"
	"encoding/base64"
	"encoding/json"

	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/fossology/LicenseDb/pkg/db"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func TestMain(m *testing.M) {
	gin.SetMode(gin.TestMode)
	dbname := "fossology"
	user := "fossy"
	password := "fossy"
	port := "5432"
	dbhost := "localhost"
	db.Connect(&dbhost, &port, &user, &dbname, &password)

	exitcode := m.Run()
	os.Exit(exitcode)
}

func makeRequest(method, path string, body interface{}, isAuthanticated bool) *httptest.ResponseRecorder {
	reqBody, _ := json.Marshal(body)
	req := httptest.NewRequest(method, path, bytes.NewBuffer(reqBody))
	req.Header.Set("Content-Type", "application/json")
	if isAuthanticated {
		req.Header.Set("Authorization", "Basic "+base64.StdEncoding.EncodeToString([]byte("fossy:fossy")))
	}
	w := httptest.NewRecorder()
	Router().ServeHTTP(w, req)
	return w
}
func TestGetLicense(t *testing.T) {
	expectLicense := models.LicenseDB{
		Shortname:     "MIT",
		Fullname:      "MIT License",
		Text:          "MIT License\n\nCopyright (c) <year> <copyright holders>\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n",
		Url:           "https://opensource.org/licenses/MIT",
		TextUpdatable: "f",
		DetectorType:  "1",
		Active:        "t",
		Flag:          "1",
		Marydone:      "t",
		SpdxId:        "MIT",
	}
	w := makeRequest("GET", "/api/licenses/MIT", nil, false)
	assert.Equal(t, http.StatusOK, w.Code)

	var res models.LicenseResponse
	json.Unmarshal(w.Body.Bytes(), &res)

	assert.Equal(t, expectLicense, res.Data[0])

}

func TestCreateLicense(t *testing.T) {
	License := models.LicenseDB{
		Shortname:     "ABCD",
		Fullname:      "ABCD License",
		Text:          "just a license",
		Url:           "https://abcdlicense/ABCD",
		SpdxId:        "1",
		TextUpdatable: "f",
		DetectorType:  "1",
		Active:        "t",
	}
	w := makeRequest("POST", "/api/licenses", License, true)
	assert.Equal(t, http.StatusCreated, w.Code)
	type response struct {
		Data models.LicenseDB `json:"data"`
	}

	var res models.LicenseResponse
	json.Unmarshal(w.Body.Bytes(), &res)

	assert.Equal(t, License, res.Data[0])

}

func TestUpdateLicense(t *testing.T) {
	License := models.LicenseDB{
		Marydone: "t",
	}
	expectedLicense := models.LicenseDB{
		Shortname:     "MIT",
		Fullname:      "MIT License",
		Text:          "MIT License\n\nCopyright (c) <year> <copyright holders>\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n",
		Url:           "https://opensource.org/licenses/MIT",
		TextUpdatable: "f",
		DetectorType:  "1",
		Active:        "t",
		Flag:          "1",
		Marydone:      "t",
		SpdxId:        "MIT",
	}
	w := makeRequest("PATCH", "/api/licenses/MIT", License, true)
	assert.Equal(t, http.StatusOK, w.Code)

	var res models.LicenseResponse
	json.Unmarshal(w.Body.Bytes(), &res)

	assert.Equal(t, expectedLicense, res.Data[0])

}

func TestSearchInLicense(t *testing.T) {
	expectLicense := models.LicenseDB{
		Shortname:     "PostgreSQL",
		Fullname:      "PostgreSQL License",
		Text:          "PostgreSQL Database Management System\n(formerly known as Postgres, then as Postgres95)\n\nPortions Copyright (c) 1996-2010, The PostgreSQL Global Development Group\n\nPortions Copyright (c) 1994, The Regents of the University of California\n\nPermission to use, copy, modify, and distribute this software and its documentation for any purpose, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and this paragraph and the following two paragraphs appear in all copies.\n\nIN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF THE UNIVERSITY OF CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.\n\nTHE UNIVERSITY OF CALIFORNIA SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED HEREUNDER IS ON AN \"AS IS\" BASIS, AND THE UNIVERSITY OF CALIFORNIA HAS NO OBLIGATIONS TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.\n",
		Url:           "http://www.postgresql.org/about/licence",
		TextUpdatable: "f",
		DetectorType:  "1",
		Active:        "t",
		Flag:          "1",
		Marydone:      "f",
		SpdxId:        "PostgreSQL",
	}
	search := models.SearchLicense{
		Field:      "fullname",
		SearchTerm: "Postgresql",
		SearchType: "",
	}
	w := makeRequest("POST", "/api/search", search, false)
	assert.Equal(t, http.StatusOK, w.Code)

	var res models.LicenseResponse
	json.Unmarshal(w.Body.Bytes(), &res)

	assert.Equal(t, expectLicense, res.Data[0])

}

func TestSearchInLicense2(t *testing.T) {
	expectLicense := []models.LicenseDB{
		{
			Shortname:     "GPL-2.0-with-autoconf-exception",
			Fullname:      "GNU General Public License v2.0 w/Autoconf exception",
			Text:          "insert GPL v2 license text here\n\nAutoconf Exception\n\nAs a special exception, the Free Software Foundation gives unlimited permission to copy, distribute and modify the configure scripts that are the output of Autoconf. You need not follow the terms of the GNU General Public License when using or distributing such scripts, even though portions of the text of Autoconf appear in them. The GNU General Public License (GPL) does govern all other use of the material that constitutes the Autoconf program.\n\nCertain portions of the Autoconf source text are designed to be copied (in certain cases, depending on the input) into the output of Autoconf. We call these the \"data\" portions. The rest of the Autoconf source text consists of comments plus executable code that decides which of the data portions to output in any given case. We call these comments and executable code the \"non-data\" portions. Autoconf never copies any of the non-data portions into its output.\n\nThis special exception to the GPL applies to versions of Autoconf released by the Free Software Foundation. When you make and distribute a modified version of Autoconf, you may extend this special exception to the GPL to apply to your modified version as well, *unless* your modified version has the potential to copy into its output some of the text that was the non-data portion of the version that you started with. (In other words, unless your change moves or copies text from the non-data portions to the data portions.) If your modification has such potential, you must delete any notice of this special exception to the GPL from your modified version.\n\n",
			Url:           "http://ac-archive.sourceforge.net/doc/copyright.html",
			Notes:         "DEPRECATED: Use license expression including main license, \"WITH\" operator, and identifier: Autoconf-exception-2.0",
			TextUpdatable: "f",
			DetectorType:  "1",
			Active:        "t",
			Flag:          "1",
			Marydone:      "f",
			SpdxId:        "LicenseRef-fossology-GPL-2.0-with-autoconf-exception",
		},
		{
			Shortname:     "Autoconf-exception-2.0",
			Fullname:      "Autoconf exception 2.0",
			Text:          "As a special exception, the Free Software Foundation gives unlimited permission to copy, distribute and modify the configure scripts that are the output of Autoconf. You need not follow the terms of the GNU General Public License when using or distributing such scripts, even though portions of the text of Autoconf appear in them. The GNU General Public License (GPL) does govern all other use of the material that constitutes the Autoconf program.\n\nCertain portions of the Autoconf source text are designed to be copied (in certain cases, depending on the input) into the output of Autoconf. We call these the \"data\" portions. The rest of the Autoconf source text consists of comments plus executable code that decides which of the data portions to output in any given case. We call these comments and executable code the \"non-data\" portions. Autoconf never copies any of the non-data portions into its output.\n\nThis special exception to the GPL applies to versions of Autoconf released by the Free Software Foundation. When you make and distribute a modified version of Autoconf, you may extend this special exception to the GPL to apply to your modified version as well, *unless* your modified version has the potential to copy into its output some of the text that was the non-data portion of the version that you started with. (In other words, unless your change moves or copies text from the non-data portions to the data portions.) If your modification has such potential, you must delete any notice of this special exception to the GPL from your modified version.\n",
			Url:           "http://ac-archive.sourceforge.net/doc/copyright.html",
			Notes:         "Typically used with GPL-2.0",
			TextUpdatable: "f",
			DetectorType:  "1",
			Active:        "t",
			Flag:          "1",
			Marydone:      "f",
			SpdxId:        "Autoconf-exception-2.0",
		},
	}
	search := models.SearchLicense{
		Field:      "url",
		SearchTerm: "http://ac-archive.sourceforge.net/doc/copyright.html",
		SearchType: "",
	}
	w := makeRequest("POST", "/api/search", search, false)
	assert.Equal(t, http.StatusOK, w.Code)

	var res models.LicenseResponse
	json.Unmarshal(w.Body.Bytes(), &res)

	assert.Equal(t, expectLicense, res.Data)
}

func TestGetUser(t *testing.T) {
	expectUser := models.User{
		Userid:       "1",
		Username:     "fossy",
		Userpassword: "fossy",
		Userlevel:    "admin",
	}
	w := makeRequest("GET", "/api/user/1", nil, false)
	assert.Equal(t, http.StatusOK, w.Code)

	var res models.UserResponse
	json.Unmarshal(w.Body.Bytes(), &res)

	assert.Equal(t, expectUser, res.Data[0])

}

func TestCreateUser(t *testing.T) {
	user := models.User{
		Userid:       "2",
		Username:     "general_user",
		Userpassword: "abc123",
		Userlevel:    "participant",
	}
	w := makeRequest("POST", "/api/user", user, true)
	assert.Equal(t, http.StatusOK, w.Code)

	var res models.UserResponse
	json.Unmarshal(w.Body.Bytes(), &res)

	assert.Equal(t, user, res.Data[0])
}
