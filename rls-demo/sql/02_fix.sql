-- The fix from audit finding 1.
alter table bookings enable row level security;

create policy "Users read own bookings" on bookings
  for select using ((select auth.uid()) = user_id);

create policy "Users create own bookings" on bookings
  for insert with check ((select auth.uid()) = user_id);
