-- Migration 002: Add is_active column to users table
-- Required for admin "deactivate account" feature
-- Date: 2026-07-28

ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active boolean NOT NULL DEFAULT true;
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
