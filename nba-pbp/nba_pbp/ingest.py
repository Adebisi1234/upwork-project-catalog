"""CLI: python -m nba_pbp.ingest --season 2023-24 --limit 5
       python -m nba_pbp.ingest --game-id 0022300001
Needs DATABASE_URL, e.g. postgresql://nba:nba@localhost:5432/nba"""
import argparse, os, sys, time
from datetime import date

import psycopg
from nba_api.stats.endpoints import leaguegamefinder, playbyplayv3

from . import db
from .parse import game_from_plays, parse_plays


def list_games(season: str, limit: int | None):
    """One entry per game: id, date, home/away team ids (from the matchup text)."""
    df = leaguegamefinder.LeagueGameFinder(
        season_nullable=season, season_type_nullable="Regular Season",
        league_id_nullable="00").get_data_frames()[0]
    games = {}
    for r in df.itertuples():
        g = games.setdefault(r.GAME_ID, {"game_id": r.GAME_ID,
                                         "game_date": date.fromisoformat(r.GAME_DATE)})
        g["home_team_id" if "vs." in r.MATCHUP else "away_team_id"] = int(r.TEAM_ID)
    out = sorted(games.values(), key=lambda g: g["game_id"])
    return out[:limit] if limit else out


def ingest_game(conn, meta: dict):
    rows = playbyplayv3.PlayByPlayV3(game_id=meta["game_id"]).get_dict()[
        "game"]["actions"]
    teams, players, plays = parse_plays(meta["game_id"], rows)
    if not plays:
        print(f"{meta['game_id']}: no plays, skipped")
        return
    game = game_from_plays(meta["game_id"], plays, meta.get("game_date"),
                           meta.get("home_team_id"), meta.get("away_team_id"))
    for t in ("home_team_id", "away_team_id"):   # games.* FK needs the team row
        if game[t] and game[t] not in teams:
            teams[game[t]] = "UNK"
    db.save_game(conn, game, teams, players, plays)
    print(f"{meta['game_id']}: {len(plays)} plays")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", help="e.g. 2023-24")
    ap.add_argument("--game-id")
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    if not (a.season or a.game_id):
        ap.error("pass --season or --game-id")
    url = os.environ.get("DATABASE_URL")
    if not url:
        sys.exit("Set DATABASE_URL")
    metas = [{"game_id": a.game_id}] if a.game_id else list_games(a.season, a.limit)
    with psycopg.connect(url, autocommit=True) as conn:
        db.init(conn)
        for m in metas:
            try:
                ingest_game(conn, m)
            except Exception as e:           # keep going; stats.nba.com is flaky
                print(f"{m['game_id']}: FAILED {e}", file=sys.stderr)
            time.sleep(0.7)                  # be polite to the API


if __name__ == "__main__":
    main()
