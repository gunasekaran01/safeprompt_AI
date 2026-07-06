-- ============================================================
-- SafePrompt AI — Supabase schema
-- Run this in the Supabase SQL Editor (Project -> SQL Editor).
-- ============================================================

-- ------------------------------------------------------------
-- Phase 2: user profiles
-- ------------------------------------------------------------

create extension if not exists pgcrypto;

-- One row per authenticated user, extending auth.users with the display
-- fields the app needs. id mirrors auth.users.id (1:1).
create table if not exists public.profiles (
    id uuid primary key references auth.users (id) on delete cascade,
    name text,
    email text not null,
    avatar_url text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- Keep updated_at current on every update, on any table that uses it.
create or replace function public.set_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists set_profiles_updated_at on public.profiles;
create trigger set_profiles_updated_at
    before update on public.profiles
    for each row
    execute function public.set_updated_at();

-- Auto-create a profile row whenever a new user signs up, seeded from
-- the signup metadata captured by the frontend's AuthContext.signUp()
-- call (supabase.auth.signUp({ options: { data: { name } } })).
create or replace function public.handle_new_user()
returns trigger as $$
begin
    insert into public.profiles (id, name, email, avatar_url)
    values (
        new.id,
        new.raw_user_meta_data ->> 'name',
        new.email,
        new.raw_user_meta_data ->> 'avatar_url'
    )
    on conflict (id) do nothing;
    return new;
end;
$$ language plpgsql security definer set search_path = public;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
    after insert on auth.users
    for each row
    execute function public.handle_new_user();

-- Row Level Security: a user may only see/edit their own profile.
-- (Inserts happen via the security-definer trigger above, so no insert
-- policy is granted directly to end users.)
alter table public.profiles enable row level security;

drop policy if exists "Users can view their own profile" on public.profiles;
create policy "Users can view their own profile"
    on public.profiles for select
    using (auth.uid() = id);

drop policy if exists "Users can update their own profile" on public.profiles;
create policy "Users can update their own profile"
    on public.profiles for update
    using (auth.uid() = id)
    with check (auth.uid() = id);

-- ------------------------------------------------------------
-- Admin support (safe pattern — avoids RLS self-recursion)
-- ------------------------------------------------------------
--
-- If you need an "is this caller an admin?" check in a policy, NEVER
-- write it as a subquery against the same table the policy is attached
-- to:
--
--   -- DO NOT DO THIS — causes "infinite recursion detected in policy
--   -- for relation profiles" (Postgres error 42P17):
--   using (exists (select 1 from public.profiles where id = auth.uid() and role = 'admin'))
--
-- Evaluating that policy re-triggers the same policy on the same table,
-- forever. Instead, wrap the check in a SECURITY DEFINER function, which
-- runs with the privileges of its owner and is NOT subject to the RLS
-- policy that calls it — breaking the recursion.

alter table public.profiles
    add column if not exists role text not null default 'user' check (role in ('user', 'admin'));

create or replace function public.is_admin(uid uuid)
returns boolean
language sql
security definer
set search_path = public
as $$
    select exists (
        select 1 from public.profiles where id = uid and role = 'admin'
    );
$$;

-- Grant admins read access to every profile, in addition to each user's
-- own-row policy above. Uses the safe helper function, not a raw subquery.
drop policy if exists "Admins can view all profiles" on public.profiles;
create policy "Admins can view all profiles"
    on public.profiles for select
    using (public.is_admin(auth.uid()) or auth.uid() = id);

-- ------------------------------------------------------------
-- Reconciliation fixes — safe to re-run if your live database was
-- created from an older/partial version of this schema and is now out
-- of sync (e.g. missing columns, stale PostgREST schema cache).
-- ------------------------------------------------------------

alter table public.analyses
    add column if not exists user_id uuid references auth.users (id) on delete cascade;

alter table public.analyses
    add column if not exists injection_detected boolean not null default false;
alter table public.analyses
    add column if not exists injection_confidence double precision not null default 0;
alter table public.analyses
    add column if not exists injection_reason text not null default '';
alter table public.analyses
    add column if not exists toxicity_detected boolean not null default false;
alter table public.analyses
    add column if not exists toxicity_category text not null default 'none';
alter table public.analyses
    add column if not exists toxicity_confidence double precision not null default 0;
alter table public.analyses
    add column if not exists toxicity_explanation text not null default '';
alter table public.analyses
    add column if not exists safety_score double precision not null default 0;
alter table public.analyses
    add column if not exists risk_level text not null default 'medium';
alter table public.analyses
    add column if not exists recommendation text not null default '';
alter table public.analyses
    add column if not exists reasoning text not null default '';

-- Force PostgREST to pick up any column/table changes immediately,
-- instead of waiting for its next automatic schema cache refresh.
notify pgrst, 'reload schema';

-- ------------------------------------------------------------
-- Phase 3: analyses, reports, user_settings + Row Level Security
-- ------------------------------------------------------------
--
-- IMPORTANT ARCHITECTURE NOTE:
-- The FastAPI backend connects to Supabase using the SERVICE ROLE key,
-- which bypasses RLS entirely by design. RLS below is real protection
-- for any client that queries these tables directly with a user's own
-- JWT (e.g. the anon key + session token) — but it is NOT what protects
-- data through our backend API. For API-mediated access, every backend
-- query MUST explicitly filter by user_id, which is what Phase 4 (the
-- next phase) implements. Treat RLS as defense-in-depth, not the sole
-- safeguard, given this architecture.

create extension if not exists pg_trgm;

-- analyses: one row per prompt safety analysis. Also serves the
-- "History" feature directly (History is just a filtered/paginated view
-- over this same table) — no separate history table is needed.
create table if not exists public.analyses (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    prompt text not null,
    injection_detected boolean not null,
    injection_confidence double precision not null,
    injection_reason text not null,
    toxicity_detected boolean not null,
    toxicity_category text not null,
    toxicity_confidence double precision not null,
    toxicity_explanation text not null,
    safety_score double precision not null,
    risk_level text not null check (risk_level in ('safe', 'low', 'medium', 'high', 'critical')),
    recommendation text not null,
    reasoning text not null,
    created_at timestamptz not null default now()
);

create index if not exists analyses_user_id_idx on public.analyses (user_id);
create index if not exists analyses_created_at_idx on public.analyses (created_at desc);
create index if not exists analyses_risk_level_idx on public.analyses (risk_level);
create index if not exists analyses_prompt_trgm_idx on public.analyses using gin (prompt gin_trgm_ops);

alter table public.analyses enable row level security;

drop policy if exists "Users can view their own analyses" on public.analyses;
create policy "Users can view their own analyses"
    on public.analyses for select
    using (auth.uid() = user_id);

drop policy if exists "Users can insert their own analyses" on public.analyses;
create policy "Users can insert their own analyses"
    on public.analyses for insert
    with check (auth.uid() = user_id);

drop policy if exists "Users can delete their own analyses" on public.analyses;
create policy "Users can delete their own analyses"
    on public.analyses for delete
    using (auth.uid() = user_id);

-- No update policy: analyses are immutable once created (matches the
-- History feature's spec, which only ever needs read + delete).

-- Per-user aggregate stats, powering the Dashboard. Grouped by user_id
-- so each user's row only reflects their own analyses.
create or replace view public.analyses_stats as
select
    user_id,
    count(*) as total_analyses,
    count(*) filter (where risk_level in ('safe', 'low')) as safe_prompts,
    count(*) filter (where risk_level in ('medium', 'high', 'critical')) as unsafe_prompts,
    count(*) filter (where injection_detected) as injection_attempts,
    count(*) filter (where toxicity_detected) as toxic_prompts,
    coalesce(avg(safety_score), 0) as average_safety_score,
    count(*) filter (where risk_level = 'safe') as safe_count,
    count(*) filter (where risk_level = 'low') as low_count,
    count(*) filter (where risk_level = 'medium') as medium_count,
    count(*) filter (where risk_level = 'high') as high_count,
    count(*) filter (where risk_level = 'critical') as critical_count
from public.analyses
group by user_id;

-- reports: metadata for generated PDF reports (Phase 6 populates this;
-- table + RLS exist now so the storage layer is ready ahead of time).
create table if not exists public.reports (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    analysis_id uuid references public.analyses (id) on delete cascade,
    file_path text,
    generated_at timestamptz not null default now()
);

create index if not exists reports_user_id_idx on public.reports (user_id);
create index if not exists reports_analysis_id_idx on public.reports (analysis_id);

alter table public.reports enable row level security;

drop policy if exists "Users can view their own reports" on public.reports;
create policy "Users can view their own reports"
    on public.reports for select
    using (auth.uid() = user_id);

drop policy if exists "Users can insert their own reports" on public.reports;
create policy "Users can insert their own reports"
    on public.reports for insert
    with check (auth.uid() = user_id);

drop policy if exists "Users can delete their own reports" on public.reports;
create policy "Users can delete their own reports"
    on public.reports for delete
    using (auth.uid() = user_id);

-- user_settings: server-synced version of the preferences currently
-- stored client-side in localStorage (theme, compact mode, auto-analyze).
-- One row per user; Phase 7 wires the frontend/backend to read/write it.
create table if not exists public.user_settings (
    user_id uuid primary key references auth.users (id) on delete cascade,
    theme text not null default 'system' check (theme in ('light', 'dark', 'system')),
    compact_mode boolean not null default false,
    auto_analyze_on_paste boolean not null default false,
    updated_at timestamptz not null default now()
);

drop trigger if exists set_user_settings_updated_at on public.user_settings;
create trigger set_user_settings_updated_at
    before update on public.user_settings
    for each row
    execute function public.set_updated_at();

alter table public.user_settings enable row level security;

drop policy if exists "Users can view their own settings" on public.user_settings;
create policy "Users can view their own settings"
    on public.user_settings for select
    using (auth.uid() = user_id);

drop policy if exists "Users can insert their own settings" on public.user_settings;
create policy "Users can insert their own settings"
    on public.user_settings for insert
    with check (auth.uid() = user_id);

drop policy if exists "Users can update their own settings" on public.user_settings;
create policy "Users can update their own settings"
    on public.user_settings for update
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);
