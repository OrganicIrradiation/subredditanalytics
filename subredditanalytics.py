from ConfigParser import SafeConfigParser
from datetime import datetime
from ftplib import FTP
import pyLogger
from random import shuffle
from requests.exceptions import HTTPError
import time

import SubredditAnalyticsBot as SAB
import SubredditAnalyticsNet as SAN

def submit_post(bot, subreddit, URL):
    logger.logInfo('Submitting post...')
    title = "SubredditAnalytics - /r/{0} - {1}".format(subreddit, datetime.now().strftime("%B %d, %Y"))
    submission = bot.client.submit(bot.post_to, title, url=URL)

    # Check if subreddit is NSFW and if so, mark submission as NSFW
    if bot.client.get_subreddit(subreddit).over18:
        submission.mark_as_nsfw()
        logger.logInfo('/r/{0} Marked as NSFW'.format(subreddit))
        
    return submission

def main():
    logger.logInfo("Welcome to the Reddit SubredditAnalytics Bot.")

    # Get the user information from the configuration file
    config = SafeConfigParser()
    config.read('config.ini')

    SAB.login(myBot, config.get('reddit', 'username'),
                     config.get('reddit', 'password'),
                     config.get('reddit', 'user_agent'))
    myBot.post_to = config.get('reddit', 'subreddit')

    while(1):
        # Load the subreddits to process
        subredditsProcessed = open('subsProcessed.txt').read().splitlines()
        subredditsToProcess = open('subsToProcess.txt').read().splitlines()

        while len(subredditsToProcess) > 0:
            subreddit = subredditsToProcess.pop(0)

            if subreddit not in subredditsProcessed:
                logger.logInfo('Processing {0}'.format(subreddit))

                # Create network object that will hold the nodes and edges
                myNet = SAN.SubredditAnalyticsNet()
                myNet.parentSub = subreddit
                myNet.logger.setLogLevel(consolelogLevel)

                # Add the processed subreddit to the bot's ban list
                myBot.subBanList.append(subreddit)

                try:
                    # Retrieve users, randomize, and take a sample for further processing
                    userList = myBot.getUsers(subreddit)

                    subList = list()
                    # Get each user's subscriptions and add them to the network
                    for index, user in enumerate(userList):
                        subList = myBot.getSubs(user)
                        logger.logInfo('Processed user {0} of {1} - {2} - {3} unique subs'.format(index+1, len(userList), user, len(subList)))
                        if subList:
                            myNet.add_users_node(user,subList)

                    # Save the JSON network file
                    myNet.processNetforSave(outputSubs,myBot)
                    myNet.saveDATAfile(len(userList))

                    logger.logInfo('Uploading via FTP')
                    try:
                        session = FTP(config.get('ftp', 'server'),
                                      config.get('ftp', 'username'),
                                      config.get('ftp', 'password'))
                        session.set_pasv(True)
                        session.cwd('JSON')
                        source = open('html/JSON/'+subreddit+'.json','rb')
                        session.storbinary('STOR '+subreddit+'.json', source)
                        source.close()
                        session.quit()
                    except Exception, e:
                        logger.logError('FTP:'+str(e))

                    logger.logInfo('Submitting to Reddit')
                    try:
                        URL = "http://redditanalytics.altervista.org/show.php?subreddit={0}".format(subreddit)
                        newsubmission = submit_post(myBot, subreddit, URL)
                    except Exception, e:
                        logger.logError('Reddit Submission: '+str(e))

                    # Add top 5 subreddits to analyze to the queue
                    topSubreddits = myNet.subredditsSortedByUsers()[:5]
                    for (sub,n) in topSubreddits:
                        if sub not in subredditsToProcess:
                            if sub not in subredditsProcessed:
                                subredditsToProcess.append(sub)

                    # Remove the processed subreddit from the ban list and append to processed
                    myBot.subBanList.remove(subreddit)
                    subredditsProcessed.append(subreddit)
                
                except HTTPError, e:
                    if e.response.status_code == 403:
                        logger.logCrit('Critical error! {0} - Subreddit not found'.format(e))
                        myBot.subBanList.remove(subreddit)   
                        subredditsProcessed.append(subreddit)
                    else:
                        logger.logCrit('Critical error! {0}'.format(e))
                        myBot.subBanList.remove(subreddit)
                        subredditsToProcess.append(subreddit)
                del myNet
            else:
                logger.logInfo('Already processed {0}'.format(subreddit))

            # Save our "state files"
            try:
                with open("subsToProcess.txt", "w") as theFile:
                    # Shuffle, just to spice things up
                    shuffle(subredditsToProcess)
                    for subreddit in subredditsToProcess:
                      theFile.write("%s\n" % subreddit)
            except Exception, e:
                logger.logError('Saving subsToProcess:'+str(e))
                
            try:
                with open("subsProcessed.txt", "w") as theFile:
                    for subreddit in subredditsProcessed:
                      theFile.write("%s\n" % subreddit)
            except Exception, e:
                logger.logError('Saving subsToProcess:'+str(e))

        time.sleep(60)

if __name__ == "__main__":
    consolelogLevel = pyLogger.INFO
    logger = pyLogger.logger('subredditanalytics', consolelogLevel)
    
    myBot = SAB.SubredditAnalyticsBot()
    myBot.scrapeLimitComments = 1000
    myBot.scrapeLimitPosts = 1000
    myBot.scrapeLimitUsers = 1000
    myBot.logger.setLogLevel(consolelogLevel)

    outputSubs = 50
    
    main()
