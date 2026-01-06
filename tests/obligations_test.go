// SPDX-FileCopyrightText: 2025 Chayan Das <01chayandas@gmail.com>
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

func TestCreateObligation(t *testing.T) {
	t.Run("SuccessWithoutLicenseIds", func(t *testing.T) {
		dto := models.ObligationCreateDTO{
			Topic:          "test-topic-1",
			Type:           "RIGHT",
			Text:           "some text",
			Classification: "GREEN",
			Comment:        ptr("unit test no license ids"),
			Active:         ptr(true),
			TextUpdatable:  ptr(false),
			Category:       ptr("GENERAL"),
		}

		assertObligationCreated(t, dto)
	})

	t.Run("SuccessWithLicenseIds", func(t *testing.T) {
		w := makeRequest("GET", "/licenses", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.LicenseResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}

		dto := models.ObligationCreateDTO{
			Topic:          "test-topic-2",
			Type:           "RIGHT",
			Text:           "another text",
			Classification: "YELLOW",
			Comment:        ptr("unit test with shortnames"),
			Active:         ptr(true),
			TextUpdatable:  ptr(true),
			LicenseIds:     []uuid.UUID{res.Data[0].Id},
			Category:       ptr("DISTRIBUTION"),
		}

		assertObligationCreated(t, dto)
	})
	t.Run("licenseDoesNotExist", func(t *testing.T) {
		dto := models.ObligationCreateDTO{
			Topic:          "test-topic-3",
			Type:           "RIGHT",
			Text:           "text with non-existing shortname",
			Classification: "RED",
			Comment:        ptr("unit test with non-existing shortname"),
			Active:         ptr(true),
			TextUpdatable:  ptr(false),
			LicenseIds:     []uuid.UUID{uuid.New()},
			Category:       ptr("GENERAL"),
		}

		w := makeRequest("POST", "/obligations", dto, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)

		var res models.LicenseError
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}

		expectedError := "Obligation created successfully but license association failed"
		assert.Equal(t, expectedError, res.Message)
	})

	t.Run("MissingRequiredField", func(t *testing.T) {
		dto := models.ObligationCreateDTO{
			// Topic missing
			Type:           "RIGHT",
			Text:           "text",
			Classification: "GREEN",
			Comment:        ptr("missing topic"),
			Active:         ptr(true),
			TextUpdatable:  ptr(false),
			Category:       ptr("GENERAL"),
		}

		w := makeRequest("POST", "/obligations", dto, true)
		if w.Code != http.StatusBadRequest {
			t.Errorf("Expected 400 for missing required field, got %d", w.Code)
		}
	})
}

func TestUpdateObligation(t *testing.T) {

	var id uuid.UUID
	t.Run("CreateObligation", func(t *testing.T) {
		dto := models.ObligationCreateDTO{
			Topic:          "test-update-topic",
			Type:           "RIGHT",
			Text:           "test text for update",
			Classification: "GREEN",
			Comment:        ptr("unit test comment"),
			Active:         ptr(true),
			TextUpdatable:  ptr(false),
			Category:       ptr("GENERAL"),
		}
		id = assertObligationCreated(t, dto)
	})

	t.Run("UpdateObligation", func(t *testing.T) {
		updateDTO := models.ObligationUpdateDTO{
			Type:           ptr("RIGHT"),
			Text:           ptr("test text for update"),
			Classification: ptr("GREEN"),
			Comment:        ptr("updated comment"),
			Active:         ptr(false),
			TextUpdatable:  ptr(false),
			Category:       ptr("GENERAL"),
		}

		assertObligationUpdated(t, id, updateDTO)
	})
	t.Run("UpdateTextUpdatableFalse", func(t *testing.T) {
		updateDTO := models.ObligationUpdateDTO{
			TextUpdatable: ptr(false),
		}
		assertObligationUpdated(t, id, updateDTO)
		textupdate := models.ObligationUpdateDTO{
			Text: ptr("Trying to update text when TextUpdatable is false"),
		}
		w := makeRequest("PATCH", "/obligations/"+id.String(), textupdate, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("UpdateTextUpdatableTrue", func(t *testing.T) {
		updateDTO := models.ObligationUpdateDTO{
			TextUpdatable: ptr(true),
		}
		assertObligationUpdated(t, id, updateDTO)

		textupdate := models.ObligationUpdateDTO{
			Text: ptr("Successfully updated text when TextUpdatable is true"),
		}
		w := makeRequest("PATCH", "/obligations/"+id.String(), textupdate, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ObligationResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}

		assert.Equal(t, *textupdate.Text, res.Data[0].Text)
	})
	t.Run("UpdateNonExistingObligation", func(t *testing.T) {
		updateDTO := models.ObligationUpdateDTO{
			Type:           ptr("RIGHT"),
			Text:           ptr("text for non-existing obligation"),
			Classification: ptr("GREEN"),
			Comment:        ptr("non-existing obligation comment"),
			Active:         ptr(true),
			TextUpdatable:  ptr(false),
			Category:       ptr("GENERAL"),
		}

		w := makeRequest("PATCH", "/obligations/"+uuid.New().String(), updateDTO, true)
		assert.Equal(t, http.StatusNotFound, w.Code)

		var res models.LicenseError
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}

		assert.Equal(t, "record not found", res.Error)
		assert.Equal(t, http.StatusNotFound, res.Status)
	})

}

func TestDeleteObligation(t *testing.T) {
	var _id uuid.UUID
	dto := models.ObligationCreateDTO{
		Topic:          "delete-test-topic",
		Type:           "RISK",
		Text:           "To be deleted",
		Classification: "GREEN",
		Comment:        ptr("delete comment"),
		Active:         ptr(true),
		TextUpdatable:  ptr(true),
		Category:       ptr("GENERAL"),
	}
	_id = assertObligationCreated(t, dto)
	id := _id.String()

	t.Run("DeleteExistingObligation", func(t *testing.T) {
		w := makeRequest("DELETE", "/obligations/"+id, nil, true)
		if w.Code != http.StatusNoContent {
			t.Fatalf("Expected status 204 No Content, got %d", w.Code)
		}
	})

	t.Run("DeleteNonExistentObligation", func(t *testing.T) {
		w := makeRequest("DELETE", "/obligations/"+id, nil, true)
		if w.Code != http.StatusNoContent {
			t.Fatalf("Expected status 204 Not Found, got %d", w.Code)
		}
	})
}

func assertObligationCreated(t *testing.T, dto models.ObligationCreateDTO) uuid.UUID {
	w := makeRequest("POST", "/obligations", dto, true)
	if w.Code != http.StatusCreated {
		t.Fatalf("Expected 201 Created, got %d", w.Code)
	}

	var resp struct {
		Status int                            `json:"status"`
		Data   []models.ObligationResponseDTO `json:"data"`
		Meta   models.PaginationMeta          `json:"paginationmeta"`
	}

	if err := json.Unmarshal(w.Body.Bytes(), &resp); err != nil {
		t.Fatalf("Failed to parse response: %v", err)
	}

	if len(resp.Data) == 0 {
		t.Fatal("No obligation returned in response")
	}

	ob := resp.Data[0]

	// Assertions
	assertField := func(fieldName string, expected, actual any) {
		if expected != actual {
			t.Errorf("Expected %s = %v, got %v", fieldName, expected, actual)
		}
	}

	assertField("Topic", dto.Topic, ob.Topic)
	assertField("Type", dto.Type, ob.Type)
	assertField("Text", dto.Text, ob.Text)
	if ob.Comment != nil {
		assertField("Comment", *dto.Comment, *ob.Comment)
	}
	if ob.Category != nil {
		assertField("Category", *dto.Category, *ob.Category)
	} else {
		assertField("Category", *dto.Category, "GENERAL")
	}

	assertField("Classification", dto.Classification, ob.Classification)
	assertField("Active", *dto.Active, ob.Active)
	assertField("TextUpdatable", *dto.TextUpdatable, ob.TextUpdatable)
	assertField("Licenses count", len(dto.LicenseIds), len(ob.LicenseIds))

	return ob.Id
}
func assertObligationUpdated(t *testing.T, id uuid.UUID, dto models.ObligationUpdateDTO) {
	w := makeRequest("PATCH", "/obligations/"+id.String(), dto, true)
	if w.Code != http.StatusOK {
		t.Fatalf("Expected 200 OK, got %d", w.Code)
	}

	var resp struct {
		Status int                            `json:"status"`
		Data   []models.ObligationResponseDTO `json:"data"`
		Meta   models.PaginationMeta          `json:"paginationmeta"`
	}

	if err := json.Unmarshal(w.Body.Bytes(), &resp); err != nil {
		t.Fatalf("Failed to parse update response: %v", err)
	}

	if len(resp.Data) == 0 {
		t.Fatal("No obligation returned in update response")
	}

	ob := resp.Data[0]

	// Field-wise assertions (only check non-nil fields from dto)
	assertField := func(fieldName string, expected, actual any) {
		if expected != actual {
			t.Errorf("Expected %s = %v, got %v", fieldName, expected, actual)
		}
	}

	if dto.Type != nil {
		assertField("Type", *dto.Type, ob.Type)
	}
	if dto.Text != nil {
		assertField("Text", *dto.Text, ob.Text)
	}
	if dto.Comment != nil {
		assertField("Comment", *dto.Comment, *ob.Comment)
	}
	if dto.Category != nil {
		assertField("Category", *dto.Category, *ob.Category)
	}
	if dto.Classification != nil {
		assertField("Classification", *dto.Classification, ob.Classification)
	}
	if dto.Active != nil {
		assertField("Active", *dto.Active, ob.Active)
	}
	if dto.TextUpdatable != nil {
		assertField("TextUpdatable", *dto.TextUpdatable, ob.TextUpdatable)
	}
}
