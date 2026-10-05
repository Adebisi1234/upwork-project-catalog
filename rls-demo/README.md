# RLS leak demo (audit finding 1)

Tiny demo for the "Supabase security audit" Upwork catalog video. **Use a throwaway
Supabase project with fake data. Never a client's.**

## Setup
1. Create a new throwaway Supabase project.
2. Auth > Users: add `alice@example.test` and `bob@example.test`.
3. SQL editor: run `sql/01_setup_rls_off.sql`.
4. Serve this folder: `python3 -m http.server 8000`, open http://localhost:8000.
   Paste the project URL and anon key (Settings > API), Alice's password.

## Video script
1. **Hook** (on the sample report): "If you built your app with Lovable or Bolt,
   there's a good chance one of these issues is in it."
2. **Finding 1**: scroll to it, then show the `bookings` table in Supabase with the
   RLS-disabled badge. Click the demo button: Alice's login returns Bob's row too.
   "This means any logged-in user can read every other user's data."
3. **Fix**: paste `sql/02_fix.sql`, click the button again: only Alice's row.
   "Here's the fix. In the audit, I check every table, your keys, your webhooks and
   your slowest queries."
4. **Close**: "You get a plain-English report in two days, and I can fix the issues
   too. Order the audit or message me with what's breaking."

Re-record: run `sql/03_reset.sql`.
