from praw.errors import *
from praw.handlers import MultiprocessHandler
from requests.exceptions import HTTPError

import itertools
import pyLogger
import praw

class SubredditAnalyticsBot(object):
    def __init__(self):
        """
        Initialize the class with some basic attributes.
        """

        self.logger = pyLogger.logger('SubredditAnalyticsBot', pyLogger.INFO)
        
        # Maximum threads to crawl. Reddit doesn't like it when you go over 1000
        self.scrapeLimitComments = None
        self.scrapeLimitPosts = None
        self.scrapeLimitUsers = 1000

        self.post_to = "test"

        self.subBanList = ['adviceanimals', 'announcements', 'art', 'askreddit'             , 'askscience', 'atheism', 'aww', 'bestof',
                            'blog', 'books', 'creepy', 'dataisbeautiful', 'diy', 'documentaries', 'earthporn',
                            'explainlikeimfive', 'fitness', 'food', 'funny', 'futurology', 'gadgets', 'gaming',
                            'getmotivated', 'gifs', 'history', 'iama', 'internetisbeautiful', 'jokes',
                            'lifeprotips', 'listentothis', 'mildlyinteresting', 'movies', 'music', 'news',
                            'nosleep', 'nottheonion', 'oldschoolcool', 'personalfinance', 'philosophy',
                            'photoshopbattles', 'pics', 'politics', 'science', 'showerthoughts', 'space', 'sports',
                            'technology', 'television', 'tifu', 'todayilearned', 'twoxchromosomes',
                            'upliftingnews', 'videos', 'worldnews', 'writingprompts', 'wtf']

        self.userBanList = ['automoderator']
        
    def login(self, username, password, user_agent):
        handler = MultiprocessHandler()
        self.client = praw.Reddit(user_agent=user_agent, handler=handler)
        self.client.login(username, password, disable_warning=True)

    def getUsers(self, subreddit):
        userList = []
       
        self.logger.logDebug('Retrieving submissions from {0}'.format(subreddit))
        submissions = self.client.get_subreddit(subreddit).get_hot(limit=self.scrapeLimitPosts)
        for index, submission in enumerate(submissions):
            self.logger.logDebug('Processing submission {0}'.format(submission.short_link))
            
            if submission.author:
                redditor = str(submission.author.name).lower()
                if (redditor not in self.userBanList) and ('bot' not in redditor):
                    userList.append(redditor)

            self.logger.logDebug('Loading more comments')
            submission.replace_more_comments(limit=None, threshold=0)
            for comment in praw.helpers.flatten_tree(submission.comments):
                try:
                    redditor = str(comment.author.name).lower()
                    if (redditor not in self.userBanList) and ('bot' not in redditor):
                        userList.append(redditor)                     
                except AttributeError:
                    continue
            
            # Prune duplicates
            userList = list(set(userList))

            self.logger.logInfo('Processed {0} of {1} max - {2} total users found ({3} max)'.format(index+1, self.scrapeLimitPosts, len(userList), self.scrapeLimitUsers))

            if len(userList) >= self.scrapeLimitUsers:
                break
            
        userList = userList[:self.scrapeLimitUsers]
        return userList

    def getSubs(self, user):
        subList = []
        
        # Handle shadowbanned/deleted accounts
        try:
            comments = self.client.get_redditor(user).get_comments('all', limit=self.scrapeLimitComments)
        except HTTPError, e:
            self.logger.logWarn('Error accessing user {0} - {1}'.format(user,e))
            return []

        # Loop through user's comments and add subreddit if unique
        
        try:
            for comment in comments:
                try:
                    subreddit = comment.subreddit.display_name.lower()
                    if subreddit not in self.subBanList:
                        self.logger.logDebug('Appending sub {0}'.format(subreddit))
                        subList.append(subreddit)
                except AttributeError:
                    self.logger.logWarn('Error accessing comment author {0}'.format(comment.permalink))
                    continue
        except Exception, e:
            self.logger.logWarn('Error with user {0}\'s comment loop - {1}'.format(user,e))

        return list(set(subList))

def login(bot, username, password, user_agent):
    bot.logger.logInfo('Logging in as {0}...'.format(username))
    
    for i in range(0, 3):
        try:
            bot.login(username, password, user_agent)
            bot.logger.logInfo('Login successful.')
            break
        
        except (InvalidUser, InvalidUserPass, RateLimitExceeded, APIException) as e:
                bot.logger.logWarn('Error - {0}'.format(e))
                exit(1)
                
        except HTTPError, e:
            bot.logger.logWarn('Error - {0}'.format(e))
            if i == 2:
                self.logger.logCrit('Failed to login')
                exit(1)
                
            else:
                bot.logger.logCrit('Retrying in 1 minute')
                # wait a minute and try again
                sleep(60)
                continue
