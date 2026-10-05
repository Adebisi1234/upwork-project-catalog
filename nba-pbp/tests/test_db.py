"""Needs a Postgres: set DATABASE_URL, otherwise skipped."""
import os, pytest, psycopg
from nba_pbp import db
from nba_pbp.parse import game_from_plays, parse_plays
from tests.fixture import ROWS

pytestmark = pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="no DATABASE_URL")


def test_roundtrip_is_idempotent():
    with psycopg.connect(os.environ["DATABASE_URL"], autocommit=True) as conn:
        db.init(conn)
        t, p, plays = parse_plays("TEST0001", ROWS)
        g = game_from_plays("TEST0001", plays)
        for _ in range(2):                      # run twice: no duplicates
            db.save_game(conn, g, t, p, plays)
        n = conn.execute("select count(*) from plays where game_id='TEST0001'").fetchone()[0]
        assert n == 3
        pts = conn.execute("select fg_points from player_game_fg_points "
                           "where game_id='TEST0001'").fetchall()
        assert pts == [(2,)]                    # Curry's miss doesn't count
        conn.execute("delete from games where game_id='TEST0001'")
