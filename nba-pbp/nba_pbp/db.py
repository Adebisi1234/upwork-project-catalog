from pathlib import Path
import psycopg

SCHEMA = Path(__file__).resolve().parent.parent / "sql" / "schema.sql"


def init(conn):
    conn.execute(SCHEMA.read_text())


def save_game(conn, game, teams, players, plays):
    """Upsert one game in a single transaction. Re-running replaces its plays."""
    with conn.transaction():
        with conn.cursor() as cur:
            cur.executemany(
                "insert into teams (team_id, tricode) values (%s, %s) "
                "on conflict (team_id) do update set tricode = excluded.tricode",
                list(teams.items()))
            cur.executemany(
                "insert into players (player_id, name) values (%s, %s) "
                "on conflict (player_id) do update set name = excluded.name",
                list(players.items()))
            cur.execute(
                "insert into games (game_id, game_date, home_team_id, away_team_id, home_score, away_score) "
                "values (%(game_id)s, %(game_date)s, %(home_team_id)s, %(away_team_id)s, %(home_score)s, %(away_score)s) "
                "on conflict (game_id) do update set "
                "game_date = coalesce(excluded.game_date, games.game_date), "
                "home_team_id = coalesce(excluded.home_team_id, games.home_team_id), "
                "away_team_id = coalesce(excluded.away_team_id, games.away_team_id), "
                "home_score = excluded.home_score, away_score = excluded.away_score", game)
            cur.execute("delete from plays where game_id = %s", (game["game_id"],))
            cols = list(plays[0].keys())
            with cur.copy(f"copy plays ({', '.join(cols)}) from stdin") as cp:
                for p in plays:
                    cp.write_row([p[c] for c in cols])
