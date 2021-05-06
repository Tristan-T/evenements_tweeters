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
from spacy.matcher import DependencyMatcher
#Miscellaneous
from datetime import datetime
import time
from http.client import IncompleteRead
import sys
import _thread
import geonamescache
import re
#Learning model disaster prediction
from relevancy import TextNormalizer
import relevancy as relevancy


#Global variables
#Config file dict (json)
config = ""
#Geocoder for geoname
geolocator = ""
#MongoDB
tweetValide = ""
tweetRealTime = ""
tweetInvalide = ""
#spaCy
nlp = ""
#Tweepy
api = ""
#geonamescache
gc = geonamescache.GeonamesCache()


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
    global tweetInvalide
    tweetValide = db[config["mongodb"]["collection_valid_name"]]
    tweetRealTime = db[config["mongodb"]["collection_real_time_name"]]
    tweetInvalide = db[config["mongodb"]["collection_invalid_name"]]

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
def addTweetRealTimeDB(idTweet, text, disasterType, url, jsonData, date, location, tweetTextClean, tokens, isPast, onlyHashtags, spacyDep, spacyGPE):
    print("MONGODB :: Adding tweet real time " + str(idTweet))
    tweetRealTime.insert_one({
        "_id": str(idTweet),
        "text": text,
        "disasterType": disasterType,
        "url": url,
        "json": jsonData,
        "date": date,
        "location": location, #STRING
        "tokens": tokens,
        "isPast": isPast,
        "onlyHashtags": onlyHashtags,
        "spacyDep": spacyDep,
        "spacyGPE": spacyGPE
    })

def addTweetValideDB(idTweet, text, disasterType, url, jsonData, date, locations, tweetTextClean, tokens, isPast, onlyHashtags=None, spacyDep=None, spacyGPE=None):
    print("MONGODB :: Adding tweet to be validated " + str(idTweet))
    tweetValide.insert_one({
        "_id": str(idTweet),
        "text": text,
        "disasterType": disasterType,
        "url": url,
        "json": jsonData,
        "date": date,
        "locations": locations, #LISTE DE STRING
        "validated": False,
        "validatedLocations": None,
        "offTopic": None,
        "rule": None,
        "tokens": tokens,
        "isPast": isPast,
        "onlyHashtags": onlyHashtags,
        "spacyDep": spacyDep,
        "spacyGPE": spacyGPE
    })

def addTweetInvalideDB(idTweet, text, disasterType, url, jsonData, date):
    print("MONGODB :: Adding tweet invalidated " + str(idTweet))
    tweetInvalide.insert_one({
        "_id": str(idTweet),
        "text": text,
        "disasterType": disasterType,
        "url": url,
        "json": jsonData,
        "date": date
    })

#-----------------------------------------------------#
#                   spaCy functions                   #
#-----------------------------------------------------#
#Load spaCy basic pipeline
def loadSpacy():
    print("SPACY :: Chargement du pipeline")
    global nlp
    nlp = spacy.load("en_core_web_sm")
    # Retrieve the default token-matching regex pattern
    re_token_match = spacy.tokenizer._get_regex_pattern(nlp.Defaults.token_match)
    # Add #hashtag pattern
    re_token_match = f"({re_token_match}|#\\w+|@\\w+)"
    nlp.tokenizer.token_match = re.compile(re_token_match).match
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

def onlyHashtags(doc) :
    #Tester la vitesse
    listHashtags = list(filter(lambda tok: ('#' in tok.text[0]), doc))

    foundCity = False
    foundDisaster = False

    nameCity = []

    for hashtag in listHashtags:
        hashtagValue = hashtag.text[1:].casefold()
        if(hashtagValue in [x.casefold() for x in config["evenements_tweeter"]["keywords"]]):
            foundDisaster = True
        if(len(gc.search_cities(hashtagValue.capitalize())) > 0):
            foundCity = True
            nameCity.append(hashtagValue)

    if foundCity and foundDisaster:
        return [True, nameCity[0]]
    else:
        return [False, nameCity]

def isPast(doc):
    #Un seul temps pour tout le texte ?
    for token in doc:
        tense = token.morph.get("Tense")
        if len(tense) == 1:
            if (tense[0] == 'Past') :
                return True
    return False

def getGPE(doc):
    gpe = []
    for ent in doc.ents:
        if ent.label_ == 'GPE' :
            gpe.append(ent.text)
    return gpe

def containsDisaster(doc):
    for token in doc:
        if (token.text in [x.casefold() for x in config["evenements_tweeter"]["keywords"]]) :
            return True
    return False

def spacyGPE(doc, firstTime=True):
    gpeList = getGPE(doc)
    newWords = []
    if (len(gpeList) == 0):
        if (not firstTime):
            #envoie BD
            return [False, []]
        else :
            for word in doc:
                newWord = word.text_with_ws.casefold().capitalize()
                newWords.append(newWord)
            doc2 = nlp(''.join(newWords))
            spacyGPE(doc2, firstTime=False)
    if (len(gpeList) == 1) :
        #Si pas au passé et contient un désastre c'est ok
        if(not isPast(doc) and containsDisaster(doc)) :
            return [True, gpeList[0]]
        else:
            return [False, gpeList]
    if (len(gpeList) > 1) :
        for gpe in gpeList:
            #On supprime les GPE qui ne sont pas des villes
            if (len(gc.search_cities(gpe.capitalize())) == 0) :
                print("Suppression GPE : "+ gpe)
                gpeList.remove(gpe)

        if (len(gpeList) == 0) :
            #envoie bd
            return [False, []]

        if (len(gpeList) == 1) :
            if(not isPast(doc) and containsDisaster(doc)) :
                return [True, gpeList[0]]
            else:
                return [False, gpeList]

        if (len(gpeList) > 1) :
            for sentence in doc.sents:
                print("")
                print("phrase :", sentence.text)
                print("gpe :", getGPE(sentence))
                print("contient disaster :", containsDisaster(sentence))
                if (len(getGPE(sentence)) == 1 and containsDisaster(sentence)) :
                    return [True, gpeList[0]]

    return [False, gpeList]

def spacyDep(doc):
    matcher = DependencyMatcher(nlp.vocab, validate=True)
    pattern = [
      {
        "RIGHT_ID": "anchor_AUX",       #unique name
        "RIGHT_ATTRS": {"POS":"AUX"}  #token pattern for disaster
      },
      {
        "LEFT_ID": "anchor_AUX",
        "REL_OP": ">",
        "RIGHT_ID": "anchor_disaster", ##Il faut aussi vérifier que c'est bien un désastre
        "RIGHT_ATTRS": {"DEP":"attr"}
      },
      {
        "LEFT_ID":"anchor_AUX",
        "REL_OP": ">",
        "RIGHT_ID":"AUX_prep",
        "RIGHT_ATTRS": {"DEP":"prep", "POS":"ADP"}
      },
      {
        "LEFT_ID":"AUX_prep",
        "REL_OP" :">",
        "RIGHT_ID":"pobj_prep",
        "RIGHT_ATTRS": {"DEP":"pobj"} ##Normalement c'est une ville, il faut donc la recup
      }
    ]
    matcher.add("DISASTER", [pattern])
    #displacy.serve(doc)
    matches = matcher(doc)
    if bool(matches):
        return [True, doc[matches[0][1][-1]].text]
    else:
        return [False, []]



#-----------------------------------------------------#
#                   Processing tweet                  #
#-----------------------------------------------------#
def heuristicMaster(doc):
    #Si la phrase est au passé, on la supprime toujours
    if isPast(doc):
        return False

    #Si l'une des trois grandes heuristique est vraie, alors on ajoute au site web
    return {"onlyHashtags":onlyHashtags(doc), "spacyGPE":spacyGPE(doc), "spacyDep":spacyDep(doc)}


def processTweet(status):
    #On vérifie que le tweet ne soit pas un retweet
    try:
        status.retweeted_status
        #Return None stoppe la fonction
        return None
    except AttributeError:
        pass

    try:
        status.quoted_status_id
        return None
    except AttributeError:
        pass

    #On vérifie également que ça ne soit pas une réponse et qu'un de nos keywords soit bien dans le texte du tweet
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

    print(tweetText)
    disasterType = ""
    for keyWord in config["evenements_tweeter"]["keywords"]:
        if keyWord in tweetText:
            disasterType = keyWord

    url = "https://twitter.com/i/status/" + str(status.id)

    #Si les trois conditions précentes sont remplies alors on vérifie que le texte du tweet correspondent bien à une catastrophe naturelle avec notre modèle d'aprentissage
    if relevancy.predict(tweetText): #Si c'est vrai on cherche à savoir la localisation
        #On nettoie le texte indépendamment de l'IA
        tweetTextClean = relevancy.MyCleanText(tweetText)

        doc = nlp(tweetTextClean)

        tokens = []
        for word in doc:
            tokens.append(word.text)

        dicHeur = heuristicMaster(doc)

        if not dicHeur: #isPast returned True
            addTweetValideDB(status.id, tweetText, disasterType, url, status._json, status.created_at, [], tweetTextClean, tokens, True)
            return False

        addRL = False
        for key,value in dicHeur.items():
            if value[0]:
                addRL = True
                location = value[1]
                break

        if addRL:
            addTweetRealTimeDB(status.id, tweetText, disasterType, url, status._json, status.created_at, location, tweetTextClean, tokens, False, dicHeur["onlyHashtags"][0], dicHeur["spacyDep"][0], dicHeur["spacyGPE"][0])

        else:
            addTweetValideDB(status.id, tweetText, disasterType, url, status._json, status.created_at, dicHeur["spacyGPE"][1], tweetTextClean, tokens, False, dicHeur["onlyHashtags"][0], dicHeur["spacyDep"][0], dicHeur["spacyGPE"][0])

    else: #Si c'est faux on l'envois dans une base spéciale pour l'utiliser si nécessaire
        addTweetInvalideDB(status.id, tweetText, disasterType, url, status._json, status.created_at)

    #On renvois une valeur pour arrêter le thread proprement
    return True

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
        #On lance un thread pour ne pas interrompre le stream
        _thread.start_new_thread(processTweet, (status,))

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
    relevancy.loadModel()
    loginTweepy()
    startTweepyStream()

if __name__ == "__main__":
    main()
