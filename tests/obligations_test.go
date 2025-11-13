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

func TestCreateObligation(t *testing.T) {
	t.Run("SuccessWithoutShortnames", func(t *testing.T) {
		dto := models.ObligationDTO{
			Topic:          ptr("test-topic-1"),
			Type:           ptr("RIGHT"),
			Text:           ptr("some text"),
			Modifications:  ptr(false),
			Classification: ptr("GREEN"),
			Comment:        ptr("unit test no shortnames"),
			Active:         ptr(true),
			TextUpdatable:  ptr(false),
			Shortnames:     []string{},
			Category:       ptr("GENERAL"),
		}

		assertObligationCreated(t, dto)
	})

	t.Run("SuccessWithShortnames", func(t *testing.T) {
		dto := models.ObligationDTO{
			Topic:          ptr("test-topic-2"),
			Type:           ptr("RIGHT"),
			Text:           ptr("another text"),
			Modifications:  ptr(true),
			Classification: ptr("YELLOW"),
			Comment:        ptr("unit test with shortnames"),
			Active:         ptr(true),
			TextUpdatable:  ptr(true),
			Shortnames:     []string{"MIT"},
			Category:       ptr("DISTRIBUTION"),
		}

		assertObligationCreated(t, dto)
	})
	t.Run("shortnamenotexist", func(t *testing.T) {
		dto := models.ObligationDTO{
			Topic:          ptr("test-topic-3"),
			Type:           ptr("RIGHT"),
			Text:           ptr("text with non-existing shortname"),
			Modifications:  ptr(false),
			Classification: ptr("RED"),
			Comment:        ptr("unit test with non-existing shortname"),
			Active:         ptr(true),
			TextUpdatable:  ptr(false),
			Shortnames:     []string{"NonExistentShortname"},
			Category:       ptr("GENERAL"),
		}

		w := makeRequest("POST", "/obligations", dto, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)

		var res models.LicenseError
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}

		expectedError := "license with shortname NonExistentShortname not found"
		assert.Equal(t, expectedError, res.Error)
		assert.Equal(t, http.StatusBadRequest, res.Status)
	})

	t.Run("DuplicateTopic", func(t *testing.T) {
		dto := models.ObligationDTO{
			Topic:          ptr("duplicate-topic"),
			Type:           ptr("RIGHT"),
			Text:           ptr("text for duplicate topic"),
			Modifications:  ptr(false),
			Classification: ptr("GREEN"),
			Comment:        ptr("first insert"),
			Active:         ptr(true),
			TextUpdatable:  ptr(false),
			Shortnames:     []string{},
			Category:       ptr("GENERAL"),
		}
		assertObligationCreated(t, dto)

		// Try again with same topic
		w := makeRequest("POST", "/obligations", dto, true)
		if w.Code == http.StatusCreated {
			t.Errorf("Expected error for duplicate topic, got 201")
		}
	})

	t.Run("MissingRequiredField", func(t *testing.T) {
		dto := models.ObligationDTO{
			// Topic missing
			Type:           ptr("RIGHT"),
			Text:           ptr("text"),
			Modifications:  ptr(false),
			Classification: ptr("GREEN"),
			Comment:        ptr("missing topic"),
			Active:         ptr(true),
			TextUpdatable:  ptr(false),
			Shortnames:     []string{},
			Category:       ptr("GENERAL"),
		}

		w := makeRequest("POST", "/obligations", dto, true)
		if w.Code != http.StatusBadRequest {
			t.Errorf("Expected 400 for missing required field, got %d", w.Code)
		}
	})
}

func TestUpdateObligation(t *testing.T) {
	t.Run("CreateObligation", func(t *testing.T) {
		dto := models.ObligationDTO{
			Topic:          ptr("test-update-topic"),
			Type:           ptr("RIGHT"),
			Text:           ptr("test text for update"),
			Modifications:  ptr(false),
			Classification: ptr("GREEN"),
			Comment:        ptr("unit test comment"),
			Active:         ptr(true),
			TextUpdatable:  ptr(false),
			Shortnames:     []string{},
			Category:       ptr("GENERAL"),
		}
		assertObligationCreated(t, dto)
	})

	t.Run("UpdateObligation", func(t *testing.T) {
		updateDTO := models.ObligationUpdateDTO{
			Type:           ptr("RIGHT"),
			Text:           ptr("test text for update"),
			Classification: ptr("GREEN"),
			Modifications:  ptr(true),
			Comment:        ptr("updated comment"),
			Active:         ptr(false),
			TextUpdatable:  ptr(false),
			Category:       ptr("GENERAL"),
		}

		assertObligationUpdated(t, "test-update-topic", updateDTO)
	})
	t.Run("UpdateTextUpdatableFalse", func(t *testing.T) {
		updateDTO := models.ObligationUpdateDTO{
			TextUpdatable: ptr(false),
		}
		assertObligationUpdated(t, "test-update-topic", updateDTO)
		textupdate := models.ObligationUpdateDTO{
			Text: ptr("Trying to update text when TextUpdatable is false"),
		}
		w := makeRequest("PATCH", "/obligations/test-update-topic", textupdate, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})

	t.Run("UpdateTextUpdatableTrue", func(t *testing.T) {
		updateDTO := models.ObligationUpdateDTO{
			TextUpdatable: ptr(true),
		}
		assertObligationUpdated(t, "test-update-topic", updateDTO)

		textupdate := models.ObligationUpdateDTO{
			Text: ptr("Successfully updated text when TextUpdatable is true"),
		}
		w := makeRequest("PATCH", "/obligations/test-update-topic", textupdate, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.ObligationResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}

		assert.Equal(t, *textupdate.Text, *res.Data[0].Text)
	})
	t.Run("UpdateNonExistingObligation", func(t *testing.T) {
		updateDTO := models.ObligationUpdateDTO{
			Type:           ptr("RIGHT"),
			Text:           ptr("text for non-existing obligation"),
			Classification: ptr("GREEN"),
			Modifications:  ptr(false),
			Comment:        ptr("non-existing obligation comment"),
			Active:         ptr(true),
			TextUpdatable:  ptr(false),
			Category:       ptr("GENERAL"),
		}

		w := makeRequest("PATCH", "/obligations/non-existing-topic", updateDTO, true)
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
	topic := "delete-test-topic"
	dto := models.ObligationDTO{
		Topic:          ptr(topic),
		Type:           ptr("RISK"),
		Text:           ptr("To be deleted"),
		Classification: ptr("GREEN"),
		Modifications:  ptr(false),
		Comment:        ptr("delete comment"),
		Active:         ptr(true),
		TextUpdatable:  ptr(true),
		Shortnames:     []string{},
		Category:       ptr("GENERAL"),
	}
	assertObligationCreated(t, dto)

	t.Run("DeleteExistingObligation", func(t *testing.T) {
		w := makeRequest("DELETE", "/obligations/"+topic, nil, true)
		if w.Code != http.StatusNoContent {
			t.Fatalf("Expected status 204 No Content, got %d", w.Code)
		}
	})

	t.Run("DeleteNonExistentObligation", func(t *testing.T) {
		w := makeRequest("DELETE", "/obligations/"+topic, nil, true)
		if w.Code != http.StatusNoContent {
			t.Fatalf("Expected status 204 Not Found, got %d", w.Code)
		}
	})
}

func assertObligationCreated(t *testing.T, dto models.ObligationDTO) {
	w := makeRequest("POST", "/obligations", dto, true)
	if w.Code != http.StatusCreated {
		t.Fatalf("Expected 201 Created, got %d", w.Code)
	}

	var resp struct {
		Status int                    `json:"status"`
		Data   []models.ObligationDTO `json:"data"`
		Meta   any                    `json:"paginationmeta"`
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

	assertField("Topic", *dto.Topic, *ob.Topic)
	assertField("Type", *dto.Type, *ob.Type)
	assertField("Text", *dto.Text, *ob.Text)
	assertField("Comment", *dto.Comment, *ob.Comment)
	assertField("Category", *dto.Category, *ob.Category)
	assertField("Classification", *dto.Classification, *ob.Classification)
	assertField("Modifications", *dto.Modifications, *ob.Modifications)
	assertField("Active", *dto.Active, *ob.Active)
	assertField("TextUpdatable", *dto.TextUpdatable, *ob.TextUpdatable)
	assertField("Shortnames count", len(dto.Shortnames), len(ob.Shortnames))
}
func assertObligationUpdated(t *testing.T, topic string, dto models.ObligationUpdateDTO) {
	w := makeRequest("PATCH", "/obligations/"+topic, dto, true)
	if w.Code != http.StatusOK {
		t.Fatalf("Expected 200 OK, got %d", w.Code)
	}

	var resp struct {
		Status int                    `json:"status"`
		Data   []models.ObligationDTO `json:"data"`
		Meta   any                    `json:"paginationmeta"`
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
		assertField("Type", *dto.Type, *ob.Type)
	}
	if dto.Text != nil {
		assertField("Text", *dto.Text, *ob.Text)
	}
	if dto.Comment != nil {
		assertField("Comment", *dto.Comment, *ob.Comment)
	}
	if dto.Category != nil {
		assertField("Category", *dto.Category, *ob.Category)
	}
	if dto.Classification != nil {
		assertField("Classification", *dto.Classification, *ob.Classification)
	}
	if dto.Modifications != nil {
		assertField("Modifications", *dto.Modifications, *ob.Modifications)
	}
	if dto.Active != nil {
		assertField("Active", *dto.Active, *ob.Active)
	}
	if dto.TextUpdatable != nil {
		assertField("TextUpdatable", *dto.TextUpdatable, *ob.TextUpdatable)
	}
}
