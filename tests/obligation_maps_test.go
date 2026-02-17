// SPDX-FileCopyrightText: 2026 Krishi Agrawal <krishi.agrawal26@gmail.com>
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

func TestGetObligationMapByObligationId(t *testing.T) {
	loginAs(t, "admin")

	licenseW := makeRequest("GET", "/licenses", nil, true)
	assert.Equal(t, http.StatusOK, licenseW.Code)

	var licenseRes models.LicenseResponse
	if err := json.Unmarshal(licenseW.Body.Bytes(), &licenseRes); err != nil {
		t.Fatalf("Failed to parse license response: %v", err)
	}

	if len(licenseRes.Data) == 0 {
		t.Skip("No licenses available for testing")
	}

	dto := models.ObligationCreateDTO{
		Topic:          "test-obligation-map",
		Type:           "RIGHT",
		Text:           "Test obligation text",
		Classification: "GREEN",
		Comment:        ptr("Test comment"),
		Active:         ptr(true),
		TextUpdatable:  ptr(false),
		Category:       ptr("GENERAL"),
		LicenseIds:     []uuid.UUID{licenseRes.Data[0].Id},
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

	t.Run("getObligationMapByObligationId", func(t *testing.T) {
		w := makeRequest("GET", "/obligation_maps/obligation/"+obligationId.String(), nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ObligationMapResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		if len(res.Data) > 0 {
			assert.Equal(t, dto.Topic, res.Data[0].Topic)
			assert.GreaterOrEqual(t, len(res.Data[0].Licenses), 0)
		}
	})

	t.Run("getObligationMapForNonExistingObligation", func(t *testing.T) {
		w := makeRequest("GET", "/obligation_maps/obligation/"+uuid.New().String(), nil, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	t.Run("getObligationMapWithInvalidId", func(t *testing.T) {
		w := makeRequest("GET", "/obligation_maps/obligation/invalid-id", nil, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

func TestGetObligationMapByLicenseId(t *testing.T) {
	licenseW := makeRequest("GET", "/licenses", nil, true)
	assert.Equal(t, http.StatusOK, licenseW.Code)

	var licenseRes models.LicenseResponse
	if err := json.Unmarshal(licenseW.Body.Bytes(), &licenseRes); err != nil {
		t.Fatalf("Failed to parse license response: %v", err)
	}

	if len(licenseRes.Data) == 0 {
		t.Skip("No licenses available for testing")
	}
	licenseId := licenseRes.Data[0].Id

	t.Run("getObligationMapByLicenseId", func(t *testing.T) {
		w := makeRequest("GET", "/obligation_maps/license/"+licenseId.String(), nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ObligationMapResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		assert.GreaterOrEqual(t, len(res.Data), 0)
	})

	t.Run("getObligationMapForNonExistingLicense", func(t *testing.T) {
		w := makeRequest("GET", "/obligation_maps/license/"+uuid.New().String(), nil, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	t.Run("getObligationMapWithInvalidId", func(t *testing.T) {
		w := makeRequest("GET", "/obligation_maps/license/invalid-id", nil, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

func TestPatchObligationMap(t *testing.T) {
	dto := models.ObligationCreateDTO{
		Topic:          "test-patch-obligation-map",
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

	licenseW := makeRequest("GET", "/licenses", nil, true)
	assert.Equal(t, http.StatusOK, licenseW.Code)

	var licenseRes models.LicenseResponse
	if err := json.Unmarshal(licenseW.Body.Bytes(), &licenseRes); err != nil {
		t.Fatalf("Failed to parse license response: %v", err)
	}

	if len(licenseRes.Data) == 0 {
		t.Skip("No licenses available for testing")
	}
	licenseId := licenseRes.Data[0].Id

	t.Run("patchObligationMapAddLicense", func(t *testing.T) {
		mapInput := models.LicenseMapInput{
			MapInput: []models.LicenseMapElement{
				{
					Id:  licenseId,
					Add: true,
				},
			},
		}

		w := makeRequest("PATCH", "/obligation_maps/obligation/"+obligationId.String()+"/license", mapInput, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ObligationMapResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
	})

	t.Run("patchObligationMapRemoveLicense", func(t *testing.T) {
		mapInputAdd := models.LicenseMapInput{
			MapInput: []models.LicenseMapElement{
				{
					Id:  licenseId,
					Add: true,
				},
			},
		}
		_ = makeRequest("PATCH", "/obligation_maps/obligation/"+obligationId.String()+"/license", mapInputAdd, true)

		mapInputRemove := models.LicenseMapInput{
			MapInput: []models.LicenseMapElement{
				{
					Id:  licenseId,
					Add: false,
				},
			},
		}

		w := makeRequest("PATCH", "/obligation_maps/obligation/"+obligationId.String()+"/license", mapInputRemove, true)
		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("patchObligationMapForNonExistingObligation", func(t *testing.T) {
		mapInput := models.LicenseMapInput{
			MapInput: []models.LicenseMapElement{
				{
					Id:  licenseId,
					Add: true,
				},
			},
		}

		w := makeRequest("PATCH", "/obligation_maps/obligation/"+uuid.New().String()+"/license", mapInput, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	t.Run("patchObligationMapWithInvalidJSON", func(t *testing.T) {
		w := makeRequest("PATCH", "/obligation_maps/obligation/"+obligationId.String()+"/license", "invalid", true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}

func TestUpdateLicenseInObligationMap(t *testing.T) {
	dto := models.ObligationCreateDTO{
		Topic:          "test-update-obligation-map",
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

	licenseW := makeRequest("GET", "/licenses", nil, true)
	assert.Equal(t, http.StatusOK, licenseW.Code)

	var licenseRes models.LicenseResponse
	if err := json.Unmarshal(licenseW.Body.Bytes(), &licenseRes); err != nil {
		t.Fatalf("Failed to parse license response: %v", err)
	}

	if len(licenseRes.Data) == 0 {
		t.Skip("No licenses available for testing")
	}
	licenseId := licenseRes.Data[0].Id

	t.Run("updateLicenseInObligationMap", func(t *testing.T) {
		licenseListInput := models.LicenseListInput{
			LicenseIds: []uuid.UUID{licenseId},
		}

		w := makeRequest("PUT", "/obligation_maps/obligation/"+obligationId.String()+"/license", licenseListInput, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ObligationMapResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
	})

	t.Run("updateLicenseInObligationMapWithEmptyList", func(t *testing.T) {
		licenseListInput := models.LicenseListInput{
			LicenseIds: []uuid.UUID{},
		}

		w := makeRequest("PUT", "/obligation_maps/obligation/"+obligationId.String()+"/license", licenseListInput, true)
		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("updateLicenseInObligationMapForNonExistingObligation", func(t *testing.T) {
		licenseListInput := models.LicenseListInput{
			LicenseIds: []uuid.UUID{licenseId},
		}

		w := makeRequest("PUT", "/obligation_maps/obligation/"+uuid.New().String()+"/license", licenseListInput, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	t.Run("updateLicenseInObligationMapWithInvalidJSON", func(t *testing.T) {
		w := makeRequest("PUT", "/obligation_maps/obligation/"+obligationId.String()+"/license", "invalid", true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}
