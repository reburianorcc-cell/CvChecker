-- Run once in the Supabase SQL Editor before using reusable TORs.
create table if not exists public.cv_tor_library (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    filename text not null,
    tor_text text not null,
    requirements jsonb not null default '[]'::jsonb,
    created_at timestamptz not null default now()
);
create index if not exists cv_tor_library_name_idx on public.cv_tor_library(name);
-- The app uses the existing server-side Supabase secret/service_role key.
-- Do not expose that key to browser clients. Configure RLS/access policies
-- according to your deployment's authentication model.
