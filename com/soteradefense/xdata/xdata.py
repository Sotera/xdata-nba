import json
import logging
import os
import urllib
import urllib2
from datetime import datetime
from string import Template
from bs4 import BeautifulSoup

""" NOTES 
NBA breaks their GameIDs down in the following manner {AAA}{BB}{CCCCC}
where
    A is either 001:preseason, 002:season, 003:specialty games (eg. all-star, exhibitions)
    B is the seasons start year
    C is the game number

0011200001 is the start of preseason games in the 2012/2013 season
0021200001 is the start of season games in the 2012/2013 season
0011300001 is the start of preseason games in the 2013/2014 season
0021300001 is the start of season games in the 2013/2014 season

All data is valid back to the 2010 season
in the 2009 season there appears to be no "notebook" content
in the 2008 season there appears to be no "preview, recap, or notebook" content
"""

""" Variables """
logging.basicConfig(filename='../../../xdata.log', level=logging.DEBUG)
gameInfoURLTemplate = Template('http://www.nba.com/games/$gameCode/gameinfo.html')
gameDetailURLTemplate = Template('http://stats.nba.com/stats/boxscore?GameID=00$gameID&RangeType=0&StartPeriod=0&EndPeriod=0&StartRange=0&EndRange=0')
espn_search=Template('http://espn.go.com/nba/schedule?date=$gameDate|.*$winningTeam.*$winningScore.*$losingTeam.*$losingScore|$currentGameId')
currentGameId = 21300550
outputDirPrefix = "../../../output/"
gameIdFile = "%sGame.ID" % outputDirPrefix
opener = urllib2.build_opener()
startTime = datetime.now()
noDataMsg = 'No Data Available'

print 'Starting Retrieval'
logging.info('Staring Retrieval')

logging.info('Checking if Game.ID file exists')
if os.path.exists(gameIdFile):
    with open(gameIdFile, "r") as idFile:
        try:
            currentGameId = int(idFile.read())
            logging.debug("Game.ID file found. Starting process with gameId: %d" % currentGameId)
            print 'Game.ID file found. Starting process with gameId: %d' % currentGameId
        except Exception as e:
            logging.error("Unable to read Game.ID file. Going ahead with default gameId: %d\n%s" % (currentGameId, e))
            print 'Unable to read Game.ID file. Going ahead with default gameId: %d' % currentGameId
    idFile.close()
while True:
    """ Get the structured text """
    currentURL = gameDetailURLTemplate.substitute(gameID=currentGameId)
    logging.debug('Current URL:%s' % currentURL)
    nbaStatStructured = urllib2.Request(currentURL, None, {} )
    url = opener.open(nbaStatStructured)
    content = json.load(url, encoding='utf-8')
    
    """ Pull Out Important Information """
    status = content['resultSets'][0]['rowSet'][0][4]
    if status != 'Final' and status != 'PPD':
        with open(gameIdFile, "w+") as idFile:
            idFile.write(str(currentGameId))
        idFile.close()
        break;
    gameId = content['parameters']['GameID']
    gameDate = content['resultSets'][0]['rowSet'][0][0]
    gameCode = content['resultSets'][0]['rowSet'][0][5]
    homeTeamCity = content['resultSets'][1]['rowSet'][1][5]
    homeTeamScore = content['resultSets'][1]['rowSet'][1][21]
    awayTeamCity = content['resultSets'][1]['rowSet'][0][5]
    awayTeamScore = content['resultSets'][1]['rowSet'][0][21]
    playerData = ''
    for player in content['resultSets'][4]['rowSet']:
        playerData += player[5] + ", " + player[3] + "\n"
    
    """ Generate EPSN URLs """
    gameDate = datetime.strptime(gameDate, "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d")
    with open("%sespn_search_urls.txt" % outputDirPrefix, "a+") as googleUrls:
        if (int(awayTeamScore) > int(homeTeamScore)):
            winningTeamCity = awayTeamCity
            winningTeamScore = awayTeamScore
            losingTeamCity = homeTeamCity
            losingTeamScore = homeTeamScore
        else :
            winningTeamCity = homeTeamCity
            winningTeamScore = homeTeamScore
            losingTeamCity = awayTeamCity
            losingTeamScore = awayTeamScore
        googleUrls.write(espn_search.substitute(gameDate=urllib.quote_plus(gameDate), winningTeam=winningTeamCity, winningScore=winningTeamScore, losingTeam=losingTeamCity, losingScore=losingTeamScore, currentGameId=currentGameId) + "\n")
    googleUrls.close()
    
    """ Generate Follow Up URL """
    gameInfoURL = gameInfoURLTemplate.substitute(gameCode=gameCode)
    logging.debug('Game Info URL:%s' % gameInfoURL)
    
    """ Get Unstructured Text """
    unstructured = opener.open(gameInfoURL)
    soup = BeautifulSoup(unstructured)
    
    preview = soup.find("div", {"id": "nbaGIPreview"})
    recap = soup.find("div", {"id": "nbaGIRecap2"})
    notebook = soup.find("div", {"id": "nbaGINotebook"})
    
    """ Write to output files """
    statFileName = "%s00%d_gamestats.json" %(outputDirPrefix, currentGameId)
    with open(statFileName, 'w+') as outfile:
        json.dump(content, outfile)
    outfile.close
    
    playerDataFileName = "%s00%d_playerName.txt" %(outputDirPrefix, currentGameId)
    with open(playerDataFileName, 'w+') as outfile:
        outfile.write(playerData)
    outfile.close
    
    previewFileName = "%s00%d_preview.txt" %(outputDirPrefix, currentGameId)
    previewFile = open(previewFileName, 'w+')
    if preview is not None:
        previewText = " ".join(preview.strings)
        previewFile.write(previewText)
    else:
        previewFile.write(noDataMsg)
    previewFile.close()
    
    recapFileName = "%s00%d_recap.txt" %(outputDirPrefix, currentGameId)
    recapFile = open(recapFileName, 'w+')
    if recap is not None:
        recapText = " ".join(recap.strings)
        recapFile.write(recapText)
    else:
        recapFile.write(noDataMsg)
    recapFile.close()
    
    notebookFileName = "%s00%d_notebook.txt" %(outputDirPrefix, currentGameId)
    notebookFile = open(notebookFileName, 'w+')
    if notebook is not None:
        notebookText = " ".join(notebook.strings)
        notebookFile.write(notebookText)
    else:
        notebookFile.write(noDataMsg)
    notebookFile.close()
    
    currentGameId += 1
""" END WHILE LOOP """
opener.close()
endTime = datetime.now()
delta = endTime - startTime

print 'Stopping Retrieval -- Processing Time: %d seconds' %(delta.seconds + delta.microseconds/1E6)
logging.info('Stopping Retrieval -- Processing Time: %d seconds' %(delta.seconds + delta.microseconds/1E6))