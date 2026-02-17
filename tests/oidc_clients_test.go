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

func TestGetUserOidcClients(t *testing.T) {
	loginAs(t, "admin")

	t.Run("getUserOidcClients", func(t *testing.T) {
		w := makeRequest("GET", "/oidcClients", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.OidcClientsResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		assert.NotNil(t, res.Data)
		assert.GreaterOrEqual(t, len(res.Data), 0)
	})

	t.Run("unauthorized", func(t *testing.T) {
		w := makeRequest("GET", "/oidcClients", nil, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestAddOidcClient(t *testing.T) {
	t.Run("addOidcClientSuccess", func(t *testing.T) {
		oidcClient := models.CreateDeleteOidcClientDTO{
			ClientId: "test-client-id-1",
		}

		w := makeRequest("POST", "/oidcClients", oidcClient, true)
		assert.Equal(t, http.StatusCreated, w.Code)

		var res models.OidcClientsResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		if len(res.Data) > 0 {
			assert.Equal(t, oidcClient.ClientId, res.Data[0].ClientId)
		}
	})

	t.Run("addDuplicateOidcClient", func(t *testing.T) {
		oidcClient := models.CreateDeleteOidcClientDTO{
			ClientId: "test-client-id-2",
		}

		w1 := makeRequest("POST", "/oidcClients", oidcClient, true)
		assert.Equal(t, http.StatusCreated, w1.Code)

		w2 := makeRequest("POST", "/oidcClients", oidcClient, true)
		assert.Equal(t, http.StatusConflict, w2.Code)
	})

	t.Run("addOidcClientWithInvalidJSON", func(t *testing.T) {
		w := makeRequest("POST", "/oidcClients", "invalid", true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("unauthorized", func(t *testing.T) {
		oidcClient := models.CreateDeleteOidcClientDTO{
			ClientId: "test-client-id-3",
		}
		w := makeRequest("POST", "/oidcClients", oidcClient, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestRevokeClient(t *testing.T) {
	oidcClient := models.CreateDeleteOidcClientDTO{
		ClientId: "test-revoke-client",
	}
	addW := makeRequest("POST", "/oidcClients", oidcClient, true)
	assert.Equal(t, http.StatusCreated, addW.Code)

	t.Run("revokeClientSuccess", func(t *testing.T) {
		w := makeRequest("DELETE", "/oidcClients", oidcClient, true)
		assert.Equal(t, http.StatusNoContent, w.Code)
	})

	t.Run("revokeNonExistingClient", func(t *testing.T) {
		nonExistingClient := models.CreateDeleteOidcClientDTO{
			ClientId: "non-existing-client",
		}
		w := makeRequest("DELETE", "/oidcClients", nonExistingClient, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	t.Run("revokeClientWithInvalidJSON", func(t *testing.T) {
		w := makeRequest("DELETE", "/oidcClients", "invalid", true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("unauthorized", func(t *testing.T) {
		w := makeRequest("DELETE", "/oidcClients", oidcClient, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}
