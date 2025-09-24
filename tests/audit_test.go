// SPDX-FileCopyrightText: 2025 Chayan Das <01chayandas@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only
package test

import (
	"encoding/json"
	"net/http"
	"testing"

	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

func TestGetAuditsAndChangelog(t *testing.T) {
	// make sure we have atleast one changelog
	license := models.LicenseCreateDTO{
		Shortname: "MIT3",
		Fullname:  "MIT License 3",
		Text:      `MIT1 License copyright (c) <year> <copyright holders> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.`,
		Url:       ptr("https://opensource.org/licenses/MIT"),
		Notes:     ptr("This license is OSI approved."),
		Source:    ptr("spdx"),
		SpdxId:    "LicenseRef-MIT3",
		Risk:      ptr(int64(2)),
	}
	_ = makeRequest("POST", "/licenses", license, true)

	var audit models.Audit

	t.Run("getAllAudit", func(t *testing.T) {
		w := makeRequest("GET", "/audits", nil, true)

		assert.Equal(t, http.StatusOK, w.Code)

		var resp models.AuditResponse
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		assert.NoError(t, err)

		assert.Equal(t, http.StatusOK, resp.Status)
		assert.NotNil(t, resp.Data)

		audit = resp.Data[0]
	})

	t.Run("getSingleAudit", func(t *testing.T) {
		w := makeRequest("GET", "/audits/"+audit.Id.String(), nil, false)
		assert.Equal(t, http.StatusOK, w.Code)
		var resp models.AuditResponse
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusOK, resp.Status)
		assert.Equal(t, audit.Id, resp.Data[0].Id)
		assert.NotNil(t, resp.Data[0].Entity)
	})

	t.Run("getSingleAuditInvalidID", func(t *testing.T) {
		w := makeRequest("GET", "/audits/8484848", nil, false)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("getSingleAuditNotFound", func(t *testing.T) {
		w := makeRequest("GET", "/audits/"+uuid.New().String(), nil, false)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	var changelog models.ChangeLog
	t.Run("getChangelog", func(t *testing.T) {
		w := makeRequest("GET", "/audits/"+audit.Id.String()+"/changes", nil, true)

		assert.Equal(t, http.StatusOK, w.Code)

		var resp models.ChangeLogResponse
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusOK, resp.Status)
		assert.NotEmpty(t, resp.Data)

		changelog = resp.Data[0]
	})

	t.Run("getChangelogNotFound", func(t *testing.T) {
		w := makeRequest("GET", "/audits/"+uuid.New().String()+"/changes", nil, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	t.Run("getChange", func(t *testing.T) {
		w := makeRequest("GET", "/audits/"+audit.Id.String()+"/changes/"+changelog.Id.String(), nil, true)

		assert.Equal(t, http.StatusOK, w.Code)

		var resp models.ChangeLogResponse
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusOK, resp.Status)
	})

	t.Run("getChangeInvalidID", func(t *testing.T) {
		w := makeRequest("GET", "/audits/142564356/changes/0456565", nil, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("getChangeNotFound", func(t *testing.T) {
		w := makeRequest("GET", "/audits"+uuid.New().String()+"/changes/"+uuid.New().String(), nil, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})
}
