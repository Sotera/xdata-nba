import logging
import json
import glob
import re
from string import Template

""" NOTES
Using default field delimiter and record delimiter for Hive, \001 and \n respectively

Structure of table targeted by this script:

game_players (
  game_id       STRING,
  player_id     INT,
  player_name   STRING,
  team_id       INT,
  team_city     STRING
);

"""

""" Variables """
logging.basicConfig(filename='../../../transformer_game_players.log', level=logging.DEBUG)
tableTemplate=Template('$gameID\x01$playerID\x01$playerName\x01$teamID\x01$teamCity\n')
filenamePattern = re.compile(".*(\d{10})_.*$")
inputDir = "../../../output/"
outputDirPrefix = "../../../"
filesProcessed = 0
exceptionsThrown = 0

print 'Starting Transform'
logging.info('Staring Transform')

gamePlayerFileName = "%sgame_players.hive" % outputDirPrefix
with open(gamePlayerFileName, 'a+') as outfile:
    for f in glob.glob(inputDir + "*_gamePlayers.json"):
        try:
            d = open(f, 'r')
            gameID = filenamePattern.match(f).group(1)
            content = json.load(d, encoding='utf-8')
            for record in content['resultSets'][0]['rowset']:
                try:
                    outfile.write(tableTemplate.substitute(gameID=gameID, playerID=record[0], playerName=record[1], teamID=record[2], teamCity=record[3]))
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