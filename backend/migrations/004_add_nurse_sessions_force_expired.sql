-- Migration 004: Add force_expired flag to nurse_sessions
-- Lets admins immediately invalidate a 6-digit access code
-- Date: 2026-07-28

ALTER TABLE nurse_sessions ADD COLUMN IF NOT EXISTS force_expired boolean NOT NULL DEFAULT false;
