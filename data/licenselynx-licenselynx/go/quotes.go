// SPDX-FileCopyrightText: Copyright 2026 Siemens AG
// SPDX-License-Identifier: BSD-3-Clause

package licenselynx

import "strings"

var quoteReplacements = map[rune]rune{
	'\u2018': '\'',
	'\u2019': '\'',
	'\u201A': '\'',
	'\u201B': '\'',
	'\u2032': '\'',
	'\uFF07': '\'',
	'\u201C': '\'',
	'\u201D': '\'',
	'\u201E': '\'',
	'\u201F': '\'',
	'\u2033': '\'',
	'\u00AB': '\'',
	'\u00BB': '\'',
	'\uFF02': '\'',
}

func normalizeQuotes(input string) string {
	if input == "" {
		return input
	}

	return strings.Map(func(r rune) rune {
		if replacement, ok := quoteReplacements[r]; ok {
			return replacement
		}

		return r
	}, input)
}
