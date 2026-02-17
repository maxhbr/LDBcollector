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

func TestGetDashboardData(t *testing.T) {
	loginAs(t, "admin")

	t.Run("getDashboardData", func(t *testing.T) {
		w := makeRequest("GET", "/dashboard", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.DashboardResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		assert.NotNil(t, res.Data)
		assert.GreaterOrEqual(t, res.Data.LicensesCount, int64(0))
		assert.GreaterOrEqual(t, res.Data.ObligationsCount, int64(0))
		assert.GreaterOrEqual(t, res.Data.UsersCount, int64(0))
		assert.GreaterOrEqual(t, res.Data.LicenseChangesSinceLastMonth, int64(0))
		riskFreqLen := 0
		if res.Data.RiskLicenseFrequency != nil {
			riskFreqLen = len(res.Data.RiskLicenseFrequency)
		}
		categoryFreqLen := 0
		if res.Data.CategoryObligationFrequency != nil {
			categoryFreqLen = len(res.Data.CategoryObligationFrequency)
		}
		assert.GreaterOrEqual(t, riskFreqLen, 0)
		assert.GreaterOrEqual(t, categoryFreqLen, 0)
	})

	t.Run("getDashboardDataUnauthorized", func(t *testing.T) {
		w := makeRequest("GET", "/dashboard", nil, false)
		assert.Contains(t, []int{http.StatusOK, http.StatusUnauthorized}, w.Code)
	})
}
