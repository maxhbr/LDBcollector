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

func TestCreateLicense(t *testing.T) {
	license := models.LicenseCreateDTO{
		Shortname: "MIT",
		Fullname:  "MIT License",
		Text:      `MIT License copyright (c) <year> <copyright holders> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.`,
		Url:       "https://opensource.org/licenses/MIT",
		Notes:     "This license is OSI approved.",
		Source:    "spdx",
		SpdxId:    "MIT",
		Risk:      int64(2),
	}

	t.Run("success", func(t *testing.T) {
		w := makeRequest("POST", "/licenses", license, true)
		assert.Equal(t, http.StatusCreated, w.Code)
		var res models.LicenseResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling response: %v", err)
			return
		}
		if len(res.Data) == 0 {
			t.Fatal("Response data is empty, cannot validate fields")
		}
		assert.Equal(t, license.Shortname, res.Data[0].Shortname)
		assert.Equal(t, license.Fullname, res.Data[0].Fullname)
		assert.Equal(t, license.Text, res.Data[0].Text)
		assert.Equal(t, license.SpdxId, res.Data[0].SpdxId)
	})
	t.Run("missingFields", func(t *testing.T) {
		invalidLicense := models.LicenseCreateDTO{
			Shortname: "",
			Fullname:  "",
			Text:      "",
			Url:       "",
			SpdxId:    "",
			Notes:     "This license is OSI approved.",
			Risk:      int64(2),
		}
		w := makeRequest("POST", "/licenses", invalidLicense, true)
		assert.Equal(t, http.StatusBadRequest, w.Code)
	})
	t.Run("unauthorized", func(t *testing.T) {
		license := models.LicenseCreateDTO{
			Shortname: "UnauthorizedLicense",
			Fullname:  "Unauthorized License",
			Text:      "This license should not be created without authentication.",
			Url:       "https://licenses.org/unauthorized",
			SpdxId:    "UNAUTHORIZED",
			Notes:     "This license is OSI approved.",
			Risk:      int64(2),
		}
		w := makeRequest("POST", "/licenses", license, false)
		assert.Equal(t, http.StatusUnauthorized, w.Code)
	})
	t.Run("duplicateLicense", func(t *testing.T) {
		license := models.LicenseCreateDTO{
			Shortname: "Test1",
			Fullname:  "Blank ExternalRef License",
			Text:      "Test license with blank ExternalRef",
			Url:       "https://licenses.org/blankref",
			SpdxId:    "MIT",
			Source:    "spdx",
			Notes:     "This license is OSI approved.",
			Risk:      int64(2),
		}
		w1 := makeRequest("POST", "/licenses", license, true)
		assert.Equal(t, http.StatusCreated, w1.Code)

		w2 := makeRequest("POST", "/licenses", license, true)
		assert.Equal(t, http.StatusConflict, w2.Code)
	})

}

func TestGetLicense(t *testing.T) {
	license := models.LicenseResponseDTO{
		Shortname:     "MIT",
		Fullname:      "MIT License",
		Text:          "MIT License\n\nCopyright (c) <year> <copyright holders>\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n",
		Url:           "https://opensource.org/licenses/MIT",
		TextUpdatable: false,
		Active:        true,
		SpdxId:        "MIT",
	}
	t.Run("existingLicense", func(t *testing.T) {
		w := makeRequest("GET", "/licenses/MIT", nil, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.LicenseResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}

		assert.Equal(t, license.Shortname, res.Data[0].Shortname)
	})
	t.Run("nonExistingLicense", func(t *testing.T) {
		w := makeRequest("GET", "/licenses/NonExistentLicense", nil, true)
		assert.Equal(t, http.StatusNotFound, w.Code)

		var res models.LicenseResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}

		assert.Empty(t, res.Data)

	})

}

func TestUpdateLicense(t *testing.T) {

	expectedLicense := models.LicenseResponseDTO{
		Fullname:      "MIT License updated",
		Text:          "MIT License\n\nCopyright (c) <year> <copyright holders>\n\nPermission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n",
		Url:           "https://opensource.org/licenses/MIT",
		TextUpdatable: true,
		Active:        true,
		SpdxId:        "MIT",
	}
	t.Run("updatetextwithoutpermission", func(t *testing.T) {
		license := models.LicenseUpdateDTO{
			TextUpdatable: ptr(false),
		}
		// Attempt to update text without permission
		licenseToUpdate := models.LicenseUpdateDTO{
			Fullname:      ptr("MIT License updated"),
			Text:          ptr("updated text for MIT License"),
			Url:           ptr("https://opensource.org/licenses/MIT"),
			TextUpdatable: ptr(false),
			Active:        ptr(true),
			SpdxId:        ptr("MIT"),
		}
		w1 := makeRequest("PATCH", "/licenses/MIT", license, true)
		assert.Equal(t, http.StatusOK, w1.Code)

		w2 := makeRequest("PATCH", "/licenses/MIT", licenseToUpdate, true)
		assert.Equal(t, http.StatusBadRequest, w2.Code)

	})
	t.Run("UpdateExistingLicense", func(t *testing.T) {
		license := models.LicenseUpdateDTO{
			TextUpdatable: ptr(true),
		}
		w1 := makeRequest("PATCH", "/licenses/MIT", license, true)
		assert.Equal(t, http.StatusOK, w1.Code)

		w := makeRequest("PATCH", "/licenses/MIT", expectedLicense, true)
		assert.Equal(t, http.StatusOK, w.Code)

		var res models.LicenseResponse
		if err := json.Unmarshal(w.Body.Bytes(), &res); err != nil {
			t.Errorf("Error unmarshalling JSON: %v", err)
			return
		}

		assert.Equal(t, expectedLicense.Fullname, res.Data[0].Fullname)
		assert.Equal(t, expectedLicense.TextUpdatable, res.Data[0].TextUpdatable)
	})

	t.Run("UpdateNonExistingLicense", func(t *testing.T) {
		nonExistingLicense := models.LicenseUpdateDTO{
			Fullname:      ptr("Non Existent License"),
			Text:          ptr("This license does not exist."),
			Url:           ptr("https://licenses.org/nonexistent"),
			TextUpdatable: ptr(false),
			Active:        ptr(true),
			SpdxId:        ptr("NONEXISTENT"),
		}
		w := makeRequest("PATCH", "/licenses/NonExistentLicense", nonExistingLicense, true)
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
