-- SPDX-FileCopyrightText: 2025 Siemens AG
-- SPDX-FileCopyrightText: 2025 Dearsh Oberoi <oberoidearsh@gmail.com>
-- SPDX-License-Identifier: GPL-2.0-only

ALTER TABLE obligations DROP COLUMN modifications;
ALTER TABLE obligations DROP CONSTRAINT uni_obligations_md5;
ALTER TABLE obligations DROP COLUMN md5;
ALTER TABLE license_dbs DROP COLUMN rf_flag;