import logging
import json
import glob
import re
from string import Template

""" NOTES
Using default field delimiter and record delimiter for Hive, \001 and \n respectively

Structure of table targeted by this script:

game_play_by_play (
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

"""

""" Variables """
logging.basicConfig(filename='../../../transformer_game_play_by_play.log', level=logging.DEBUG)
tableTemplate=Template('$gameID\x01$gamePeriod\x01$timeStamp\x01$gameClock\x01$eventHomeTeam\x01$eventVisitTeam\x01$eventNeutral\x01$score\x01$scoreMargin\n')
filenamePattern = re.compile(".*(\d{10})_.*$")
inputDir = "../../../output/"
outputDirPrefix = "../../../"
filesProcessed = 0
exceptionsThrown = 0

print 'Starting Transform'
logging.info('Staring Transform')

gamePlayerFileName = "%sgame_play_by_play.hive" % outputDirPrefix
with open(gamePlayerFileName, 'a+') as outfile:
    for f in glob.glob(inputDir + "*_playbyplay.json"):
        try:
            d = open(f, 'r')
            gameID = filenamePattern.match(f).group(1)
            content = json.load(d, encoding='utf-8')
            for record in content['resultSets'][0]['rowSet']:
                try:
                    outfile.write(tableTemplate.substitute(gameID=gameID, gamePeriod=record[4], timeStamp=record[5], gameClock=record[6],eventHomeTeam=record[7],eventVisitTeam=record[9],eventNeutral=record[8],score=record[10],scoreMargin=record[11]))
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