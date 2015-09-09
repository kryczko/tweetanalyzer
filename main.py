#!/usr/bin/env python

import ibm_db
import tweepy
import inspect
from datetime import date
from alchemyapi import AlchemyAPI
import time


tracking = ['db2', 'mysql', 'dashdb', 'oracle 12c', 'mongodb', 'postgresql', 'microsoft sql server', 'sqlite']

conn = ibm_db.connect('DATABASE=BLUDB; HOSTNAME=awh-yp-small02.services.dal.bluemix.net; PORT=50000; PROTOCAL=TCPIP; UID=dash104862; PWD=rBZIHKHQqX0o', '', '')

class MyStreamListener(tweepy.StreamListener):
	def __init__(self, api):
		tweepy.StreamListener.__init__(self, api)
		self.alchemyapi = AlchemyAPI()
		self.inserts = 0
		self.print_count = 0
	
	def get_main_keyword(self, text):
		if 'keywords' in self.alchemyapi.keywords('text', text):
			if len(self.alchemyapi.keywords('text', text)['keywords']) > 0:
				return self.alchemyapi.keywords('text', text)['keywords'][0]['text']
		return ''

	def get_sentiment(self, text):
		if 'docSentiment' in self.alchemyapi.sentiment('text', text):
			return self.alchemyapi.sentiment('text', text)['docSentiment']['type']

	def is_english(self, text):
		if self.alchemyapi.keywords('text', text)['language'] == 'english':
			return True
		return False

	def what_cat(self, text):
		for elem in tracking:
			for smaller_elem in elem.split():
				if smaller_elem in text.lower():
					return elem
		return 'unknown'

	def insert_into_table(self, data):
		sql = 'insert into dash104862.tweepy_tweets('
		columns = ''
		values = ' values('

		for key,val in data.items():
			columns += str(key) + ','
			values += str(val) + ','
		columns = columns[:-1] + ')'
		values = values[:-1] + ')'

		sql += columns + values

		# print (sql)
		stmt = ibm_db.prepare(conn, sql)
		try:
			ibm_db.execute(stmt)
			self.inserts += 1
			print ("%d inserts completed" % (self.inserts))
		except:
			print("Warning: Insertion into table failed.")
		# result = ibm_db.fetch_both(stmt)
		# while (result):
		# 	print( result )
		# 	result = ibm_db.fetch_both(stmt)
	
	def on_status(self, status):
		if self.print_count == 0:
			print ("Searching for tweets...")
			self.print_count += 1

		print ('%d Twitter API calls remaining...' % api.rate_limit_status()['resources']['application']['/application/rate_limit_status']['remaining'])

		if self.is_english(status.text):
			tweet_dict = {}
			tweet_dict['tweet'] = "\'" + status.text.lower().replace('\'', ' ') + "\'"
			tweet_dict['date_of_tweet'] = 'TIMESTAMP_FORMAT(\'' + str(status.created_at) + '\',\'YYYY-MM-DD HH24:MI:SS\')'
			tweet_dict['date_of_author'] = 'TIMESTAMP_FORMAT(\'' + str(status.author.created_at) + '\',\'YYYY-MM-DD HH24:MI:SS\')' # when the user was created
			tweet_dict['verified'] = "\'" + str(status.author.verified) + "\'" # verfied
			tweet_dict['author_favourites'] = status.author.favourites_count # total number of favourites
			tweet_dict['author_followers'] = status.author.followers_count # total number of followers
			tweet_dict['author_friends'] = status.author.friends_count # total number of follows
			tweet_dict['screen_name'] = "\'" + status.author.screen_name + "\'" # username 
			tweet_dict['tweet_time_zone'] = "\'" + str(status.author.time_zone) + "\'" # where the user is from
			tweet_dict['tweet_favourite_count'] = status.favorite_count
			tweet_dict['tweet_retweet_count'] = status.retweet_count
			tweet_dict['tweet_keyword'] = "\'" + str(self.get_main_keyword(status.text).lower()) + "\'" 
			tweet_dict['tweet_sentiment'] = "\'" + str(self.get_sentiment(status.text)) + "\'"
			tweet_dict['search_string'] = "\'" + self.what_cat(status.text) + "\'"
			self.insert_into_table(tweet_dict)



consumer_key = 'aAG0jYGwxKSHwdQ2tSfDRMskR'
consumer_secret = '3w2JOgJDHulIXZtdB1WZPjJZXjbLNGkH0eG2H1RNehIyPDVTIV'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token('3313570090-Z2EApD4DAMJqKCCbGyG3CpEymk9Kx5l8Wqng0VM', 'tlU875YAS94wnpZGFXaHno55Ow6AX9aJctHNvQzfPaL9y')

# Construct the API instance
api = tweepy.API(auth, wait_on_rate_limit=True)
myStreamListener = MyStreamListener(api)
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)

myStream.filter(track=tracking)
