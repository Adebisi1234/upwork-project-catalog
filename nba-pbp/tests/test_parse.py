import pytest
from nba_pbp.parse import clock_to_seconds, game_from_plays, parse_plays
from tests.fixture import ROWS


def test_clock():
    assert clock_to_seconds("PT11M43.00S") == 703.0
    assert clock_to_seconds("PT00M00.50S") == 0.5
    with pytest.raises(ValueError):
        clock_to_seconds("11:43")


def test_parse_plays():
    teams, players, plays = parse_plays("0022300001", ROWS)
    assert teams == {1610612747: "LAL", 1610612744: "GSW"}
    assert players == {2544: "James", 201939: "Curry"}
    assert plays[0]["team_id"] is None and plays[0]["shot_distance"] is None
    assert plays[1]["shot_value"] == 2 and plays[1]["is_field_goal"]
    assert game_from_plays("0022300001", plays)["home_score"] == 2
