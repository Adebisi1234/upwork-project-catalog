-- Clean NBA play-by-play schema. Idempotent: safe to run repeatedly.

create table if not exists teams (
  team_id   bigint primary key,
  tricode   text not null
);

create table if not exists players (
  player_id bigint primary key,
  name      text not null
);

create table if not exists games (
  game_id    text primary key,          -- e.g. 0022300001
  game_date  date,
  home_team_id bigint references teams(team_id),
  away_team_id bigint references teams(team_id),
  home_score int,
  away_score int
);

create table if not exists plays (
  game_id        text   not null references games(game_id) on delete cascade,
  action_number  int    not null,
  period         smallint not null,
  clock_seconds  numeric(5,1) not null,   -- seconds remaining in the period
  team_id        bigint references teams(team_id),
  player_id      bigint references players(player_id),
  action_type    text,
  sub_type       text,
  description    text,
  is_field_goal  boolean not null default false,
  shot_result    text,                    -- 'Made' | 'Missed' | null
  shot_value     smallint,                -- 2 or 3 for shots
  shot_distance  numeric(5,1),
  x              numeric(6,1),
  y              numeric(6,1),
  home_score     int,
  away_score     int,
  primary key (game_id, action_number)
);

create index if not exists plays_player_idx on plays (player_id);
create index if not exists plays_team_idx   on plays (team_id);

-- Shots only, with court coordinates: ready for shot charts.
create or replace view shots as
select p.game_id, p.period, p.clock_seconds, p.team_id, p.player_id,
       pl.name as player_name, p.shot_value, p.shot_distance, p.x, p.y,
       (p.shot_result = 'Made') as made
from plays p
left join players pl using (player_id)
where p.is_field_goal;

-- Points per player per game from made shots (free throws excluded; see README).
create or replace view player_game_fg_points as
select game_id, player_id, sum(shot_value) as fg_points
from shots where made and player_id is not null
group by game_id, player_id;
