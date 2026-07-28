-- Migration 001: Add 'admin' to users.role CHECK constraint
-- Applies to: Supabase and any existing local Postgres where the old constraint existed
-- Date: 2026-07-28

ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users ADD CONSTRAINT users_role_check
  CHECK (role IN ('patient', 'nurse', 'admin'));
