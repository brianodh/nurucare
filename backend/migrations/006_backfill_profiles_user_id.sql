-- Migration 006: One-time backfill of profiles.user_id
--
-- Historical bug: save_intake_data(session_id, ...) reused session_id as
-- profile_id directly, without ever writing profiles.user_id. For
-- authenticated patients, the JWT `sub` (== users.user_id) was passed in
-- as session_id, so profile_id == user_id by coincidence. We exploit that
-- coincidence here to set user_id explicitly so real JOINs work going
-- forward. Anonymous profiles (no matching users row) keep user_id = NULL
-- as intended.
--
-- WARNING: Run on a copy / backup of production data first.
-- Date: 2026-07-28

UPDATE profiles p
   SET user_id = u.user_id
  FROM users u
 WHERE p.profile_id = u.user_id
   AND p.user_id IS NULL;
