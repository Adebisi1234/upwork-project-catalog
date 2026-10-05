"""Turn raw PlayByPlayV3 rows (list of dicts) into clean rows. No I/O here."""
import re
from datetime import date

_CLOCK = re.compile(r"PT(\d+)M([\d.]+)S")


def clock_to_seconds(clock: str) -> float:
    """'PT11M43.00S' -> 703.0"""
    m = _CLOCK.fullmatch(clock or "")
    if not m:
        raise ValueError(f"unexpected clock format: {clock!r}")
    return int(m.group(1)) * 60 + float(m.group(2))


def _id(v):
    """NBA uses 0 for 'nobody'. Store that as NULL."""
    return int(v) if v not in (None, "", 0, "0") else None


def _num(v):
    return None if v in (None, "") else v


def _score(v):
    return int(v) if v not in (None, "") else None


def parse_plays(game_id: str, rows: list[dict]):
    """Return (teams, players, plays) as lists of dicts."""
    teams, players, plays = {}, {}, []
    for r in rows:
        team_id, player_id = _id(r.get("teamId")), _id(r.get("personId"))
        if team_id:
            teams[team_id] = r["teamTricode"]
        if player_id:
            players[player_id] = r["playerName"]
        plays.append({
            "game_id": game_id,
            "action_number": int(r["actionNumber"]),
            "period": int(r["period"]),
            "clock_seconds": clock_to_seconds(r["clock"]),
            "team_id": team_id,
            "player_id": player_id,
            "action_type": r.get("actionType") or None,
            "sub_type": r.get("subType") or None,
            "description": r.get("description") or None,
            "is_field_goal": bool(r.get("isFieldGoal")),
            "shot_result": r.get("shotResult") or None,
            "shot_value": _score(r.get("shotValue")) or None,
            "shot_distance": _num(r.get("shotDistance")) if r.get("isFieldGoal") else None,
            "x": _num(r.get("xLegacy")) if r.get("isFieldGoal") else None,
            "y": _num(r.get("yLegacy")) if r.get("isFieldGoal") else None,
            "home_score": _score(r.get("scoreHome")),
            "away_score": _score(r.get("scoreAway")),
        })
    return teams, players, plays


def game_from_plays(game_id: str, plays: list[dict], game_date: date | None = None,
                    home_team_id=None, away_team_id=None):
    """Final score = last row that carries a score."""
    scored = [p for p in plays if p["home_score"] is not None]
    last = scored[-1] if scored else {}
    return {"game_id": game_id, "game_date": game_date,
            "home_team_id": home_team_id, "away_team_id": away_team_id,
            "home_score": last.get("home_score"), "away_score": last.get("away_score")}
