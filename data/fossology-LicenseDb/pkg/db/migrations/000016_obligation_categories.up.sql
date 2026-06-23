-- SPDX-FileCopyrightText: 2026 Siemens AG
-- SPDX-FileContributor: Dearsh Oberoi <dearsh.oberoi@siemens.com>
--
-- SPDX-License-Identifier: GPL-2.0-only

BEGIN;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS obligation_categories (
    id      UUID    NOT NULL PRIMARY KEY DEFAULT uuid_generate_v4(),
    category TEXT   NOT NULL UNIQUE,
    active  BOOLEAN NOT NULL DEFAULT TRUE
);

INSERT INTO obligation_categories (category) VALUES
    ('DISTRIBUTION'),
    ('PATENT'),
    ('INTERNAL'),
    ('CONTRACTUAL'),
    ('EXPORT_CONTROL'),
    ('GENERAL')
ON CONFLICT (category) DO NOTHING;

ALTER TABLE obligations ADD COLUMN obligation_category_id UUID;
ALTER TABLE obligations ADD CONSTRAINT fk_obligation_category FOREIGN KEY (obligation_category_id) REFERENCES obligation_categories(id);
UPDATE obligations SET obligation_category_id = (SELECT id FROM obligation_categories WHERE obligation_categories.category = obligations.category);
ALTER TABLE obligations DROP COLUMN category;
COMMIT;