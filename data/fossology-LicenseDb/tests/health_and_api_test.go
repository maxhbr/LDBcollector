// SPDX-FileCopyrightText: 2026 Krishi Agrawal <krishi.agrawal26@gmail.com>
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

func TestGetHealth(t *testing.T) {
	t.Run("getHealthSuccess", func(t *testing.T) {
		w := makeRequest("GET", "/health", nil, false)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.LicenseError
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		assert.Contains(t, res.Message, "Database is running")
	})
}

func TestGetAPICollection(t *testing.T) {
	t.Run("getAPICollectionSuccess", func(t *testing.T) {
		w := makeRequest("GET", "/apiCollection", nil, false)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.APICollectionResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		assert.NotNil(t, res.Data)
		assert.NotNil(t, res.Data.Authenticated)
		assert.NotNil(t, res.Data.UnAuthenticated)
	})
}
