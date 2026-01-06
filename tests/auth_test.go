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

func TestLoginUser(t *testing.T) {
	t.Run("login as superadmin", func(t *testing.T) {
		loginAs(t, "superadmin")
	})

	t.Run("login as admin", func(t *testing.T) {
		loginAs(t, "admin")
	})

	t.Run("wrong password", func(t *testing.T) {
		logindata := models.UserLogin{
			Username:     "fossy_superadmin",
			Userpassword: "wrong-password",
		}

		w := makeRequest("POST", "/login", logindata, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestCreateUser(t *testing.T) {
	t.Run("Success", func(t *testing.T) {
		user := models.UserCreate{
			UserName:     ptr("fossy-test"),
			UserPassword: ptr("abc123"),
			UserLevel:    ptr("ADMIN"),
			DisplayName:  ptr("fossy-test"),
			UserEmail:    ptr("fossy-test@gmail.com"),
		}
		w := makeRequest("POST", "/users", user, true)
		assert.Equal(t, http.StatusCreated, w.Code)

		var res models.UserResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, *user.UserName, *res.Data[0].UserName)
		assert.Equal(t, *user.UserLevel, *res.Data[0].UserLevel)
	})

	t.Run("MissingFields", func(t *testing.T) {
		user := models.UserCreate{}
		w := makeRequest("POST", "/users", user, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
	t.Run("DuplicateUser", func(t *testing.T) {
		user := models.UserCreate{
			UserName:     ptr("fossy2"),
			UserPassword: ptr("abc123"),
			UserLevel:    ptr("ADMIN"),
			DisplayName:  ptr("fossy2"),
			UserEmail:    ptr("fossy2@gmail.com"),
		}

		// First request should succeed
		w1 := makeRequest("POST", "/users", user, true)
		assert.Equal(t, http.StatusCreated, w1.Code)

		// Second request with same user should fail
		w2 := makeRequest("POST", "/users", user, true)
		assert.Equal(t, http.StatusConflict, w2.Code)
	})

	t.Run("Unauthorized", func(t *testing.T) {
		user := models.UserCreate{
			UserName:     ptr("fossy2"),
			UserPassword: ptr("abc123"),
			UserLevel:    ptr("ADMIN"),
			DisplayName:  ptr("fossy2"),
			UserEmail:    ptr("fossy2@gmail.com"),
		}
		w := makeRequest("POST", "/users", user, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

// loginAs logs in as the given user type ("superadmin" or "admin") and sets AuthToken.
func loginAs(t *testing.T, userType string) {
	var username string

	switch userType {
	case "superadmin":
		username = "fossy_superadmin"
	case "admin":
		username = "fossy_admin"
	default:
		t.Fatalf("Invalid user type provided: %s", userType)
	}

	logindata := models.UserLogin{
		Username:     username,
		Userpassword: "fossy",
	}

	w := makeRequest("POST", "/login", logindata, false)

	if w.Code != http.StatusOK {
		t.Fatalf("[%s] login failed with status: %d, body: %s", userType, w.Code, w.Body.String())
	}

	var resp map[string]interface{}
	if err := json.Unmarshal(w.Body.Bytes(), &resp); err != nil {
		t.Fatalf("Failed to parse login response: %v", err)
	}

	data, ok := resp["data"].(map[string]interface{})
	if !ok {
		t.Fatalf("Response 'data' field missing or invalid. Got: %v", resp)
	}

	token, ok := data["access_token"].(string)
	if !ok || token == "" {
		t.Fatalf("access_token not found in response. Got: %v", data)
	}

	assert.NotEmpty(t, token, "Auth token should not be empty")

	AuthToken = token
}
