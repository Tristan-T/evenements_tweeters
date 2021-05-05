import tweepy
import json
import datetime
import spacy
from pymongo import MongoClient, GEO2D
import urllib
import datetime


import mongodb
import geoname

nlp = spacy.load("en_core_web_sm")

keyWords = [
"floodwater",
"Earthquake",
"Volcanic Eruptions",
"Volcanic Eruption",
"volcanoes",
"Hurricane",
"Cyclone",
"Storm",
"Flooding",
"Extreme precipitation",
"Wildfire",
"Landslide",
"Tsunami"]

def isRetweet(tweet):
    try:
        tweet.retweeted_status
        return True
    except AttributeError:
        return False

def getLocations(tweetText):
    doc = nlp(tweetText)
    locations = []
    for ent in doc.ents:
        if ent.label_ == 'GPE':
            locations.append(ent.text)
    return locations

class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)
        if (not(isRetweet(status))) :
            words = status.text.split()
            disasterType = ""
            for keyWord in keyWords:
                if keyWord in words:
                    disasterType = keyWord
            url = "https://twitter.com/i/web/status/" + str(status.id)
            locationsInTweet = getLocations(status.text)
            if (len(locationsInTweet) == 1):
                try :
                    location = geoname.getLocation(locationsInTweet[0])
                    mongodb.addTweetRealTimeDB(status.id, status.text, disasterType, url, status._json, status.created_at, location)
                except NameError:
                    mongodb.addTweetValideDB(status.id, status.text, disasterType, url, status._json, status.created_at, locationsInTweet)
            elif (len(locationsInTweet) > 1):
                mongodb.addTweetValideDB(status.id, status.text, disasterType, url, status._json, status.created_at, locationsInTweet)
            else:
                mongodb.addTweetValideDB(status.id, status.text, disasterType, url, status._json, status.created_at, None)

    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_error disconnects the stream
            return True
        else:
            print("The status code is " + status_code)
            return False


auth = tweepy.OAuthHandler("AGkuOLBeI1fuvznbTuvClUxzY", "49rnsc86xjyIK4PYWqLDyDYvkpdh2R4L7IU1rej9djmHAWGXId")
api = tweepy.API(auth)

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
myStream.filter(track=keyWords, is_async=True)
