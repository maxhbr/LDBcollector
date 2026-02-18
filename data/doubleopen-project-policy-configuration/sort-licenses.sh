#!/bin/env bash

# SPDX-FileCopyrightText: 2025 Double Open Oy <support@doubleopen.org>
# SPDX-License-Identifier: CC0-1.0

# Avoid multi-line strings being unwrapped by `yq`.
# This works around https://github.com/mikefarah/yq/issues/439.
sed -i 's,>-,|,g' license-classifications.yml

# Replace empty lines with marker comments.
# This works around https://github.com/mikefarah/yq/issues/515.
sed -i 's,^$,#EMPTY_LINE,g' license-classifications.yml

yq -i '.categorizations |= sort_by(.id)' license-classifications.yml

# Replace marker comments (with potential indentation added by `yq`) with empty lines.
sed -i 's, *#EMPTY_LINE,,g' license-classifications.yml

# Restore original folded blocks with stripped newlines.
sed -i 's,|,>-,g' license-classifications.yml
