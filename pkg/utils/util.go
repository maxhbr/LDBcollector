// SPDX-FileCopyrightText: 2023 Kavya Shukla <kavyuushukla@gmail.com>
// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Gaurav Mishra <mishra.gaurav@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package utils

import (
	"fmt"
	"html"
	"net/http"
	"strconv"
	"strings"
	"time"

	"golang.org/x/crypto/bcrypt"

	"github.com/gin-gonic/gin"

	"github.com/fossology/LicenseDb/pkg/models"
)

// The Converter function takes an input of type models.LicenseJson and converts it into a
// corresponding models.LicenseDB object.
// It performs several field assignments and transformations to create the LicenseDB object,
// including generating the SpdxId based on the SpdxCompatible field.
// The resulting LicenseDB object is returned as the output of this function.
func Converter(input models.LicenseJson) models.LicenseDB {
	spdxCompatible, err := strconv.ParseBool(input.SpdxCompatible)
	if err != nil {
		spdxCompatible = false
	}
	if spdxCompatible {
		input.SpdxCompatible = input.Shortname
	} else {
		input.SpdxCompatible = "LicenseRef-fossology-" + input.Shortname
	}

	copyleft, err := strconv.ParseBool(input.Copyleft)
	if err != nil {
		copyleft = false
	}
	fsfFree, err := strconv.ParseBool(input.FSFfree)
	if err != nil {
		fsfFree = false
	}
	osiApproved, err := strconv.ParseBool(input.OSIapproved)
	if err != nil {
		osiApproved = false
	}
	gplv2Compatible, err := strconv.ParseBool(input.GPLv2compatible)
	if err != nil {
		gplv2Compatible = false
	}
	gplv3Compatible, err := strconv.ParseBool(input.GPLv3compatible)
	if err != nil {
		gplv3Compatible = false
	}
	textUpdatable, err := strconv.ParseBool(input.TextUpdatable)
	if err != nil {
		textUpdatable = false
	}
	active, err := strconv.ParseBool(input.Active)
	if err != nil {
		active = false
	}
	marydone, err := strconv.ParseBool(input.Marydone)
	if err != nil {
		marydone = false
	}
	addDate, err := time.Parse(time.RFC3339, input.AddDate)
	if err != nil {
		addDate = time.Now()
	}
	detectorType := input.DetectorType
	risk, err := strconv.ParseInt(input.Risk, 10, 64)
	if err != nil {
		risk = 0
	}
	flag, err := strconv.ParseInt(input.Flag, 10, 64)
	if err != nil {
		flag = 1
	}

	result := models.LicenseDB{
		Shortname:       input.Shortname,
		Fullname:        input.Fullname,
		Text:            input.Text,
		Url:             input.Url,
		Copyleft:        copyleft,
		AddDate:         addDate,
		FSFfree:         fsfFree,
		OSIapproved:     osiApproved,
		GPLv2compatible: gplv2Compatible,
		GPLv3compatible: gplv3Compatible,
		Notes:           input.Notes,
		Fedora:          input.Fedora,
		TextUpdatable:   textUpdatable,
		DetectorType:    detectorType,
		Active:          active,
		Source:          input.Source,
		SpdxId:          input.SpdxCompatible,
		Risk:            risk,
		Flag:            flag,
		Marydone:        marydone,
	}
	return result
}

// ParseIdToInt convert the string ID from gin.Context to an integer and throw error if conversion fails. Also,
// update the gin.Context with REST API error.
func ParseIdToInt(c *gin.Context, id string, idType string) (int64, error) {
	parsedId, err := strconv.ParseInt(id, 10, 64)
	if err != nil {
		er := models.LicenseError{
			Status:    http.StatusBadRequest,
			Message:   fmt.Sprintf("invalid %s id", idType),
			Error:     err.Error(),
			Path:      c.Request.URL.Path,
			Timestamp: time.Now().Format(time.RFC3339),
		}
		c.JSON(http.StatusBadRequest, er)
		return 0, err
	}
	return parsedId, nil
}

// HashPassword hashes the password of the user using bcrypt. It also trims the
// username and escapes the HTML characters.
func HashPassword(user *models.User) error {
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(*user.Userpassword), bcrypt.DefaultCost)

	if err != nil {
		return err
	}
	*user.Userpassword = string(hashedPassword)

	user.Username = html.EscapeString(strings.TrimSpace(user.Username))

	return nil
}

// VerifyPassword compares the input password with the password stored in the
// database. Returns nil on success, or an error on failure.
func VerifyPassword(inputPassword, dbPassword string) error {
	return bcrypt.CompareHashAndPassword([]byte(dbPassword), []byte(inputPassword))
}
