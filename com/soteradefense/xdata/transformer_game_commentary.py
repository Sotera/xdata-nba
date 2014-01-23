import logging
import glob
import re
from string import Template

""" NOTES
Using default field delimiter and record delimiter for Hive, \001 and \n respectively

Structure of table targeted by this script:

game_commentary (
  game_id       STRING,
  preview       STRING,
  recap         STRING,
  notebook      STRING
);

"""

""" Variables """
logging.basicConfig(filename='../../../transformer_game_commentary.log', level=logging.DEBUG)
tableTemplate=Template('$gameID\x01$preview\x01$recap\x01$notebook\n')
filenamePattern = re.compile(".*(\d{10})_.*$")
inputDir = "../../../output/"
outputDirPrefix = "../../../"
filesProcessed = 0
exceptionsThrown = 0

print 'Starting Transform'
logging.info('Staring Transform')

gameCommentaryFileName = "%sgame_commentary.hive" % outputDirPrefix
with open(gameCommentaryFileName, 'a+') as outfile:
    for f in glob.glob(inputDir + "*_recap.txt"):
        try:
            gameID = filenamePattern.match(f).group(1)
            try:
                recap = open(f).read().replace('\n', '')
            except Exception as e:
                logging.exception("Error parsing recap file: %s" %f)
                pass
            try:
                previewFileName = "%s%s_preview.txt" %(inputDir, gameID)
                preview = open(previewFileName).read().replace('\n', '')
            except Exception as e:
                logging.exception("Error parsing preview file: %s_preview.txt" % gameID)
                pass
            try:
                notebookFileName = "%s%s_notebook.txt" %(inputDir, gameID)
                notebook = open(notebookFileName).read().replace('\n', '')
            except Exception as e:
                logging.exception("Error parsing notebook file: %s_notebook.txt" % gameID)
                pass
            try:
                outfile.write(tableTemplate.substitute(gameID=gameID, preview=preview, recap=recap, notebook=notebook))
            except Exception as e:
                logging.exception("Error writing to output file")
                continue            
            filesProcessed += 3
        except Exception as e:
            logging.exception("Error in transforming file: %s" % f)
            exceptionsThrown += 1
            continue
outfile.close()

print 'Stopping Transform\n-- Files Processed: %s\n-- Exceptions Caught: %s' %(filesProcessed, exceptionsThrown)
logging.info('Stopping Transform\n-- Files Processed: %s\n-- Exceptions Caught: %s' %(filesProcessed, exceptionsThrown))