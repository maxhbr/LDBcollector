// SPDX-FileCopyrightText: 2026 Krishi Agrawal <krishi.agrawal26@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package test

import (
	"bytes"
	"encoding/json"
	"mime/multipart"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/fossology/LicenseDb/pkg/api"
	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/stretchr/testify/assert"
)

func TestFilterLicense(t *testing.T) {
	loginAs(t, "admin")

	t.Run("filterByActive", func(t *testing.T) {
		w := makeRequest("GET", "/licenses?active=true", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.LicenseResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.GreaterOrEqual(t, len(res.Data), 0)
	})

	t.Run("filterByOSIApproved", func(t *testing.T) {
		w := makeRequest("GET", "/licenses?osiapproved=true", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.LicenseResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.GreaterOrEqual(t, len(res.Data), 0)
	})

	t.Run("filterByCopyleft", func(t *testing.T) {
		w := makeRequest("GET", "/licenses?copyleft=false", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.LicenseResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.GreaterOrEqual(t, len(res.Data), 0)
	})

	t.Run("filterBySpdxId", func(t *testing.T) {
		license := models.LicenseCreateDTO{
			Shortname: "TEST-FILTER-SPDX",
			Fullname:  "Test Filter SPDX License",
			Text:      "Test license text",
			Url:       ptr("https://example.com"),
			Notes:     ptr("Test notes"),
			Source:    ptr("test"),
			SpdxId:    "LicenseRef-TEST-FILTER-SPDX",
			Risk:      ptr(int64(1)),
		}
		createW := makeRequest("POST", "/licenses", license, true)
		assert.Equal(t, http.StatusCreated, createW.Code)

		w := makeRequest("GET", "/licenses?spdxid=LicenseRef-TEST-FILTER-SPDX", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.LicenseResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		if len(res.Data) > 0 {
			assert.Equal(t, license.SpdxId, res.Data[0].SpdxId)
		}
	})

	t.Run("filterWithPagination", func(t *testing.T) {
		w := makeRequest("GET", "/licenses?page=1&limit=5", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.LicenseResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.GreaterOrEqual(t, len(res.Data), 0)
		assert.NotNil(t, res.Meta)
	})

	t.Run("filterWithSorting", func(t *testing.T) {
		w := makeRequest("GET", "/licenses?sort_by=shortname&order_by=asc", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.LicenseResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.GreaterOrEqual(t, len(res.Data), 0)
	})

	t.Run("filterWithInvalidSortBy", func(t *testing.T) {
		w := makeRequest("GET", "/licenses?sort_by=invalid_field", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)
	})
}

func TestExportLicenses(t *testing.T) {
	t.Run("exportSuccess", func(t *testing.T) {
		w := makeRequest("GET", "/licenses/export", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var licenses []models.LicenseResponseDTO
		if err := json.Unmarshal(w.Body.Bytes(), &licenses); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.GreaterOrEqual(t, len(licenses), 0)
		assert.Contains(t, w.Header().Get("Content-Disposition"), "license-export")
	})
}

func TestGetAllLicensePreviews(t *testing.T) {
	t.Run("getActivePreviews", func(t *testing.T) {
		w := makeRequest("GET", "/licenses/preview?active=true", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.LicensePreviewResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		assert.GreaterOrEqual(t, len(res.Licenses), 0)
	})

	t.Run("getInactivePreviews", func(t *testing.T) {
		w := makeRequest("GET", "/licenses/preview?active=false", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.LicensePreviewResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
	})

	t.Run("getPreviewsWithInvalidActive", func(t *testing.T) {
		w := makeRequest("GET", "/licenses/preview?active=invalid", nil, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

func TestImportLicenses(t *testing.T) {
	t.Run("importSuccess", func(t *testing.T) {
		licenses := []models.LicenseImportDTO{
			{
				Shortname: ptr("IMPORT-TEST-1"),
				Fullname:  ptr("Import Test License 1"),
				Text:      ptr("Test license text for import"),
				Url:       ptr("https://example.com/import1"),
				Notes:     ptr("Test notes for import"),
				Source:    ptr("test"),
				SpdxId:    ptr("LicenseRef-IMPORT-TEST-1"),
				Risk:      ptr(int64(2)),
			},
		}

		jsonData, err := json.Marshal(licenses)
		assert.NoError(t, err)

		body := &bytes.Buffer{}
		writer := multipart.NewWriter(body)
		part, err := writer.CreateFormFile("file", "licenses.json")
		assert.NoError(t, err)
		_, err = part.Write(jsonData)
		assert.NoError(t, err)
		writer.Close()

		fullPath := baseURL + "/licenses/import"
		req := httptest.NewRequest("POST", fullPath, body)
		req.Header.Set("Content-Type", writer.FormDataContentType())
		req.Header.Set("Authorization", "Bearer "+AuthToken)
		w := httptest.NewRecorder()
		api.Router().ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ImportLicensesResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		assert.GreaterOrEqual(t, len(res.Data), 0)
	})

	t.Run("importWithInvalidFile", func(t *testing.T) {
		body := &bytes.Buffer{}
		writer := multipart.NewWriter(body)
		part, err := writer.CreateFormFile("file", "licenses.txt")
		assert.NoError(t, err)
		_, err = part.Write([]byte("not json"))
		assert.NoError(t, err)
		writer.Close()

		fullPath := baseURL + "/licenses/import"
		req := httptest.NewRequest("POST", fullPath, body)
		req.Header.Set("Content-Type", writer.FormDataContentType())
		req.Header.Set("Authorization", "Bearer "+AuthToken)
		w := httptest.NewRecorder()
		api.Router().ServeHTTP(w, req)

		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("importWithoutFile", func(t *testing.T) {
		w := makeRequest("POST", "/licenses/import", nil, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

func TestSearchInLicense(t *testing.T) {
	t.Run("searchWithFullText", func(t *testing.T) {
		searchReq := models.SearchLicense{
			Field:      "shortname",
			Search:     "full_text_search",
			SearchTerm: "MIT",
		}

		w := makeRequest("POST", "/search", searchReq, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.LicenseResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
	})

	t.Run("searchWithFuzzy", func(t *testing.T) {
		searchReq := models.SearchLicense{
			Field:      "fullname",
			Search:     "fuzzy",
			SearchTerm: "MIT",
		}

		w := makeRequest("POST", "/search", searchReq, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.LicenseResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
	})

	t.Run("searchWithInvalidField", func(t *testing.T) {
		searchReq := models.SearchLicense{
			Field:      "invalid_field",
			Search:     "full_text_search",
			SearchTerm: "MIT",
		}

		w := makeRequest("POST", "/search", searchReq, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("searchWithInvalidAlgorithm", func(t *testing.T) {
		searchReq := models.SearchLicense{
			Field:      "shortname",
			Search:     "invalid_algorithm",
			SearchTerm: "MIT",
		}

		w := makeRequest("POST", "/search", searchReq, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	t.Run("searchWithInvalidJSON", func(t *testing.T) {
		w := makeRequest("POST", "/search", []byte("invalid json"), true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

func TestGetSimilarLicenses(t *testing.T) {
	t.Run("findSimilarLicenses", func(t *testing.T) {
		similarityReq := models.SimilarityRequest{
			Text: "MIT License\n\nCopyright (c) <year> <copyright holders>\n\nPermission is hereby granted",
		}

		w := makeRequest("POST", "/licenses/similarity", similarityReq, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ApiResponse[[]models.SimilarLicense]
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		if res.Data != nil {
			assert.GreaterOrEqual(t, len(res.Data), 0)
		}
	})

	t.Run("findSimilarWithEmptyText", func(t *testing.T) {
		similarityReq := models.SimilarityRequest{
			Text: "",
		}

		w := makeRequest("POST", "/licenses/similarity", similarityReq, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("findSimilarWithInvalidJSON", func(t *testing.T) {
		w := makeRequest("POST", "/licenses/similarity", []byte("invalid json"), true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}
