-- ============================================================
-- Hotfix: infinite recursion in the "profiles" RLS policy
-- (Postgres error 42P17: "infinite recursion detected in policy
-- for relation \"profiles\"")
--
-- Cause: an earlier "Admins can view all profiles" policy checked
-- admin status with a raw subquery against profiles itself:
--
--   using (exists (select 1 from public.profiles where id = auth.uid() and role = 'admin'))
--
-- Evaluating that policy re-triggers the same policy on the same
-- table, forever. This file replaces it with the safe pattern:
-- a SECURITY DEFINER function, which runs with the privileges of
-- its owner and is therefore NOT subject to the RLS policy that
-- calls it, breaking the recursion.
--
-- Safe to re-run any time (idempotent). Run this in the Supabase
-- SQL Editor once against any project whose "profiles" policy
-- still has the old recursive form -- this is now also folded
-- into schema.sql for brand-new projects, so you only need this
-- file if your project predates that fix.
-- ============================================================

-- Make sure the admin-role column exists (no-op if already present).
alter table public.profiles
    add column if not exists role text not null default 'user' check (role in ('user', 'admin'));

-- The recursion-safe admin check.
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

-- Drop whatever version of the admin policy currently exists (the
-- recursive one, if that's what you have) and recreate it using the
-- safe function above.
drop policy if exists "Admins can view all profiles" on public.profiles;
create policy "Admins can view all profiles"
    on public.profiles for select
    using (public.is_admin(auth.uid()) or auth.uid() = id);

-- Same rationale applied to analyses/reports admin-visibility policies,
-- in case those were also created with an old recursive/unsafe form.
drop policy if exists "Admins can view all analyses" on public.analyses;
create policy "Admins can view all analyses"
    on public.analyses for select
    using (public.is_admin(auth.uid()) or auth.uid() = user_id);

drop policy if exists "Admins can view all reports" on public.reports;
create policy "Admins can view all reports"
    on public.reports for select
    using (public.is_admin(auth.uid()) or auth.uid() = user_id);

notify pgrst, 'reload schema';
