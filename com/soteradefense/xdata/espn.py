import os
import logging
import urllib2
import re
from datetime import datetime
from string import Template
from bs4 import BeautifulSoup

""" NOTES
This module takes the espn URLs generated from xdata.py and queries
the espn schedule page. From this page the code will match the anchor 
tag to the specific game. It will then pull the espn game id from this
link. It will use the espn game id to access the comments about the
game stored at facebook.

Caution: The current facebook url contains an api_key. Not sure if this
key is dynamic, transient or constant. This may cause problems for 
reuse. Also the comments currently contain a "view more" link for both
the individual comment chains and for the full list of comments for the 
game. The code currently does not account for pulling addition comments
by way of this link. That will take more substantial processing.

Additionally, the code currently assumes a reply depth of 1. Its possible
to reply to replies on the web page. This is not currently accounted for
within this code.
"""

""" Variables """
logging.basicConfig(filename='../../../espn.log', level=logging.DEBUG)
espnConvTemplate = Template("http://espn.go.com/nba/conversation?gameId=$gameId")
commentTemplate = Template("https://www.facebook.com/plugins/comments.php?api_key=116656161708917&channel_url=http%3A%2F%2Fstatic.ak.facebook.com%2Fconnect%2Fxd_arbiter.php%3Fversion%3D28%23cb%3Df6f3ef02c%26domain%3Despn.go.com%26origin%3Dhttp%253A%252F%252Fespn.go.com%252Ffe8b1fd14%26relation%3Dparent.parent&href=http%3A%2F%2Fscores.espn.go.com%2Fnba%2Fconversation%3FgameId%3D$gameId&locale=en_US&numposts=25&sdk=joey&width=872")
outputDirPrefix = "../../../output/"
espnUrlFile = "%sespn_search_urls.txt" % outputDirPrefix
opener = urllib2.build_opener()
opener.addheaders = [('User-agent','Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
startTime = datetime.now()
gamesProcessed = 0
commentsProcessed = 0
exceptionsThrown = 0

print 'Starting Retrieval'
logging.info('Staring Retrieval')

""" Pull comments and replies out of the HTML element """
def processFeedback(commentRoot, commentsFile):
    global commentsProcessed
    commenterName = commentRoot.find("a", {"class" : "profileName"}).text
    commenterComment = commentRoot.find("div", {"class" : "postText"}).text.strip().replace('\n',' ')
    commentsFile.write("%s::%s\n" % (commenterName, commenterComment))
    commentsProcessed += 1
    for r in commentRoot.find_all("li", {"class" : "fbFeedbackPost fbFirstPartyPost fbCommentReply"}):
        replier = r.find("a", {"class" : "profileName"}).text
        reply = r.find("div", {"class" : "postText"}).text.strip().replace('\n',' ')
        commentsFile.write("%s::%s\n" % (replier, reply))

if os.path.exists(espnUrlFile):
    """ Read the URL file generated by the nba.com routine """
    with open(espnUrlFile, "r") as urlFile:
        for line in urlFile:
            try:
                url, query, nbaGameId = line.split('|')
                nbaGameId = nbaGameId.rstrip('\n')
                logging.debug("\n---ESPN Search URL: %s\n---Query: %s\n---GameId: %s" % (url, query, nbaGameId))
                unstructured = opener.open(url)
                soup = BeautifulSoup(unstructured)
                """ Follow the nba.com process file naming convention """
                commentsFileName = "%s00%s_espn_comments.txt" %(outputDirPrefix, nbaGameId)
                commentsFile = open(commentsFileName, 'w+')
                try:
                    """ Find the link that matches the game data """
                    for a in soup.find_all('a', text=re.compile(query), limit=1):
                        currentGameId = a['href'].split('=')[1]
                        commentUrl = commentTemplate.substitute(gameId=currentGameId)
                        logging.debug("Comment URL: %s" % commentUrl)
                        """ Poll the facebook comments page for the specific game """
                        comments = opener.open(commentUrl)
                        chatSoup = BeautifulSoup(comments)
                        """ Iterate over the comments """
                        for l in chatSoup.findAll("li", {"class" : "fbFeedbackPost fbFirstPartyPost fbTopLevelComment"}):
                            try:
                                processFeedback(l, commentsFile)
                            except Exception as e:
                                logging.exception("Exception when processing comments")
                                exceptionsThrown += 1
                                """ Continue with remaining URLs """
                                continue
                except Exception as e:
                    logging.exception("Exception when processing comments")
                    exceptionsThrown += 1
                finally:
                    commentsFile.close()
                gamesProcessed += 1
                print("."),
            except Exception as e:
                logging.exception("Unable to open URL: %s" % url)
                print("!"),
                exceptionsThrown += 1
                """ Continue with remaining URLs """
                continue
    urlFile.close()
opener.close()

endTime = datetime.now()
delta = endTime - startTime

print '\nStopping Retrieval\n-- Processing Time: %d seconds\n-- Games Processed: %s\n-- Comments Processed: %s\n-- Exceptions Caught: %s' %(delta.seconds + delta.microseconds/1E6, gamesProcessed, commentsProcessed, exceptionsThrown)
logging.info('Stopping Retrieval\n-- Processing Time: %d seconds\n-- Games Processed: %s\n-- Comments Processed: %s\n-- Exceptions Caught: %s' %(delta.seconds + delta.microseconds/1E6, gamesProcessed, commentsProcessed, exceptionsThrown))