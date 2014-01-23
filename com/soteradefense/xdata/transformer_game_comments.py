import logging
import glob
import re
from string import Template

""" NOTES
Using default field delimiter and record delimiter for Hive, \001 and \n respectively

Structure of table targeted by this script:

game_comments (
  game_id       STRING,
  commenter     STRING,
  comments      STRING
);

"""

""" Variables """
logging.basicConfig(filename='../../../transformer_game_comments.log', level=logging.DEBUG)
tableTemplate=Template('$gameID\x01$commenter\x01$comment\n')
filenamePattern = re.compile(".*(\d{10})_.*$")
commenterPattern = re.compile("(.*?)::(.*)")
inputDir = "../../../output/"
outputDirPrefix = "../../../"
filesProcessed = 0
exceptionsThrown = 0

print 'Starting Transform'
logging.info('Staring Transform')

gamePlayerFileName = "%sgame_comments.hive" % outputDirPrefix
with open(gamePlayerFileName, 'a+') as outfile:
    for f in glob.glob(inputDir + "*_comments.txt"):
        try:
            d = open(f, 'r')
            gameID = filenamePattern.match(f).group(1)
            for line in d:
                try:
                    match = commenterPattern.match(line)
                    commenter = match.group(1)
                    comment = match.group(2)
                    outfile.write(tableTemplate.substitute(gameID=gameID, commenter=commenter, comment=comment))
                except Exception as e:
                    logging.exception("Error parsing line: %s" % line)
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