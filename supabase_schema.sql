create extension if not exists pgcrypto;

create table if not exists public.cv_evaluations (
    id uuid primary key default gen_random_uuid(),
    candidate_name text not null,
    pos_level text not null check (pos_level in ('Pro A','Pro B','Pro C')),
    applied_position text not null,
    project_name text,
    tor_name text,
    client_name text,
    age integer check (age is null or age between 15 and 100),
    candidate_number text,
    key_classification text not null default 'Non-Key' check (key_classification in ('Key','Non-Key')),
    key_scope text check (key_scope is null or key_scope in ('International','Local')),
    decision text not null default 'FAIL' check (decision in ('PASS','FAIL')),
    email text,
    mobile text,
    sex text,
    evaluation_date date not null,
    total_score numeric(6,2) not null,
    overall_percentage numeric(6,2) not null,
    result text not null check (result in ('QUALIFIED','NOT QUALIFIED')),
    details_json jsonb not null,
    source_filename text,
    storage_path text,
    created_at timestamptz not null default now()
);

create index if not exists cv_evaluations_created_at_idx on public.cv_evaluations (created_at desc);
alter table public.cv_evaluations enable row level security;

-- The Streamlit server uses the Supabase secret key. It bypasses RLS and must
-- only be stored in server-side Streamlit secrets. Do not add public anon
-- policies for this private candidate information.
