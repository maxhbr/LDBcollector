-- SPDX-FileCopyrightText: 2025 Siemens AG
-- SPDX-FileCopyrightText: 2025 Dearsh Oberoi <oberoidearsh@gmail.com>
-- SPDX-License-Identifier: GPL-2.0-only

ALTER TABLE obligations ADD COLUMN modifications BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE obligations ADD COLUMN md5 TEXT NOT NULL;
ALTER TABLE obligations ADD CONSTRAINT uni_obligations_md5 UNIQUE (md5);
ALTER TABLE license_dbs ADD COLUMN rf_flag BIGINT NOT NULL DEFAULT 0;