-- SPDX-FileCopyrightText: 2026 Vishesh Gupta <vishesh15th@gmail.com>
-- SPDX-License-Identifier: GPL-2.0-only

ALTER TABLE users ADD COLUMN subscribed BOOLEAN DEFAULT FALSE;
