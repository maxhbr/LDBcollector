-- SPDX-FileCopyrightText: 2025 Siemens AG
-- SPDX-FileCopyrightText: 2025 Dearsh Oberoi <oberoidearsh@gmail.com>
-- SPDX-License-Identifier: GPL-2.0-only

ALTER TABLE license_dbs
DROP COLUMN rf_fsffree,
DROP COLUMN rf_gplv2compatible,
DROP COLUMN rf_gplv3compatible,
DROP COLUMN rf_fedora,
DROP COLUMN rf_detector_type,
DROP COLUMN marydone;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'shortname_not_empty'
    ) THEN
        ALTER TABLE license_dbs
        ADD CONSTRAINT shortname_not_empty CHECK (char_length(trim(rf_shortname)) > 0);
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'fullname_not_empty'
    ) THEN
        ALTER TABLE license_dbs
        ADD CONSTRAINT fullname_not_empty CHECK (char_length(trim(rf_fullname)) > 0);
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'text_not_empty'
    ) THEN
        ALTER TABLE license_dbs
        ADD CONSTRAINT text_not_empty CHECK (char_length(trim(rf_text)) > 0);
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'spdx_id_not_empty'
    ) THEN
        ALTER TABLE license_dbs
        ADD CONSTRAINT spdx_id_not_empty CHECK (char_length(trim(rf_spdx_id)) > 0);
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'risk_from_0_to_5'
    ) THEN
        ALTER TABLE license_dbs
        ADD CONSTRAINT risk_from_0_to_5 CHECK (rf_risk >= 0 AND rf_risk <= 5);
    END IF;
END$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'flag_from_0_to_2'
    ) THEN
        ALTER TABLE license_dbs
        ADD CONSTRAINT flag_from_0_to_2 CHECK (rf_flag >= 0 AND rf_flag <= 2);
    END IF;
END$$;