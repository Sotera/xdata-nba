import json
import logging
import urllib2


""" Variables """
logging.basicConfig(filename='../../../team_data.log', level=logging.DEBUG)
url='http://stats.nba.com/stats/leaguedashteamstats?Season=2013-14&AllStarSeason=2012-13&SeasonType=Regular+Season&LeagueID=00&MeasureType=Base&PerMode=PerGame&PlusMinus=N&PaceAdjust=N&Rank=N&Outcome=&Location=&Month=0&SeasonSegment=&DateFrom=&DateTo=&OpponentTeamID=0&VsConference=&VsDivision=&GameSegment=&Period=0&LastNGames=0&GameScope=&PlayerExperience=&PlayerPosition=&StarterBench=&pageNo=1&rowsPerPage=30&columnOrder=TEAM_NAME%2CW%2CL'
opener = urllib2.build_opener()
opener.addheaders = [('User-agent','Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
outputDirPrefix = "../../../output/"
print 'Starting Retrieval'
logging.info('Staring Retrieval')

response = opener.open(url)
content = json.load(response, encoding='utf-8')
teamDataFileName = "%steamdata.json" %(outputDirPrefix)
with open(teamDataFileName, 'w+') as outfile:
    json.dump(content, outfile)
outfile.close

print 'Stopping Retrieval'
logging.info('Stopping Retrieval')
