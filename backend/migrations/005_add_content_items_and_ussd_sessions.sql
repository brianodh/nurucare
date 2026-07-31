-- Migration 005: content_items + ussd_sessions tables (admin console + offline flow)
-- Date: 2026-07-28

CREATE TABLE IF NOT EXISTS content_items (
  content_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  content_type varchar(50) NOT NULL,
  item_key varchar(100) NOT NULL,
  content_data jsonb NOT NULL,
  version int NOT NULL DEFAULT 1,
  updated_by uuid REFERENCES users(user_id),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (content_type, item_key)
);
CREATE INDEX IF NOT EXISTS idx_content_items_type ON content_items(content_type);

CREATE TABLE IF NOT EXISTS ussd_sessions (
  ussd_session_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  external_session_id varchar(255),
  phone_number varchar(50),
  service_code varchar(50),
  status varchar(20) NOT NULL DEFAULT 'active',
  steps_completed int NOT NULL DEFAULT 0,
  profile_id uuid REFERENCES profiles(profile_id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  completed_at timestamptz
);
CREATE INDEX IF NOT EXISTS idx_ussd_sessions_status ON ussd_sessions(status);
CREATE INDEX IF NOT EXISTS idx_ussd_sessions_created_at ON ussd_sessions(created_at);

CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
