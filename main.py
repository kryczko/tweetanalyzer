#!/usr/bin/env python

import tweepy

class MyStreamListener(tweepy.StreamListener):
	def __init__(self):
		tweepy.StreamListener.__init__(self)
		self.tweets = []

	def on_status(self, status):
		self.tweets.append(status.text)
		print 'I have found', len(self.tweets), 'tweets'

consumer_key = 'aAG0jYGwxKSHwdQ2tSfDRMskR'
consumer_secret = '3w2JOgJDHulIXZtdB1WZPjJZXjbLNGkH0eG2H1RNehIyPDVTIV'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token('3313570090-Z2EApD4DAMJqKCCbGyG3CpEymk9Kx5l8Wqng0VM', 'tlU875YAS94wnpZGFXaHno55Ow6AX9aJctHNvQzfPaL9y')

# Construct the API instance
api = tweepy.API(auth)

print "Everything worked!"

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)

myStream.filter(track=['google'])