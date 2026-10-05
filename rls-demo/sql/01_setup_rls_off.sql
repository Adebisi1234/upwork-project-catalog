-- DEMO ONLY. Run in a THROWAWAY Supabase project. Never a client's project.
-- Before running: Auth > Users > add two users (confirm email):
--   alice@example.test  and  bob@example.test  (any passwords)

create table if not exists bookings (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id),
  customer    text not null,
  phone       text not null,
  starts_at   timestamptz not null
);

-- The mistake: RLS off (the default for tables made via SQL, and what the
-- audit finds in AI-built apps). Supabase shows the "RLS disabled" badge.
alter table bookings disable row level security;
grant select, insert on bookings to anon, authenticated;

-- Fake data only.
insert into bookings (user_id, customer, phone, starts_at)
select id, 'Alice Demo', '+1 555 0100', now() + interval '1 day'
from auth.users where email = 'alice@example.test';

insert into bookings (user_id, customer, phone, starts_at)
select id, 'Bob Demo', '+1 555 0199', now() + interval '2 days'
from auth.users where email = 'bob@example.test';
