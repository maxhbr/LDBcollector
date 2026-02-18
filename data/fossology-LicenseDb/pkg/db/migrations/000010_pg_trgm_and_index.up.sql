-- SPDX-FileCopyrightText: 2025 Chayan Das <01chayandas@gmail.com>
-- SPDX-License-Identifier: GPL-2.0-only

-- Enable pg_trgm extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create GiST index for fuzzy search on rf_text (license)
CREATE INDEX IF NOT EXISTS gist_rf_text_idx
ON license_dbs USING gist (rf_text gist_trgm_ops);

-- Create GiST index for fuzzy search on text (obligation)
CREATE INDEX IF NOT EXISTS gist_text_idx
ON obligations USING gist (text gist_trgm_ops);

