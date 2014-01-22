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
playByPlayURLTemplate = Template('http://stats.nba.com/stats/playbyplay?GameID=00$gameID&StartPeriod=0&EndPeriod=0&playbyplay=undefined')
espnSearch=Template('http://espn.go.com/nba/schedule?date=$gameDate|.*$winningTeam.*$winningScore.*$losingTeam.*$losingScore|$currentGameId')
yahooGame=Template('http://sports.yahoo.com/nba/scoreboard/?date=$gameDate|/nba/$awayTeamCity-$awayTeamName-$homeTeamCity-$homeTeamName.*|$currentGameId')
playerJSON=Template('[$playerID, "$playerName", $teamID, "$teamCity"]')
currentGameId = 21200001
outputDirPrefix = "../../../output/"
gameIdFile = "%sGame.ID" % outputDirPrefix
opener = urllib2.build_opener()
opener.addheaders = [('User-agent','Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
startTime = datetime.now()
noDataMsg = 'No Data Available'
gamesProcessed = 0
exceptionsThrown = 0

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
            logging.exception("Unable to read Game.ID file. Going ahead with default gameId: %d" % currentGameId)
            print 'Unable to read Game.ID file. Going ahead with default gameId: %d' % currentGameId
    idFile.close()
while True:
    try:
        """ Get the structured text """
        currentURL = gameDetailURLTemplate.substitute(gameID=currentGameId)
        logging.debug('Current URL:%s' % currentURL)
        url = opener.open(currentURL)
        content = json.load(url, encoding='utf-8')
        """ Pull Out Important Information """
        status = content['resultSets'][0]['rowSet'][0][4]
        if status != 'Final' and status != 'PPD' and status != 'CNCL':
            with open(gameIdFile, "w+") as idFile:
                idFile.write(str(currentGameId))
            idFile.close()
            break;
        """ Get Game Data """
        gameId = content['parameters']['GameID']
        gameDate = content['resultSets'][0]['rowSet'][0][0]
        gameCode = content['resultSets'][0]['rowSet'][0][5]
        """ Get Team Data """
        homeTeamId = content['resultSets'][0]['rowSet'][0][6]
        if content['resultSets'][1]['rowSet'][0][3] == homeTeamId:
            homeTeamCity = content['resultSets'][1]['rowSet'][0][5]
            homeTeamScore = content['resultSets'][1]['rowSet'][0][21]
            awayTeamCity = content['resultSets'][1]['rowSet'][1][5]
            awayTeamScore = content['resultSets'][1]['rowSet'][1][21]
        else:
            homeTeamCity = content['resultSets'][1]['rowSet'][1][5]
            homeTeamScore = content['resultSets'][1]['rowSet'][1][21]
            awayTeamCity = content['resultSets'][1]['rowSet'][0][5]
            awayTeamScore = content['resultSets'][1]['rowSet'][0][21]
        if content['resultSets'][5]['rowSet'][0][1] == homeTeamId:
            homeTeamName= content['resultSets'][5]['rowSet'][0][2]
            awayTeamName= content['resultSets'][5]['rowSet'][1][2]
        else:
            homeTeamName= content['resultSets'][5]['rowSet'][1][2]
            awayTeamName= content['resultSets'][5]['rowSet'][0][2]
        """ Get Player Data """
        playerData = '{"resultSets":[{"headers": ["PLAYER_ID", "PLAYER_NAME", "TEAM_ID", "TEAM_CITY"], "rowset":['
        for player in content['resultSets'][4]['rowSet']:
            playerData += playerJSON.substitute(playerID=player[4], playerName=player[5], teamID=player[1], teamCity=player[3]) + ","
        """ strip last comma away """
        playerData = playerData[:-1]
        playerData += "]}]}"
        """ Generate EPSN URLs """
        espnGameDate = datetime.strptime(gameDate, "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d")
        with open("%sespn_search_urls.txt" % outputDirPrefix, "a+") as espnUrls:
            if (int(awayTeamScore) > int(homeTeamScore)):
                winningTeamCity = awayTeamCity
                winningTeamScore = awayTeamScore
                losingTeamCity = homeTeamCity
                losingTeamScore = homeTeamScore
                """ ESPN uses team name to distinguish between the two LA teams """
                if winningTeamCity == 'Los Angeles':
                    winningTeamCity = 'LA ' + awayTeamName
                if losingTeamCity == 'Los Angeles':
                    losingTeamCity = 'LA ' + homeTeamName
            else :
                winningTeamCity = homeTeamCity
                winningTeamScore = homeTeamScore
                losingTeamCity = awayTeamCity
                losingTeamScore = awayTeamScore
                """ ESPN uses team name to distinguish between the two LA teams """
                if winningTeamCity == 'Los Angeles':
                    winningTeamCity = 'LA ' + homeTeamName
                if losingTeamCity == 'Los Angeles':
                    losingTeamCity = 'LA ' + awayTeamName
            espnUrls.write(espnSearch.substitute(gameDate=urllib.quote_plus(espnGameDate), winningTeam=winningTeamCity, winningScore=winningTeamScore, losingTeam=losingTeamCity, losingScore=losingTeamScore, currentGameId=currentGameId) + "\n")
        espnUrls.close()
        
        """ Generate Yahoo URLs """
        yahooGameDate = datetime.strptime(gameDate, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
        with open("%syahoo_search_urls.txt" % outputDirPrefix, "a+") as yahooUrls:
            yahooUrls.write(yahooGame.substitute(gameDate=urllib.quote_plus(yahooGameDate), awayTeamCity=awayTeamCity.replace(' ','-').lower(), awayTeamName=awayTeamName.replace(' ','-').lower(), homeTeamCity=homeTeamCity.replace(' ','-').lower(), homeTeamName=homeTeamName.replace(' ','-').lower(), currentGameId=currentGameId) + "\n")
        yahooUrls.close()
        
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
        
        playerDataFileName = "%s00%d_gamePlayers.json" %(outputDirPrefix, currentGameId)
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
        
        """ Write Play-by-Play File """
        playByPlayFileName = "%s00%d_playbyplay.json" %(outputDirPrefix, currentGameId)
        currentURL = playByPlayURLTemplate.substitute(gameID=currentGameId)
        logging.debug('Play-by-play URL:%s' % currentURL)
        url = opener.open(currentURL)
        playByPlay = json.load(url, encoding='utf-8')
        with open(playByPlayFileName, 'w+') as outfile:
            json.dump(playByPlay, outfile)
        outfile.close
        
        """ Wrap Up """
        currentGameId += 1
        gamesProcessed += 1
        print("."),
    except urllib2.HTTPError:
        logging.exception("Error in processing game: %s" % url)
        print("!")
        exceptionsThrown += 1
        with open(gameIdFile, "w+") as idFile:
                idFile.write(str(currentGameId))
        idFile.close()
        break;
    except Exception as e:
        logging.exception("Error in processing game: %s" % url)
        print("!"),
        currentGameId += 1
        exceptionsThrown += 1
        """ Continue with remaining Games """
        continue
""" END WHILE LOOP """
opener.close()
endTime = datetime.now()
delta = endTime - startTime

print '\nStopping Retrieval\n-- Processing Time: %d seconds\n-- Games Processed: %s\n-- Exceptions Caught: %s' %(delta.seconds + delta.microseconds/1E6, gamesProcessed, exceptionsThrown)
logging.info('Stopping Retrieval\n-- Processing Time: %d seconds\n-- Games Processed: %s\n-- Exceptions Caught: %s' %(delta.seconds + delta.microseconds/1E6, gamesProcessed, exceptionsThrown))