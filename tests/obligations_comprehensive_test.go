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
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

func TestGetAllObligation(t *testing.T) {
	loginAs(t, "admin")

	t.Run("getAllActiveObligations", func(t *testing.T) {
		w := makeRequest("GET", "/obligations?active=true", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ObligationResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		assert.GreaterOrEqual(t, len(res.Data), 0)
	})

	t.Run("getAllObligationsWithPagination", func(t *testing.T) {
		w := makeRequest("GET", "/obligations?page=1&limit=5", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ObligationResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		assert.NotNil(t, res.Meta)
	})

	t.Run("getAllObligationsWithOrderBy", func(t *testing.T) {
		w := makeRequest("GET", "/obligations?order_by=desc", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ObligationResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
	})
}

func TestGetObligation(t *testing.T) {
	dto := models.ObligationCreateDTO{
		Topic:          "test-get-obligation",
		Type:           "RIGHT",
		Text:           "Test obligation text",
		Classification: "GREEN",
		Comment:        ptr("Test comment"),
		Active:         ptr(true),
		TextUpdatable:  ptr(false),
		Category:       ptr("GENERAL"),
	}
	createW := makeRequest("POST", "/obligations", dto, true)
	assert.Equal(t, http.StatusCreated, createW.Code)

	var createRes models.ObligationResponse
	if err := json.Unmarshal(createW.Body.Bytes(), &createRes); err != nil {
		t.Fatalf("Failed to parse create response: %v", err)
	}
	if len(createRes.Data) == 0 {
		t.Fatal("No obligation returned in create response")
	}
	obligationId := createRes.Data[0].Id

	t.Run("getExistingObligation", func(t *testing.T) {
		w := makeRequest("GET", "/obligations/"+obligationId.String(), nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ObligationResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		if len(res.Data) > 0 {
			assert.Equal(t, dto.Topic, res.Data[0].Topic)
		}
	})

	t.Run("getNonExistingObligation", func(t *testing.T) {
		w := makeRequest("GET", "/obligations/"+uuid.New().String(), nil, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	t.Run("getObligationWithInvalidId", func(t *testing.T) {
		w := makeRequest("GET", "/obligations/invalid-id", nil, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

func TestGetAllObligationPreviews(t *testing.T) {
	t.Run("getActivePreviews", func(t *testing.T) {
		w := makeRequest("GET", "/obligations/preview?active=true", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ObligationPreviewResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		assert.GreaterOrEqual(t, len(res.Data), 0)
	})

	t.Run("getPreviewsWithInvalidActive", func(t *testing.T) {
		w := makeRequest("GET", "/obligations/preview?active=invalid", nil, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

func TestGetObligationAudits(t *testing.T) {
	dto := models.ObligationCreateDTO{
		Topic:          "test-audit-obligation",
		Type:           "RIGHT",
		Text:           "Test obligation text",
		Classification: "GREEN",
		Comment:        ptr("Test comment"),
		Active:         ptr(true),
		TextUpdatable:  ptr(false),
		Category:       ptr("GENERAL"),
	}
	createW := makeRequest("POST", "/obligations", dto, true)
	assert.Equal(t, http.StatusCreated, createW.Code)

	var createRes models.ObligationResponse
	if err := json.Unmarshal(createW.Body.Bytes(), &createRes); err != nil {
		t.Fatalf("Failed to parse create response: %v", err)
	}
	if len(createRes.Data) == 0 {
		t.Fatal("No obligation returned in create response")
	}
	obligationId := createRes.Data[0].Id

	t.Run("getObligationAudits", func(t *testing.T) {
		w := makeRequest("GET", "/obligations/"+obligationId.String()+"/audits", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.AuditResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		assert.GreaterOrEqual(t, len(res.Data), 0)
	})

	t.Run("getObligationAuditsWithPagination", func(t *testing.T) {
		w := makeRequest("GET", "/obligations/"+obligationId.String()+"/audits?page=1&limit=5", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.AuditResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
	})

	t.Run("getAuditsForNonExistingObligation", func(t *testing.T) {
		w := makeRequest("GET", "/obligations/"+uuid.New().String()+"/audits", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.AuditResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		assert.Equal(t, 0, len(res.Data))
	})
}

func TestExportObligations(t *testing.T) {
	t.Run("exportSuccess", func(t *testing.T) {
		w := makeRequest("GET", "/obligations/export", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var obligations []models.ObligationResponseDTO
		if err := json.Unmarshal(w.Body.Bytes(), &obligations); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.GreaterOrEqual(t, len(obligations), 0)
		assert.Contains(t, w.Header().Get("Content-Disposition"), "obligations-export")
	})
}

func TestImportObligations(t *testing.T) {
	t.Run("importSuccess", func(t *testing.T) {
		licenseW := makeRequest("GET", "/licenses", nil, true)
		assert.Equal(t, http.StatusOK, licenseW.Code)

		var licenseRes models.LicenseResponse
		if err := json.Unmarshal(licenseW.Body.Bytes(), &licenseRes); err != nil {
			t.Fatalf("Failed to parse license response: %v", err)
		}

		var licenseId *uuid.UUID
		if len(licenseRes.Data) > 0 {
			licenseId = &licenseRes.Data[0].Id
		}

		obligations := []models.ObligationFileDTO{
			{
				Topic:          ptr("IMPORT-OBLIGATION-1"),
				Type:           ptr("RIGHT"),
				Text:           ptr("Test obligation text for import"),
				Classification: ptr("GREEN"),
				Comment:        ptr("Test comment"),
				Active:         ptr(true),
				TextUpdatable:  ptr(false),
				Category:       ptr("GENERAL"),
			},
		}

		if licenseId != nil {
			obligations[0].LicenseIds = &[]uuid.UUID{*licenseId}
		}

		jsonData, err := json.Marshal(obligations)
		assert.NoError(t, err)

		body := &bytes.Buffer{}
		writer := multipart.NewWriter(body)
		part, err := writer.CreateFormFile("file", "obligations.json")
		assert.NoError(t, err)
		_, err = part.Write(jsonData)
		assert.NoError(t, err)
		writer.Close()

		fullPath := baseURL + "/obligations/import"
		req := httptest.NewRequest("POST", fullPath, body)
		req.Header.Set("Content-Type", writer.FormDataContentType())
		req.Header.Set("Authorization", "Bearer "+AuthToken)
		w := httptest.NewRecorder()
		api.Router().ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ImportObligationsResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
	})

	t.Run("importWithInvalidFile", func(t *testing.T) {
		body := &bytes.Buffer{}
		writer := multipart.NewWriter(body)
		part, err := writer.CreateFormFile("file", "obligations.txt")
		assert.NoError(t, err)
		_, err = part.Write([]byte("not json"))
		assert.NoError(t, err)
		writer.Close()

		fullPath := baseURL + "/obligations/import"
		req := httptest.NewRequest("POST", fullPath, body)
		req.Header.Set("Content-Type", writer.FormDataContentType())
		req.Header.Set("Authorization", "Bearer "+AuthToken)
		w := httptest.NewRecorder()
		api.Router().ServeHTTP(w, req)

		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("importWithoutFile", func(t *testing.T) {
		fullPath := baseURL + "/obligations/import"
		req := httptest.NewRequest("POST", fullPath, nil)
		req.Header.Set("Authorization", "Bearer "+AuthToken)
		w := httptest.NewRecorder()
		api.Router().ServeHTTP(w, req)

		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

func TestGetSimilarObligations(t *testing.T) {
	t.Run("findSimilarObligations", func(t *testing.T) {
		similarityReq := models.SimilarityRequest{
			Text: "You must include the copyright notice and this permission notice in all copies",
		}

		w := makeRequest("POST", "/obligations/similarity", similarityReq, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ApiResponse[[]models.SimilarObligation]
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

		w := makeRequest("POST", "/obligations/similarity", similarityReq, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("findSimilarWithInvalidJSON", func(t *testing.T) {
		fullPath := baseURL + "/obligations/similarity"
		req := httptest.NewRequest("POST", fullPath, bytes.NewBuffer([]byte("invalid json")))
		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Authorization", "Bearer "+AuthToken)
		w := httptest.NewRecorder()
		api.Router().ServeHTTP(w, req)

		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}
