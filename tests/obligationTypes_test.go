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

func TestCreateObligationType(t *testing.T) {
	loginAs(t, "admin")

	obType := models.ObligationType{
		Type:   "PERMISSION",
		Active: ptr(true),
	}

	t.Run("success", func(t *testing.T) {
		w := makeRequest("POST", "/obligations/types", obType, true)
		assert.Equal(t, http.StatusCreated, w.Code)

		var res models.ObligationTypeResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling response: %v", err)
			return
		}
		assert.Equal(t, obType.Type, res.Data[0].Type)
	})

	t.Run("missingFields", func(t *testing.T) {
		invalidObType := models.ObligationType{
			Type:   "",
			Active: ptr(true),
		}
		w := makeRequest("POST", "/obligations/types", invalidObType, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("unauthorized", func(t *testing.T) {
		w := makeRequest("POST", "/obligations/types", obType, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("duplicateObligationType", func(t *testing.T) {
		duplicate := models.ObligationType{
			Type:   "DUPLICATE",
			Active: ptr(true),
		}

		w1 := makeRequest("POST", "/obligations/types", duplicate, true)
		assert.Equal(t, http.StatusCreated, w1.Code)

		w2 := makeRequest("POST", "/obligations/types", duplicate, true)
		assert.Equal(t, http.StatusConflict, w2.Code)
	})
}

// TestGetAllObligationType tests the GET /obligations/types API
func TestGetAllObligationType(t *testing.T) {
	t.Run("getAllActive", func(t *testing.T) {
		w := makeRequest("GET", "/obligations/types?active=true", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ObligationTypeResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling response: %v", err)
			return
		}
		assert.GreaterOrEqual(t, len(res.Data), 0)
	})

	t.Run("invalidQueryParam", func(t *testing.T) {
		w := makeRequest("GET", "/obligations/types?active=invalid", nil, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

func TestDeleteObligationType(t *testing.T) {
	obType := models.ObligationType{
		Type:   "TODELETE",
		Active: ptr(true),
	}
	w := makeRequest("POST", "/obligations/types", obType, true)
	assert.Equal(t, http.StatusCreated, w.Code)

	t.Run("success", func(t *testing.T) {
		w := makeRequest("DELETE", "/obligations/types/"+obType.Type, nil, true)
		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("notFound", func(t *testing.T) {
		w := makeRequest("DELETE", "/obligations/types/NonExistentType", nil, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	t.Run("unauthorized", func(t *testing.T) {
		w := makeRequest("DELETE", "/obligations/types/"+obType.Type, nil, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}
