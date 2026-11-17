-- Optional extensions shared by ERP01 and extracted service modules.
-- Existing PostgreSQL volumes are not reinitialized by this file.
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
