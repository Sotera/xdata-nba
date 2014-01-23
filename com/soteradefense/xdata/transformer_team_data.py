import logging
import json
import glob
import re
from string import Template

""" NOTES
Using default field delimiter and record delimiter for Hive, \001 and \n respectively

Structure of table targeted by this script:

team (
  team_id       INT,
  team_city     STRING,
  team_name     STRING
);

"""

""" Variables """
logging.basicConfig(filename='../../../transformer_team_data.log', level=logging.DEBUG)
tableTemplate=Template('$teamID\x01$teamCity\x01$teamName\n')
teamPattern = re.compile("^(.*)\s(\w*)$")
inputDir = "../../../output/"
outputDirPrefix = "../../../"
filesProcessed = 0
exceptionsThrown = 0

print 'Starting Transform'
logging.info('Staring Transform')

gamePlayerFileName = "%steam_data.hive" % outputDirPrefix
with open(gamePlayerFileName, 'a+') as outfile:
    for f in glob.glob(inputDir + "teamdata.json"):
        try:
            d = open(f, 'r')
            content = json.load(d, encoding='utf-8')
            for record in content['resultSets'][0]['rowSet']:
                try:
                    team = teamPattern.match(record[1])
                    teamCity = team.group(1)
                    teamName = team.group(2)
                    outfile.write(tableTemplate.substitute(teamID=record[0], teamCity=teamCity, teamName=teamName))
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