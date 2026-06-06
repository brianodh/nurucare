-- NuruCare Supabase schema for clinical profiles and secure collaboration tokens

create extension if not exists pgcrypto;
create extension if not exists vector;

create table profiles (
  profile_id uuid primary key default gen_random_uuid(),
  age int not null,
  systolic_bp int not null,
  diastolic_bp int not null,
  smoking boolean not null default false,
  migraine_type varchar(50) not null default 'none',
  breastfeeding boolean not null default false,
  postpartum_weeks int,
  last_period_date date,
  duration_pref varchar(50),
  side_effects jsonb,
  sync_token_hash varchar(255),
  restricted_methods jsonb,
  allowed_methods jsonb,
  explanations jsonb,
  confidence_score numeric(5,2),
  created_at timestamptz not null default now()
);

create table partner_sync (
  sync_id uuid primary key default gen_random_uuid(),
  profile_id uuid references profiles(profile_id) on delete cascade,
  sync_token_hash varchar(255) not null,
  expires_at timestamptz not null,
  created_at timestamptz not null default now()
);

create table nurse_sessions (
  session_id uuid primary key default gen_random_uuid(),
  profile_id uuid references profiles(profile_id) on delete cascade,
  access_code varchar(6) not null,
  expires_at timestamptz not null,
  used boolean not null default false,
  created_at timestamptz not null default now()
);

create index idx_profiles_age on profiles(age);
create index idx_partner_sync_expires_at on partner_sync(expires_at);
create index idx_nurse_sessions_expires_at on nurse_sessions(expires_at);
