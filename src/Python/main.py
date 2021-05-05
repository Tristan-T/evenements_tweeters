#MongoDB
from pymongo import MongoClient, GEO2D
from pymongo.errors import ConnectionFailure, OperationFailure
import dns
import urllib
#Config file
import json
#Geoname
from geocoder import geonames
#Tweepy
import tweepy
#spaCy
import spacy
#Miscellaneous
from datetime import datetime
import time
from http.client import IncompleteRead
import sys

#Global variables
#Config file dict (json)
config = ""
#Geocoder for geoname
geolocator = ""
#MongoDB
tweetValide = ""
tweetRealTime = ""
#spaCy
nlp = ""
#Tweepy
api = ""


#-----------------------------------------------------#
#                    Config functions                 #
#-----------------------------------------------------#

#Load the configuration file and store it in the global variable config
#TODO : Handle IOError exception
def loadConfig():
    print("CONFIG :: Chargement du fichier de configuration")

    global config
    with open("config.json", "r") as config_json:
        config = json.load(config_json)
    print("CONFIG :: Fichier de configuration chargé")


#-----------------------------------------------------#
#                   Geocoder functions                #
#-----------------------------------------------------#

# Return the geographical informations of a city string
def getLocation(textLoc):
    #parameters maxRows=5 will return a list of the five first cities
    location = geonames(textLoc, key=config['geoname']['login_key'])
    if len(location) == 1:
        # print(location.address)
        # print(location.point.format_unicode())
        return [float(location.lng), float(location.lat)]
    else:
        print("GEONAME :: Location non trouvée : " + textLoc)
        raise NameError("LocationNotFound")

#-----------------------------------------------------#
#                   MongoDB functions                 #
#-----------------------------------------------------#

def loadMongo():
    print("MONGODB :: Connexion à la base MongoDB")
    # We use urllib.parse.quote_plus for special characters that needs to be normalized for url
    username = urllib.parse.quote_plus(config["mongodb"]["username"])
    password = urllib.parse.quote_plus(config["mongodb"]["password"])
    address = config["mongodb"]["address"]
    dbname = config["mongodb"]["db_name"]
    uri = "mongodb+srv://%s:%s@%s/%s" % (username, password, address, dbname)

    #We check whether there are options to add to the URI
    options = config["mongodb"]["optional_URI_parameters"]
    if options:
        uri += "?" + options
    else:
        print("MONGODB :: Pas d'options supplémentaires pour l'URI")

    #We connect to the base
    client = MongoClient(uri)

    #Set the global collections accessors
    db = client[dbname]
    global tweetValide
    global tweetRealTime
    tweetValide = db[config["mongodb"]["collection_valid_name"]]
    tweetRealTime = db[config["mongodb"]["collection_real_time_name"]]

    try:
        #Low impact command to check if the connection was successful
        client.admin.command('ismaster')
        print("MONGODB :: Connexion réussie")
    except ConnectionFailure:
        raise SystemExit("MONGODB :: La connexion à la base a échouée, vérifiez l'état de votre base")
    except OperationFailure:
        raise SystemExit("MONGODB :: La connexion à la base a échouée, vérifiez vos paramètres")


"""
Cette fonction ajoute un tweet à la base de données "real-time" du programme.
Elle prends en paramètre :
        - L'ID du tweet, qui sera utilisé comme _id dans MongoDB
        - Le string JSON du tweet
        - La date de publication du tweet (convertissable en objet Date)
        - La location GPS du tweet (longitude puis latitude)
"""
def addTweetRealTimeDB(idTweet, text, disasterType, url, jsonData, date, location):
    print("MONGODB :: Adding tweet real time " + str(idTweet))
    tweetRealTime.insert_one({
        "_id": str(idTweet),
        "text": text,
        "disasterType": disasterType,
        "url": url,
        "json": jsonData,
        "date": date,
        "location": location
    })

def addTweetValideDB(idTweet, text, disasterType, url, jsonData, date, locations):
    print("MONGODB :: Adding tweet to be validated " + str(idTweet))
    tweetValide.insert_one({
        "_id": str(idTweet),
        "text": text,
        "disasterType": disasterType,
        "url": url,
        "json": jsonData,
        "date": date,
        "locations": locations,
        "validated": False,
        "validatedLocations": None,
        "offTopic": None,
        "rule": None
    })

#-----------------------------------------------------#
#                   spaCy functions                   #
#-----------------------------------------------------#
#Load spaCy basic pipeline
def loadSpacy():
    print("SPACY :: Chargement du pipeline")
    global nlp
    nlp = spacy.load("en_core_web_sm")
    print("SPACY :: Chargement terminé")

#Find all locations objects in a text and return a list of tokens
def getLocationsToken(tweetText):
    print(tweetText)
    doc = nlp(tweetText)
    locations = []
    for ent in doc.ents:
        if ent.label_ == 'GPE' and ent.text not in locations:
            locations.append(ent.text)
    print(locations)
    return locations

#-----------------------------------------------------#
#                   Tweepy functions                  #
#-----------------------------------------------------#
def isKeywordInText(text):
    for keyword in config["evenements_tweeter"]["keywords"]:
        if keyword in text:
            return True
    return False

class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        try:
            status.retweeted_status
            return None
        except AttributeError:
            pass

        try:
            status.quoted_status_id
            return None
        except AttributeError:
            pass

        tweetText = ""
        try:
            status.extended_tweet
            if not(status.in_reply_to_status_id) and isKeywordInText(status.extended_tweet['full_text']):
                tweetText = status.extended_tweet['full_text']
            else:
                return None
        except AttributeError:
            if not(status.in_reply_to_status_id) and isKeywordInText(status.text):
                tweetText = status.text
            else:
                return None

        disasterType = ""
        for keyWord in config["evenements_tweeter"]["keywords"]:
            if keyWord in tweetText:
                disasterType = keyWord
        url = "https://twitter.com/i/status/" + str(status.id)
        locationsInTweet = getLocationsToken(tweetText)
        if (len(locationsInTweet) == 1):
            try :
                location = getLocation(locationsInTweet[0])
                addTweetRealTimeDB(status.id, tweetText, disasterType, url, status._json, status.created_at, location)
            except NameError:
                addTweetValideDB(status.id, tweetText, disasterType, url, status._json, status.created_at, locationsInTweet)
        else:
            addTweetValideDB(status.id, tweetText, disasterType, url, status._json, status.created_at, locationsInTweet)

    def on_error(self, status_code):
        print("FOUND ERROR")
        print(status_code)
        print(self)
        #Full list of codes https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/guides/connecting
        if status_code == 420:
            #returning False in on_error disconnects the stream
            print("TWEEPY :: ERROR :: API rate limit, wait before restarting the program or change API keys")
            print("TWEEPY :: INFO :: The software will now automatically wait 15 minutes before resuming, unless manually restarted")
            time.sleep(15 * 60)
            return True
        if status_code == 403:
            print("TWEEPY :: ERROR :: Invalid credentials, check them again before restarting the app")
            return False
        if status_code == 503:
            print("TWEEPY :: ERROR :: Streaming server is over capacity, try again later")
            return False
        else:
            print("TWEEPY :: ERROR :: The status code is " + str(status_code))
            fileError = "error_"+now.strftime("%d/%m/%Y %H:%M:%S")+".txt"
            print("TWEEPY :: INFO :: The full detail of the error will be stored in : " + fileError)
            print("TWEEPY :: INFO :: The stream will not be restarted")
            with open(fileError,"w") as f:
                f.writelines(status_code)
            return False

def loginTweepy():
    print("TWEEPY :: Connexion API Twitter")
    global api
    auth = tweepy.OAuthHandler(config["tweepy"]["consumer_key"], config["tweepy"]["consumer_secret"])
    auth.set_access_token(config["tweepy"]["access_token"], config["tweepy"]["access_token_secret"])
    api = tweepy.API(auth)
    print("TWEEPY :: Connexion réussie")

def startTweepyStream():
    print("TWEEPY :: Démarrage du Listener")
    myStreamListener = MyStreamListener()
    try:
        myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener, tweet_mode='extended')
        myStream.filter(track=config["evenements_tweeter"]["keywords"])
    #When there are too many tweets, the Streaming API will send them too fast to be consumed, we ignore the error
    except IncompleteRead or ProtocolError:
        print("ERROR CAUGHT")
        input()
        pass
    except KeyboardInterrupt:
        sys.exit()
    print("TWEEPY :: Le listener a démarré")


#Point d'entrée
def main():
    print("MAIN :: Événements tweeter est en cours de démarrage...")
    loadConfig()
    loadMongo()
    loadSpacy()
    loginTweepy()
    startTweepyStream()


if __name__ == "__main__":
    main()
