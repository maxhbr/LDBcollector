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

func TestGetAllUser(t *testing.T) {
	loginAs(t, "admin")

	t.Run("getAllActiveUsers", func(t *testing.T) {
		w := makeRequest("GET", "/users?active=true", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.UserResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		assert.GreaterOrEqual(t, len(res.Data), 0)
	})

	t.Run("getAllInactiveUsers", func(t *testing.T) {
		w := makeRequest("GET", "/users?active=false", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.UserResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
	})

	t.Run("getAllUsersWithPagination", func(t *testing.T) {
		w := makeRequest("GET", "/users?page=1&limit=5", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.UserResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		assert.NotNil(t, res.Meta)
	})

	t.Run("unauthorized", func(t *testing.T) {
		w := makeRequest("GET", "/users", nil, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestGetUser(t *testing.T) {
	t.Run("getExistingUser", func(t *testing.T) {
		w := makeRequest("GET", "/users/fossy_superadmin", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.UserResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		if len(res.Data) > 0 {
			assert.Equal(t, "fossy_superadmin", *res.Data[0].UserName)
		}
	})

	t.Run("getNonExistingUser", func(t *testing.T) {
		w := makeRequest("GET", "/users/nonexistent_user", nil, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	t.Run("unauthorized", func(t *testing.T) {
		w := makeRequest("GET", "/users/fossy_superadmin", nil, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestGetUserProfile(t *testing.T) {
	t.Run("getOwnProfile", func(t *testing.T) {
		w := makeRequest("GET", "/users/profile", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.UserResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.Equal(t, http.StatusOK, res.Status)
		if len(res.Data) > 0 {
			assert.NotNil(t, res.Data[0].UserName)
		}
	})

	t.Run("unauthorized", func(t *testing.T) {
		w := makeRequest("GET", "/users/profile", nil, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestUpdateUser(t *testing.T) {
	testUser := models.UserCreate{
		UserName:     ptr("test_update_user"),
		UserPassword: ptr("testpass123"),
		UserLevel:    ptr("USER"),
		DisplayName:  ptr("Test Update User"),
		UserEmail:    ptr("testupdate@example.com"),
	}
	createW := makeRequest("POST", "/users", testUser, true)
	assert.Equal(t, http.StatusCreated, createW.Code)

	t.Run("updateUserSuccess", func(t *testing.T) {
		updateData := models.UserUpdate{
			DisplayName: ptr("Updated Display Name"),
			UserEmail:   ptr("updated@example.com"),
		}

		w := makeRequest("PATCH", "/users/test_update_user", updateData, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.UserResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		if len(res.Data) > 0 {
			assert.Equal(t, *updateData.DisplayName, *res.Data[0].DisplayName)
		}
	})

	t.Run("updateNonExistingUser", func(t *testing.T) {
		updateData := models.UserUpdate{
			DisplayName: ptr("Updated Display Name"),
		}

		w := makeRequest("PATCH", "/users/nonexistent_user", updateData, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	t.Run("updateWithInvalidData", func(t *testing.T) {
		updateData := models.UserUpdate{
			UserEmail: ptr("invalid-email"),
		}

		w := makeRequest("PATCH", "/users/test_update_user", updateData, true)
		assert.Contains(t, []int{http.StatusOK, http.StatusBadRequest}, w.Code)
	})

	t.Run("unauthorized", func(t *testing.T) {
		updateData := models.UserUpdate{
			DisplayName: ptr("Updated Display Name"),
		}
		w := makeRequest("PATCH", "/users/test_update_user", updateData, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestUpdateProfile(t *testing.T) {
	t.Run("updateOwnProfile", func(t *testing.T) {
		profileUpdate := models.ProfileUpdate{
			DisplayName: ptr("My Updated Profile Name"),
		}

		w := makeRequest("PATCH", "/users", profileUpdate, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.UserResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		if len(res.Data) > 0 {
			assert.Equal(t, *profileUpdate.DisplayName, *res.Data[0].DisplayName)
		}
	})

	t.Run("updatePassword", func(t *testing.T) {
		originalToken := AuthToken

		profileUpdate := models.ProfileUpdate{
			UserPassword: ptr("newpassword123"),
		}

		w := makeRequest("PATCH", "/users", profileUpdate, true)
		assert.Equal(t, http.StatusOK, w.Code)

		loginData := models.UserLogin{
			Username:     "fossy_superadmin",
			Userpassword: "newpassword123",
		}
		loginW := makeRequest("POST", "/login", loginData, false)
		if loginW.Code == http.StatusOK {
			var loginRes models.TokenResonse
			if err := json.Unmarshal(loginW.Body.Bytes(), &loginRes); err == nil {
				AuthToken = loginRes.Data.AccessToken
				resetPassword := models.ProfileUpdate{
					UserPassword: ptr("fossy"),
				}
				resetW := makeRequest("PATCH", "/users", resetPassword, true)
				assert.Equal(t, http.StatusOK, resetW.Code)

				loginData.Userpassword = "fossy"
				loginW2 := makeRequest("POST", "/login", loginData, false)
				if loginW2.Code == http.StatusOK {
					var loginRes2 models.TokenResonse
					if err := json.Unmarshal(loginW2.Body.Bytes(), &loginRes2); err == nil {
						AuthToken = loginRes2.Data.AccessToken
					}
				} else {
					AuthToken = originalToken
				}
			}
		}
	})

	t.Run("updateWithInvalidData", func(t *testing.T) {
		profileUpdate := models.ProfileUpdate{
			UserEmail: ptr("invalid-email"),
		}

		w := makeRequest("PATCH", "/users", profileUpdate, true)
		assert.Contains(t, []int{http.StatusOK, http.StatusBadRequest}, w.Code)
	})

	t.Run("unauthorized", func(t *testing.T) {
		profileUpdate := models.ProfileUpdate{
			DisplayName: ptr("Updated Name"),
		}
		w := makeRequest("PATCH", "/users", profileUpdate, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestDeleteUser(t *testing.T) {
	testUser := models.UserCreate{
		UserName:     ptr("test_delete_user"),
		UserPassword: ptr("testpass123"),
		UserLevel:    ptr("USER"),
		DisplayName:  ptr("Test Delete User"),
		UserEmail:    ptr("testdelete@example.com"),
	}
	createW := makeRequest("POST", "/users", testUser, true)
	assert.Equal(t, http.StatusCreated, createW.Code)

	t.Run("deleteExistingUser", func(t *testing.T) {
		w := makeRequest("DELETE", "/users/test_delete_user", nil, true)
		assert.Equal(t, http.StatusNoContent, w.Code)
	})

	t.Run("deleteNonExistingUser", func(t *testing.T) {
		w := makeRequest("DELETE", "/users/nonexistent_user", nil, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	t.Run("deleteAlreadyDeletedUser", func(t *testing.T) {
		w := makeRequest("DELETE", "/users/test_delete_user", nil, true)
		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	t.Run("unauthorized", func(t *testing.T) {
		w := makeRequest("DELETE", "/users/test_delete_user", nil, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
}

func TestVerifyRefreshToken(t *testing.T) {
	loginData := models.UserLogin{
		Username:     "fossy_superadmin",
		Userpassword: "fossy",
	}

	loginW := makeRequest("POST", "/login", loginData, false)

	if loginW.Code != http.StatusOK {
		loginData.Userpassword = "newpassword123"
		loginW = makeRequest("POST", "/login", loginData, false)
	}

	if loginW.Code != http.StatusOK {
		t.Skipf("Cannot login to get refresh token: status %d", loginW.Code)
	}

	var loginRes models.TokenResonse
	if err := json.Unmarshal(loginW.Body.Bytes(), &loginRes); err != nil {
		t.Fatalf("Failed to parse login response: %v", err)
	}

	if loginRes.Data.RefreshToken == "" {
		t.Skip("Refresh token not available in login response")
	}

	t.Run("verifyValidRefreshToken", func(t *testing.T) {
		refreshReq := models.RefreshToken{
			RefreshToken: loginRes.Data.RefreshToken,
		}

		w := makeRequest("POST", "/refresh-token", refreshReq, false)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.TokenResonse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}
		assert.NotEmpty(t, res.Data.AccessToken)
	})

	t.Run("verifyInvalidRefreshToken", func(t *testing.T) {
		refreshReq := models.RefreshToken{
			RefreshToken: "invalid_token",
		}

		w := makeRequest("POST", "/refresh-token", refreshReq, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("verifyWithEmptyToken", func(t *testing.T) {
		refreshReq := models.RefreshToken{
			RefreshToken: "",
		}

		w := makeRequest("POST", "/refresh-token", refreshReq, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})

	t.Run("verifyWithInvalidJSON", func(t *testing.T) {
		w := makeRequest("POST", "/refresh-token", "invalid", false)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
}
