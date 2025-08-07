// SPDX-FileCopyrightText: 2025 Chayan Das <01chayandas@gmail.com>
//
// SPDX-License-Identifier: GPL-2.0-only

package models

// SimilarityRequest represents a request for similarity search
type SimilarLicense struct {
	Id         int64   `json:"id" gorm:"column:rf_id" example:"123"`
	Shortname  *string `json:"shortname" gorm:"column:rf_shortname" example:"MIT"`
	Text       *string `json:"text" gorm:"column:rf_text" example:"MIT License Text here"`
	Similarity float64 `json:"similarity"`
}

// SimilarObligation represents a similar obligation found in the database
type SimilarObligation struct {
	Id         int64   `gorm:"primary_key;column:id" json:"id" example:"123" `
	Topic      *string `gorm:"column:topic" json:"topic" example:"MIT license"`
	Text       *string `gorm:"column:text" json:"text"  example:"obligation text here"`
	Similarity float64 `json:"similarity"`
}

// SimilarityRequest represents a request for similarity search
type SimilarityRequest struct {
	Text string `json:"text" binding:"required"`
}
