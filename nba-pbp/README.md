# nba-pbp

Pull NBA play-by-play into a clean Postgres schema. Small, idempotent, one command.

## Quick start
```bash
docker compose up -d
pip install -r requirements.txt
export DATABASE_URL=postgresql://nba:nba@localhost:5432/nba
python -m nba_pbp.ingest --season 2023-24 --limit 5     # or --game-id 0022300001
```
Re-running is safe: each game's plays are replaced in one transaction.

## Schema (`sql/schema.sql`)
| table | notes |
|---|---|
| `teams`, `players` | ids + tricode / name |
| `games` | date, home/away team, final score |
| `plays` | one row per event; PK `(game_id, action_number)`; clock stored as seconds remaining; "nobody" ids stored as NULL; shot fields only on field goals |
| `shots` (view) | field goals with coordinates and `made` flag |
| `player_game_fg_points` (view) | field-goal points per player per game |

Example: top scorers by field-goal points
```sql
select pl.name, sum(fg_points) from player_game_fg_points f
join players pl using (player_id) group by 1 order by 2 desc limit 10;
```

## Tests
```bash
pytest                       # parsing only
DATABASE_URL=... pytest      # also checks the DB round trip
```

## Notes
- Data comes from stats.nba.com via [`nba_api`](https://github.com/swar/nba_api) (`PlayByPlayV3`). Check NBA's terms before redistributing the data; this repo ships none.
- Free throws are plays but not field goals, so `fg_points` excludes them.
- stats.nba.com rate-limits and sometimes blocks cloud IPs; the loader sleeps between games and logs failures instead of stopping.
