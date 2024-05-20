// SPDX-FileCopyrightText: 2023 Siemens AG
// SPDX-FileContributor: Dearsh Oberoi <oberoidearsh@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package models

import (
	"encoding/json"
	"errors"
)

// When we unmarshal json, the undefined keys take zero values in structs. So, there
// is no way to differentiate between an undefined value and an actual zero value when
// it is passed. OptionalData is a generic for differentiating between undefined and
// zero valued keys in json.
type OptionalData[T any] struct {
	// This is set to true if corresponding key is present in json object
	IsDefined bool
	rawJson   json.RawMessage
	Value     T
}

func (v *OptionalData[T]) UnmarshalJSON(data []byte) error {
	v.rawJson = append((v.rawJson)[0:0], data...)
	if len(v.rawJson) != 0 {
		var x *T
		if err := json.Unmarshal(data, &x); err != nil {
			return err
		}
		if x == nil {
			return errors.New("field value cannot be null")
		}
		v.Value = *x
		v.IsDefined = true
	}
	return nil
}

type NullableAndOptionalData[T any] struct {
	// This is set to true if corresponding key is present in json object
	IsDefinedAndNotNull bool
	rawJson             json.RawMessage
	Value               T
}

func (v *NullableAndOptionalData[T]) UnmarshalJSON(data []byte) error {
	v.rawJson = append((v.rawJson)[0:0], data...)
	if len(v.rawJson) != 0 {
		var x *T
		if err := json.Unmarshal(data, &x); err != nil {
			return err
		}
		if x != nil {
			v.Value = *x
			v.IsDefinedAndNotNull = true
		}
	}
	return nil
}
