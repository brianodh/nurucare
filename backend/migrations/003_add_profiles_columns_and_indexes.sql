-- Migration 003: Add missing columns to profiles + FK index on user_id
-- Date: 2026-07-28

-- intake_channel column (default 'web' 'ussd' set by USSD flow)
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS intake_channel varchar(20) NOT NULL DEFAULT 'web';
CREATE INDEX IF NOT EXISTS idx_profiles_intake_channel ON profiles(intake_channel);

-- Critical: profiles.user_id links authenticated users → their profile row.
-- Without this index JOINs on p.user_id = u.user_id are sequential scans.
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);
