-- SPDX-FileCopyrightText: 2025 Siemens AG
-- SPDX-FileCopyrightText: 2025 Dearsh Oberoi <oberoidearsh@gmail.com>
-- SPDX-License-Identifier: GPL-2.0-only

BEGIN;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Introduce UUID column to serve as a potential primary key in the tables

ALTER TABLE users ADD COLUMN IF NOT EXISTS uuid UUID DEFAULT uuid_generate_v4();
UPDATE users SET uuid = uuid_generate_v4() WHERE uuid IS NULL;

ALTER TABLE license_dbs ADD COLUMN IF NOT EXISTS uuid UUID DEFAULT uuid_generate_v4();
UPDATE license_dbs SET uuid = uuid_generate_v4() WHERE uuid IS NULL;

ALTER TABLE obligation_types ADD COLUMN IF NOT EXISTS uuid UUID DEFAULT uuid_generate_v4();
UPDATE obligation_types SET uuid = uuid_generate_v4() WHERE uuid IS NULL;

ALTER TABLE obligation_classifications ADD COLUMN IF NOT EXISTS uuid UUID DEFAULT uuid_generate_v4();
UPDATE obligation_classifications SET uuid = uuid_generate_v4() WHERE uuid IS NULL;

ALTER TABLE obligations ADD COLUMN IF NOT EXISTS uuid UUID DEFAULT uuid_generate_v4();
UPDATE obligations SET uuid = uuid_generate_v4() WHERE uuid IS NULL;

ALTER TABLE audits ADD COLUMN IF NOT EXISTS uuid UUID DEFAULT uuid_generate_v4();
UPDATE audits SET uuid = uuid_generate_v4() WHERE uuid IS NULL;

ALTER TABLE change_logs ADD COLUMN IF NOT EXISTS uuid UUID DEFAULT uuid_generate_v4();
UPDATE change_logs SET uuid = uuid_generate_v4() WHERE uuid IS NULL;

ALTER TABLE oidc_clients ADD COLUMN IF NOT EXISTS uuid UUID DEFAULT uuid_generate_v4();
UPDATE oidc_clients SET uuid = uuid_generate_v4() WHERE uuid IS NULL;

-- Introduce UUID column to serve as a potential foreign key in the tables

ALTER TABLE license_dbs ADD COLUMN IF NOT EXISTS user_uuid UUID;
UPDATE license_dbs SET user_uuid = (SELECT uuid from users WHERE license_dbs.user_id = users.id);
ALTER TABLE license_dbs ALTER COLUMN user_uuid SET NOT NULL;

ALTER TABLE obligations ADD COLUMN IF NOT EXISTS obligation_classification_uuid UUID;
UPDATE obligations SET obligation_classification_uuid = (SELECT uuid from obligation_classifications 
WHERE obligations.obligation_classification_id = obligation_classifications.id);
ALTER TABLE obligations ALTER COLUMN obligation_classification_uuid SET NOT NULL;

ALTER TABLE obligations ADD COLUMN IF NOT EXISTS obligation_type_uuid UUID;
UPDATE obligations SET obligation_type_uuid = (SELECT uuid from obligation_types 
WHERE obligations.obligation_type_id = obligation_types.id);
ALTER TABLE obligations ALTER COLUMN obligation_type_uuid SET NOT NULL;

ALTER TABLE audits ADD COLUMN IF NOT EXISTS user_uuid UUID;
UPDATE audits SET user_uuid = (SELECT uuid FROM users WHERE audits.user_id = users.id);
ALTER TABLE audits ALTER COLUMN user_uuid SET NOT NULL;

ALTER TABLE audits ADD COLUMN IF NOT EXISTS type_uuid UUID;
UPDATE audits
SET type_uuid = CASE
  WHEN type = 'LICENSE' THEN (SELECT uuid FROM license_dbs WHERE license_dbs.rf_id = audits.type_id)
  WHEN type = 'OBLIGATION' THEN (SELECT uuid FROM obligations WHERE obligations.id = audits.type_id)
  WHEN type = 'USER' THEN (SELECT uuid FROM users WHERE users.id = audits.type_id)
  WHEN type = 'TYPE' THEN (SELECT uuid FROM obligation_types WHERE obligation_types.id = audits.type_id)
  WHEN type = 'CLASSIFICATION' THEN (SELECT uuid FROM obligation_classifications WHERE obligation_classifications.id = audits.type_id)
END;
ALTER TABLE audits ALTER COLUMN type_uuid SET NOT NULL;

ALTER TABLE change_logs ADD COLUMN IF NOT EXISTS audit_uuid UUID;
UPDATE change_logs SET audit_uuid = (SELECT uuid from audits WHERE change_logs.audit_id = audits.id);
ALTER TABLE change_logs ALTER COLUMN audit_uuid SET NOT NULL;

ALTER TABLE obligation_licenses ADD COLUMN IF NOT EXISTS license_uuid UUID;
UPDATE obligation_licenses SET license_uuid = (SELECT uuid from license_dbs WHERE license_dbs.rf_id = obligation_licenses.license_db_id);
ALTER TABLE obligation_licenses ALTER COLUMN license_uuid SET NOT NULL;

ALTER TABLE obligation_licenses ADD COLUMN IF NOT EXISTS obligation_uuid UUID;
UPDATE obligation_licenses SET obligation_uuid = (SELECT uuid from obligations WHERE obligations.id = obligation_licenses.obligation_id);
ALTER TABLE obligation_licenses ALTER COLUMN obligation_uuid SET NOT NULL;

ALTER TABLE oidc_clients ADD COLUMN IF NOT EXISTS user_uuid UUID;
UPDATE oidc_clients SET user_uuid = (SELECT uuid from users WHERE oidc_clients.user_id = users.id);
ALTER TABLE oidc_clients ALTER COLUMN user_uuid SET NOT NULL;

-- Drop old unwanted columns, rename new ones to appropriate names

ALTER TABLE oidc_clients DROP COLUMN IF EXISTS user_id;
ALTER TABLE oidc_clients DROP COLUMN IF EXISTS id;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='oidc_clients' AND column_name='user_uuid') THEN
    ALTER TABLE oidc_clients RENAME COLUMN user_uuid TO user_id;
  END IF;
END$$;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='oidc_clients' AND column_name='uuid') THEN
    ALTER TABLE oidc_clients RENAME COLUMN uuid TO id;
  END IF;
END$$;

ALTER TABLE obligation_licenses DROP COLUMN IF EXISTS license_db_id;
ALTER TABLE obligation_licenses DROP COLUMN IF EXISTS obligation_id;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='obligation_licenses' AND column_name='license_uuid') THEN
    ALTER TABLE obligation_licenses RENAME COLUMN license_uuid TO license_db_id;
  END IF;
END$$;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='obligation_licenses' AND column_name='obligation_uuid') THEN
    ALTER TABLE obligation_licenses RENAME COLUMN obligation_uuid TO obligation_id;
  END IF;
END$$;

ALTER TABLE change_logs DROP COLUMN IF EXISTS audit_id;
ALTER TABLE change_logs DROP COLUMN IF EXISTS id;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='change_logs' AND column_name='audit_uuid') THEN
    ALTER TABLE change_logs RENAME COLUMN audit_uuid TO audit_id;
  END IF;
END$$;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='change_logs' AND column_name='uuid') THEN
    ALTER TABLE change_logs RENAME COLUMN uuid TO id;
  END IF;
END$$;

ALTER TABLE audits DROP COLUMN IF EXISTS type_id;
ALTER TABLE audits DROP COLUMN IF EXISTS user_id;
ALTER TABLE audits DROP COLUMN IF EXISTS id;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='audits' AND column_name='type_uuid') THEN
    ALTER TABLE audits RENAME COLUMN type_uuid TO type_id;
  END IF;
END$$;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='audits' AND column_name='user_uuid') THEN
    ALTER TABLE audits RENAME COLUMN user_uuid TO user_id;
  END IF;
END$$;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='audits' AND column_name='uuid') THEN
    ALTER TABLE audits RENAME COLUMN uuid TO id;
  END IF;
END$$;


ALTER TABLE obligations DROP COLUMN IF EXISTS id;
ALTER TABLE obligations DROP COLUMN IF EXISTS obligation_type_id;
ALTER TABLE obligations DROP COLUMN IF EXISTS obligation_classification_id;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='obligations' AND column_name='uuid') THEN
    ALTER TABLE obligations RENAME COLUMN uuid TO id;
  END IF;
END$$;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='obligations' AND column_name='obligation_type_uuid') THEN
    ALTER TABLE obligations RENAME COLUMN obligation_type_uuid TO obligation_type_id;
  END IF;
END$$;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='obligations' AND column_name='obligation_classification_uuid') THEN
    ALTER TABLE obligations RENAME COLUMN obligation_classification_uuid TO obligation_classification_id;
  END IF;
END$$;

ALTER TABLE obligation_classifications DROP COLUMN IF EXISTS id;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='obligation_classifications' AND column_name='uuid') THEN
    ALTER TABLE obligation_classifications RENAME COLUMN uuid TO id;
  END IF;
END$$;

ALTER TABLE obligation_types DROP COLUMN IF EXISTS id;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='obligation_types' AND column_name='uuid') THEN
    ALTER TABLE obligation_types RENAME COLUMN uuid TO id;
  END IF;
END$$;

ALTER TABLE license_dbs DROP COLUMN IF EXISTS rf_id;
ALTER TABLE license_dbs DROP COLUMN IF EXISTS user_id;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='license_dbs' AND column_name='uuid') THEN
    ALTER TABLE license_dbs RENAME COLUMN uuid TO rf_id;
  END IF;
END$$;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='license_dbs' AND column_name='user_uuid') THEN
    ALTER TABLE license_dbs RENAME COLUMN user_uuid TO user_id;
  END IF;
END$$;

ALTER TABLE users DROP COLUMN IF EXISTS id;
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='uuid') THEN
    ALTER TABLE users RENAME COLUMN uuid to id;
  END IF;
END$$;

-- Add primary key and foreign key constraints

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'users_pkey'
  ) THEN
    ALTER TABLE users ADD CONSTRAINT users_pkey PRIMARY KEY (id);
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'license_dbs_pkey'
  ) THEN
    ALTER TABLE license_dbs ADD CONSTRAINT license_dbs_pkey PRIMARY KEY (rf_id);
  END IF;
END$$;
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'fk_license_dbs_user'
  ) THEN
    ALTER TABLE license_dbs ADD CONSTRAINT fk_license_dbs_user FOREIGN KEY (user_id) REFERENCES users(id);
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'obligation_classifications_pkey'
  ) THEN
    ALTER TABLE obligation_classifications ADD CONSTRAINT obligation_classifications_pkey PRIMARY KEY (id);
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'obligation_types_pkey'
  ) THEN
    ALTER TABLE obligation_types ADD CONSTRAINT obligation_types_pkey PRIMARY KEY (id);
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'obligations_pkey'
  ) THEN
    ALTER TABLE obligations ADD CONSTRAINT obligations_pkey PRIMARY KEY (id);
  END IF;
END$$;
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'fk_obligations_classification'
  ) THEN
    ALTER TABLE obligations ADD CONSTRAINT fk_obligations_classification FOREIGN KEY (obligation_classification_id) REFERENCES obligation_classifications(id);
  END IF;
END$$;
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'fk_obligations_type'
  ) THEN
    ALTER TABLE obligations ADD CONSTRAINT fk_obligations_type FOREIGN KEY (obligation_type_id) REFERENCES obligation_types(id);
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'audits_pkey'
  ) THEN
    ALTER TABLE audits ADD CONSTRAINT audits_pkey PRIMARY KEY (id);
  END IF;
END$$;
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'fk_audits_user'
  ) THEN
    ALTER TABLE audits ADD CONSTRAINT fk_audits_user FOREIGN KEY (user_id) REFERENCES users(id);
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'change_logs_pkey'
  ) THEN
    ALTER TABLE change_logs ADD CONSTRAINT change_logs_pkey PRIMARY KEY (id);
  END IF;
END$$;
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname ='fk_audits_change_logs'
  ) THEN
    ALTER TABLE change_logs ADD CONSTRAINT fk_audits_change_logs FOREIGN KEY (audit_id) REFERENCES audits(id);
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname ='fk_obligation_licenses_obligation'
  ) THEN
    ALTER TABLE obligation_licenses ADD CONSTRAINT fk_obligation_licenses_obligation FOREIGN KEY (obligation_id) REFERENCES obligations(id);
  END IF;
END$$;
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname ='fk_obligation_licenses_license_db'
  ) THEN
    ALTER TABLE obligation_licenses ADD CONSTRAINT fk_obligation_licenses_license_db FOREIGN KEY (license_db_id) REFERENCES license_dbs(rf_id);
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'obligation_licenses_pkey'
  ) THEN
    ALTER TABLE obligation_licenses 
      ADD CONSTRAINT obligation_licenses_pkey
      PRIMARY KEY (obligation_id, license_db_id);
  END IF;
END$$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname ='oidc_clients_pkey'
  ) THEN
    ALTER TABLE oidc_clients ADD CONSTRAINT oidc_clients_pkey PRIMARY KEY (id);
  END IF;
END$$;
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname ='fk_oidc_clients_users'
  ) THEN
    ALTER TABLE oidc_clients ADD CONSTRAINT fk_oidc_clients_users FOREIGN KEY (user_id) REFERENCES users(id);
  END IF;
END$$;

-- Remove unique constraints

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname ='uq_license_dbs_shortname'
  ) THEN
    ALTER TABLE license_dbs DROP CONSTRAINT uq_license_dbs_shortname;
  END IF;
END$$;

DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname ='uni_obligations_topic'
  ) THEN
    ALTER TABLE obligations DROP CONSTRAINT uni_obligations_topic;
  END IF;
END$$;

COMMIT;