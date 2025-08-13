// SPDX-FileCopyrightText: 2025 Siemens AG
// SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package validations

import (
	"github.com/github/go-spdx/v2/spdxexp"
	"github.com/go-playground/validator/v10"
)

var Validate *validator.Validate

func spdxId(fl validator.FieldLevel) bool {
	valid, _ := spdxexp.ValidateLicenses([]string{fl.Field().String()})
	return valid
}

func RegisterValidations() error {
	Validate = validator.New(validator.WithRequiredStructEnabled())
	return Validate.RegisterValidation("spdxId", spdxId)
}
