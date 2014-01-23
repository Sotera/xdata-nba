import logging
import json
import glob
import re
from string import Template

""" NOTES
Using default field delimiter and record delimiter for Hive, \001 and \n respectively

Structure of table targeted by this script:

game_player_stats (
  player_id             INT,
  team_id               INT,
  player_name            STRING,
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

"""

""" Variables """
logging.basicConfig(filename='../../../transformer_game_player_stats.log', level=logging.DEBUG)
tableTemplate=Template('$gameID\x01$playerID\x01$teamID\x01$playerName\x01$startPosition\x01$minutesPlayed\x01$fgm\x01$fga\x01$fgPct\x01$fg3m\x01$fg3a\x01$fg3Pct\x01$ftm\x01$fta\x01$ftPct\x01$oReb\x01$dReb\x01$reb\x01$ast\x01$stl\x01$blk\x01$turnovers\x01$pf\x01$pts\x01$plusMinus\n')
filenamePattern = re.compile(".*(\d{10})_.*$")
inputDir = "../../../output/"
outputDirPrefix = "../../../"
filesProcessed = 0
exceptionsThrown = 0

print 'Starting Transform'
logging.info('Staring Transform')

gamePlayerFileName = "%sgame_player_stats.hive" % outputDirPrefix
with open(gamePlayerFileName, 'a+') as outfile:
    for f in glob.glob(inputDir + "*_gamestats.json"):
        try:
            d = open(f, 'r')
            gameID = filenamePattern.match(f).group(1)
            content = json.load(d, encoding='utf-8')
            for record in content['resultSets'][4]['rowSet']:
                try:
                    outfile.write(tableTemplate.substitute(gameID=gameID,teamID=record[1], playerID=record[4], playerName=record[5],startPosition=record[6],minutesPlayed=record[8],fgm=record[9],fga=record[10],fgPct=record[11],fg3m=record[12],fg3a=record[13],fg3Pct=record[14],ftm=record[15],fta=record[16],ftPct=record[17],oReb=record[18],dReb=record[19],reb=record[20],ast=record[21],stl=record[22],blk=record[23],turnovers=record[24],pf=record[25],pts=record[26],plusMinus=record[27]))
                except Exception as e:
                    logging.exception("Error in parsing json record: %s" % record)
                    continue
            d.close()
            filesProcessed += 1
        except Exception as e:
            logging.exception("Error in transforming file: %s" % f)
            exceptionsThrown += 1
            continue
outfile.close()

print 'Stopping Transform\n-- Files Processed: %s\n-- Exceptions Caught: %s' %(filesProcessed, exceptionsThrown)
logging.info('Stopping Transform\n-- Files Processed: %s\n-- Exceptions Caught: %s' %(filesProcessed, exceptionsThrown))