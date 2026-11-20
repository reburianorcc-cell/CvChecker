-- Run once if the cv_evaluations table already exists.
alter table public.cv_evaluations
add column if not exists project_name text,
add column if not exists tor_name text,
add column if not exists client_name text,
add column if not exists age integer,
add column if not exists candidate_number text,
add column if not exists key_classification text default 'Non-Key',
add column if not exists key_scope text,
add column if not exists decision text default 'FAIL';

update public.cv_evaluations
set key_classification=coalesce(key_classification,'Non-Key'),
    decision=coalesce(decision,case when total_score>=50 then 'PASS' else 'FAIL' end);

alter table public.cv_evaluations
alter column key_classification set not null,
alter column decision set not null;

alter table public.cv_evaluations drop constraint if exists cv_evaluations_age_check;
alter table public.cv_evaluations add constraint cv_evaluations_age_check check (age is null or age between 15 and 100);
alter table public.cv_evaluations drop constraint if exists cv_evaluations_key_classification_check;
alter table public.cv_evaluations add constraint cv_evaluations_key_classification_check check (key_classification in ('Key','Non-Key'));
alter table public.cv_evaluations drop constraint if exists cv_evaluations_key_scope_check;
alter table public.cv_evaluations add constraint cv_evaluations_key_scope_check check (key_scope is null or key_scope in ('International','Local'));
alter table public.cv_evaluations drop constraint if exists cv_evaluations_decision_check;
alter table public.cv_evaluations add constraint cv_evaluations_decision_check check (decision in ('PASS','FAIL'));
