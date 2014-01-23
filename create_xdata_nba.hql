CREATE DATABASE IF NOT EXISTS xdata_nba;

USE xdata_nba;

CREATE TABLE IF NOT EXISTS game_players (
  game_id       STRING,
  player_id     INT,
  player_name   STRING,
  team_id       INT,
  team_city     STRING
);

CREATE TABLE IF NOT EXISTS game_commentary (
  game_id       STRING,
  preview       STRING,
  recap         STRING,
  notebook      STRING
);

CREATE TABLE IF NOT EXISTS game_comments (
  game_id       STRING,
  commenter     STRING,
  comments      STRING
);
CREATE TABLE IF NOT EXISTS game_stats (
  game_id               STRING,
  game_date             TIMESTAMP,
  game_status           STRING,
  game_season           SMALLINT,
  game_sequence         SMALLINT,
  game_attendance       SMALLINT,
  team_home_id          INT,
  team_visit_id         INT
);

CREATE TABLE IF NOT EXISTS game_player_stats (
  player_id             INT,
  team_id               INT,
  player_name			STRING,
  start_position        STRING,
  minutes_played        STRING,
  FGM                   TINYINT,
  FGA                   TINYINT,
  FG_PCT                FLOAT,
  FG3M                  TINYINT,
  FG3A                  TINYINT,
  FG3_PCT               FLOAT,
  FTM                   TINYINT,
  FTA                   TINYINT,
  FT_PCT                FLOAT,
  OREB                  TINYINT,
  DREB                  TINYINT,
  REB                   TINYINT,
  AST                   TINYINT,
  STL                   TINYINT,
  BLK                   TINYINT,
  TURNOVERS             TINYINT,
  PF                    TINYINT,
  PTS                   TINYINT,
  PLUS_MINUS            TINYINT
);


CREATE TABLE IF NOT EXISTS game_play_by_play (
  game_id               STRING,
  game_period           TINYINT,
  time_stamp            TIMESTAMP,
  game_clock            STRING,
  event_home_team       STRING,
  event_visit_team      STRING,
  event_neutral         STRING,
  score                 SMALLINT,
  score_margin          TINYINT
);

CREATE TABLE IF NOT EXISTS team (
  team_id       INT,
  team_city     STRING,
  team_name     STRING
);