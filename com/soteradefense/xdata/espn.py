import os
import logging
import urllib2
import re
from string import Template
from bs4 import BeautifulSoup


""" Variables """
logging.basicConfig(filename='../../../espn.log', level=logging.DEBUG)
espnConvTemplate = Template("http://espn.go.com/nba/conversation?gameId=$gameId")
commentTemplate = Template("https://www.facebook.com/plugins/comments.php?api_key=116656161708917&channel_url=http%3A%2F%2Fstatic.ak.facebook.com%2Fconnect%2Fxd_arbiter.php%3Fversion%3D28%23cb%3Df6f3ef02c%26domain%3Despn.go.com%26origin%3Dhttp%253A%252F%252Fespn.go.com%252Ffe8b1fd14%26relation%3Dparent.parent&href=http%3A%2F%2Fscores.espn.go.com%2Fnba%2Fconversation%3FgameId%3D$gameId&locale=en_US&numposts=25&sdk=joey&width=872")
outputDirPrefix = "../../../output/"
espnUrlFile = "%sespn_search_urls.txt" % outputDirPrefix
""" http://espn.go.com/nba/conversation?gameId=400278250 """
opener = urllib2.build_opener()

def processFeedback(commentRoot, commentsFile):
    commenterName = commentRoot.find("a", {"class" : "profileName"}).text
    commenterComment = commentRoot.find("div", {"class" : "postText"}).text
    commentsFile.write("%s::%s\n" % (commenterName, commenterComment))
    for r in commentRoot.find_all("li", {"class" : "fbFeedbackPost fbFirstPartyPost fbCommentReply"}):
        replier = r.find("a", {"class" : "profileName"}).text
        reply = r.find("div", {"class" : "postText"}).text
        commentsFile.write("::%s::%s::%s\n" % (commenterName, replier, reply))

if os.path.exists(espnUrlFile):
    with open(espnUrlFile, "r") as urlFile:
        for line in urlFile:
            try:
                url, query, nbaGameId = line.split('|')
                nbaGameId = nbaGameId.rstrip('\n')
                logging.debug("ESPN Search URL: %s\nQuery: %s\nGameId: %s" % (url, query, nbaGameId))
                unstructured = opener.open(url)
                soup = BeautifulSoup(unstructured)
                commentsFileName = "%s00%s_espn_comments.txt" %(outputDirPrefix, nbaGameId)
                commentsFile = open(commentsFileName, 'w+')
                try:
                    for a in soup.find_all('a', text=re.compile(query)):
                        currentGameId = a['href'].split('=')[1]
                        print "GameID: %s" % currentGameId
                        commentUrl = commentTemplate.substitute(gameId=currentGameId)
                        comments = opener.open(commentUrl)
                        chatSoup = BeautifulSoup(comments)
                        for l in chatSoup.findAll("li", {"class" : "fbFeedbackPost fbFirstPartyPost fbTopLevelComment"}):
                            processFeedback(l, commentsFile)
                except Exception as e:
                    logging.error("Exception when processing comments:\n%s " % (e))
                finally:
                    commentsFile.close()
            except Exception as e:
                logging.error("Unable to open URL: %s \n%s " % (url, e))
                print "Unable to open URL: %s" % url
    urlFile.close()
