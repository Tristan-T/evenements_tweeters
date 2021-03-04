import tweepy
import json
import datetime
import spacy
from pymongo import MongoClient, GEO2D
import urllib
import datetime
import mongoDB

keyWords = [
"floodwater", 
"Earthquakes",
"Volcanic Eruptions", 
"volcanoes",
"Hurricanes",
"Cyclones",
"Storm",
"Flooding",
"Extreme precipitation",
"Wildfires",
"Landslides",
"Tsunamis"]

def isRetweet(tweet):
    try:
        tweet.retweeted_status
        return True
    except AttributeError:
        return False

class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        if (not(isRetweet(status))) :
            gps = None if status.coordinates is None else status.coordinates
            words = status.text.split()
            disasterType = ""
            for keyWord in keyWords:
                if keyWord in words:
                    disasterType = keyWord
            url = "https://twitter.com/i/web/status/" + str(status.id)
            mongoDB.addTweetRealTimeDB(status.id, status.text, disasterType, url, status._json, status.created_at, gps)
    
    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_error disconnects the stream
            return False


auth = tweepy.OAuthHandler("AGkuOLBeI1fuvznbTuvClUxzY", "49rnsc86xjyIK4PYWqLDyDYvkpdh2R4L7IU1rej9djmHAWGXId")
api = tweepy.API(auth)

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
myStream.filter(track=keyWords, is_async=True)