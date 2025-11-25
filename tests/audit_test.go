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

func TestGetAllAudit(t *testing.T) {
	t.Run("success", func(t *testing.T) {
		w := makeRequest("GET", "/audits", nil, true)

		assert.Equal(t, http.StatusOK, w.Code)

		var resp models.AuditResponse
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		assert.NoError(t, err)

		assert.Equal(t, http.StatusOK, resp.Status)
		assert.NotNil(t, resp.Data)
	})

}

func TestGetAudit(t *testing.T) {
	t.Run("success", func(t *testing.T) {
		w := makeRequest("GET", "/audits/1", nil, false)
		assert.Equal(t, http.StatusOK, w.Code)
		var resp models.AuditResponse
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusOK, resp.Status)
		assert.Equal(t, int64(1), resp.Data[0].Id)
		assert.NotNil(t, resp.Data[0].Entity)
		entityMap, ok := resp.Data[0].Entity.(map[string]interface{})
		if !ok {
			t.Fatalf("entity is not a JSON object: %T", resp.Data[0].Entity)
		}
		idValue, ok := entityMap["Id"].(float64)
		if !ok {
			t.Fatalf("entity does not contain numeric Id field")
		}
		assert.Equal(t, float64(resp.Data[0].TypeId), idValue)
	})

	t.Run("invalidID", func(t *testing.T) {
		w := makeRequest("GET", "/audits/0", nil, false)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("notFound", func(t *testing.T) {
		w := makeRequest("GET", "/audits/99999", nil, false)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})
}
func TestGetChangeLogs(t *testing.T) {
	t.Run("success", func(t *testing.T) {
		w := makeRequest("GET", "/audits/1/changes", nil, true)

		assert.Equal(t, http.StatusOK, w.Code)

		var resp models.ChangeLogResponse
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusOK, resp.Status)
		assert.NotEmpty(t, resp.Data)
	})

	t.Run("notFound", func(t *testing.T) {
		w := makeRequest("GET", "/audits/99999/changes", nil, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})
}
func TestGetChangeLogByID(t *testing.T) {
	t.Run("success", func(t *testing.T) {
		w := makeRequest("GET", "/audits/1/changes/1", nil, true)

		assert.Equal(t, http.StatusOK, w.Code)

		var resp models.ChangeLogResponse
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		assert.NoError(t, err)
		assert.Equal(t, http.StatusOK, resp.Status)
		assert.Equal(t, 1, int(resp.Data[0].Id))
	})

	t.Run("invalidID", func(t *testing.T) {
		w := makeRequest("GET", "/audits/1/changes/0", nil, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("notFound", func(t *testing.T) {
		w := makeRequest("GET", "/audits/1/changes/99999", nil, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})
}
