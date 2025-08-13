-- SPDX-FileCopyrightText: 2025 Siemens AG
-- SPDX-FileCopyrightText: 2025 Dearsh Oberoi <oberoidearsh@gmail.com>
-- SPDX-License-Identifier: GPL-2.0-only

ALTER TABLE license_dbs
ADD COLUMN rf_fsffree BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN rf_gplv2compatible BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN rf_gplv3compatible BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN rf_fedora TEXT NOT NULL DEFAULT '',
ADD COLUMN rf_detector_type BIGINT NOT NULL DEFAULT 1,
ADD COLUMN marydone BOOLEAN NOT NULL DEFAULT FALSE;

ALTER TABLE license_dbs DROP CONSTRAINT IF EXISTS shortname_not_empty;
ALTER TABLE license_dbs DROP CONSTRAINT IF EXISTS fullname_not_empty;
ALTER TABLE license_dbs DROP CONSTRAINT IF EXISTS text_not_empty;
ALTER TABLE license_dbs DROP CONSTRAINT IF EXISTS spdx_id_not_empty;
ALTER TABLE license_dbs DROP CONSTRAINT IF EXISTS risk_from_0_to_5;
ALTER TABLE license_dbs DROP CONSTRAINT IF EXISTS flag_from_0_to_2;