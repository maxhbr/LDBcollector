// SPDX-FileCopyrightText: 2026 Siemens AG
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
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

func TestCreateObligationCategory(t *testing.T) {
	loginAs(t, "admin")

	obCategory := models.ObligationCategory{
		Category: "GENERAL-II",
		Active:   ptr(true),
	}

	t.Run("success", func(t *testing.T) {
		w := makeRequest("POST", "/obligations/categories", obCategory, true)
		assert.Equal(t, http.StatusCreated, w.Code)

		var res models.ObligationCategoryResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling response: %v", err)
			return
		}
		assert.Equal(t, obCategory.Category, res.Data[0].Category)
	})

	t.Run("missingFields", func(t *testing.T) {
		invalidObCategory := models.ObligationCategory{
			Category: "",
			Active:   ptr(true),
		}
		w := makeRequest("POST", "/obligations/categories", invalidObCategory, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("unauthorized", func(t *testing.T) {
		w := makeRequest("POST", "/obligations/categories", obCategory, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("duplicateObligationCategory", func(t *testing.T) {
		duplicate := models.ObligationCategory{
			Category: "DUPLICATE",
			Active:   ptr(true),
		}

		w1 := makeRequest("POST", "/obligations/categories", duplicate, true)
		assert.Equal(t, http.StatusCreated, w1.Code)

		w2 := makeRequest("POST", "/obligations/categories", duplicate, true)
		assert.Equal(t, http.StatusConflict, w2.Code)
	})
}

// TestGetAllObligationCategory tests the GET /obligations/categories API
func TestGetAllObligationCategory(t *testing.T) {
	t.Run("getAllActive", func(t *testing.T) {
		w := makeRequest("GET", "/obligations/categories?active=true", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ObligationCategoryResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling response: %v", err)
			return
		}
		assert.GreaterOrEqual(t, len(res.Data), 0)
	})

	t.Run("invalidQueryParam", func(t *testing.T) {
		w := makeRequest("GET", "/obligations/categories?active=invalid", nil, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

func TestDeleteObligationCategory(t *testing.T) {
	obCategory := models.ObligationCategory{
		Category: "TODELETE",
		Active:   ptr(true),
	}
	w := makeRequest("POST", "/obligations/categories", obCategory, true)
	assert.Equal(t, http.StatusCreated, w.Code)

	t.Run("success", func(t *testing.T) {
		w := makeRequest("DELETE", "/obligations/categories/"+obCategory.Category, nil, true)
		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("notFound", func(t *testing.T) {
		w := makeRequest("DELETE", "/obligations/categories/NonExistentCategory", nil, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	t.Run("unauthorized", func(t *testing.T) {
		w := makeRequest("DELETE", "/obligations/categories/"+obCategory.Category, nil, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}
