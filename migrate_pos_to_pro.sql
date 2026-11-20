-- Run this once in Supabase SQL Editor if cv_evaluations already exists.
alter table public.cv_evaluations
drop constraint if exists cv_evaluations_pos_level_check;

update public.cv_evaluations
set pos_level = case pos_level
    when 'POS A' then 'Pro A'
    when 'POS B' then 'Pro B'
    when 'POS C' then 'Pro C'
    else pos_level
end;

alter table public.cv_evaluations
add constraint cv_evaluations_pos_level_check
check (pos_level in ('Pro A','Pro B','Pro C'));
