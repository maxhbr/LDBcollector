// SPDX-FileCopyrightText: Copyright 2026 Siemens AG
// SPDX-License-Identifier: BSD-3-Clause

package licenselynx

import (
	"fmt"
	"testing"
)

func TestNormalizeQuotes(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name  string
		input string
		want  string
	}{
		{name: "empty string", input: "", want: ""},
		{name: "ascii unchanged", input: "Apache-2.0", want: "Apache-2.0"},
		{name: "mixed quotes", input: "“MIT” and ‘BSD’", want: "'MIT' and 'BSD'"},
	}

	for quote := range quoteReplacements {
		tests = append(tests, struct {
			name  string
			input string
			want  string
		}{
			name:  fmt.Sprintf("replaces %U", quote),
			input: string([]rune{'a', quote, 'b'}),
			want:  "a'b",
		})
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()
			if got := normalizeQuotes(test.input); got != test.want {
				t.Fatalf("normalizeQuotes mismatch: got %q want %q", got, test.want)
			}
		})
	}
}
