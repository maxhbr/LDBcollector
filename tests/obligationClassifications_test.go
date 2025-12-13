// SPDX-FileCopyrightText: 2025 Chayan Das <01chayandas@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package test

import (
	"encoding/json"
	"net/http"
	"testing"

	"github.com/fossology/LicenseDb/pkg/models"
	"github.com/stretchr/testify/assert"
)

func TestCreateObligationClassification(t *testing.T) {
	loginAs(t, "admin")

	validClassification := models.ObligationClassification{
		Classification: "TEST_CREATE",
		Color:          "#FF00FF",
		Active:         ptr(true),
	}

	t.Run("success", func(t *testing.T) {
		w := makeRequest("POST", "/obligations/classifications", validClassification, true)
		assert.Equal(t, http.StatusCreated, w.Code)

		var res models.ObligationClassificationResponse
		err := json.Unmarshal(w.Body.Bytes(), &res)
		assert.NoError(t, err)
		assert.Equal(t, validClassification.Classification, res.Data[0].Classification)
		assert.Equal(t, validClassification.Color, res.Data[0].Color)
	})

	t.Run("duplicateConflict", func(t *testing.T) {
		w := makeRequest("POST", "/obligations/classifications", validClassification, true)
		assert.Equal(t, http.StatusConflict, w.Code)
	})

	t.Run("validationFailed", func(t *testing.T) {
		invalidClassification := models.ObligationClassification{
			Classification: "lowercase",
			Color:          "notacolor",
			Active:         ptr(true),
		}
		w := makeRequest("POST", "/obligations/classifications", invalidClassification, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("unauthorized", func(t *testing.T) {
		w := makeRequest("POST", "/obligations/classifications", validClassification, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}
func TestGetAllObligationClassification(t *testing.T) {

	t.Run("successWithActiveTrue", func(t *testing.T) {
		w := makeRequest("GET", "/obligations/classifications?active=true", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ObligationClassificationResponse
		err := json.Unmarshal(w.Body.Bytes(), &res)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusOK, res.Status)
		assert.NotEmpty(t, res.Data)
	})

	t.Run("successWithDefaultActive", func(t *testing.T) {
		w := makeRequest("GET", "/obligations/classifications", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ObligationClassificationResponse
		err := json.Unmarshal(w.Body.Bytes(), &res)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusOK, res.Status)
	})

	t.Run("invalidActiveParam", func(t *testing.T) {
		w := makeRequest("GET", "/obligations/classifications?active=notabool", nil, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}
func TestDeleteObligationClassificationAPI(t *testing.T) {
	classification := "TEST_DELETE_CREATE"
	loginAs(t, "admin")

	validClassification := models.ObligationClassification{
		Classification: classification,
		Color:          "#FF00FE",
		Active:         ptr(true),
	}

	t.Run("success", func(t *testing.T) {
		w := makeRequest("POST", "/obligations/classifications", validClassification, true)
		assert.Equal(t, http.StatusCreated, w.Code)

		var res models.ObligationClassificationResponse
		err := json.Unmarshal(w.Body.Bytes(), &res)
		assert.NoError(t, err)
		assert.Equal(t, validClassification.Classification, res.Data[0].Classification)
		assert.Equal(t, validClassification.Color, res.Data[0].Color)
	})

	t.Run("successDelete", func(t *testing.T) {
		w := makeRequest("DELETE", "/obligations/classifications/"+classification, nil, true)
		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("deleteAlreadyInactive", func(t *testing.T) {
		w := makeRequest("DELETE", "/obligations/classifications/"+classification, nil, true)
		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("deleteNotFound", func(t *testing.T) {
		w := makeRequest("DELETE", "/obligations/classifications/DOES_NOT_EXIST", nil, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	t.Run("unauthorized", func(t *testing.T) {
		w := makeRequest("DELETE", "/obligations/classifications/"+classification, nil, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}
