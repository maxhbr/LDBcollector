-- SPDX-FileCopyrightText: 2025 Chayan Das <01chayandas@gmail.com>
-- SPDX-License-Identifier: GPL-2.0-only


CREATE TABLE IF NOT EXISTS obligation_licenses (
    obligation_id BIGINT NOT NULL,
    license_db_id BIGINT NOT NULL,
    PRIMARY KEY (obligation_id, license_db_id),
    CONSTRAINT fk_obligation_licenses_obligation FOREIGN KEY (obligation_id) REFERENCES obligations(id),
    CONSTRAINT fk_obligation_licenses_license_db FOREIGN KEY (license_db_id) REFERENCES license_dbs(rf_id)
);
