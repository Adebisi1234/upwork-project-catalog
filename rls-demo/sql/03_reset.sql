-- Put the demo back to the "broken" state to re-record.
drop policy if exists "Users read own bookings" on bookings;
drop policy if exists "Users create own bookings" on bookings;
alter table bookings disable row level security;
