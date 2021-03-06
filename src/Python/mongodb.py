from pymongo import MongoClient, GEO2D
import urllib
import datetime

#TODO : Securely store password
password = str(input("Please enter DB password : "))
#Password needs to be encoded for URL standards
passwordEncoded = urllib.parse.quote_plus(password)

client = MongoClient("mongodb+srv://terL3:" + passwordEncoded + "@dbtweet.fakza.mongodb.net/DBTweet?retryWrites=true&w=majority")
db=client.DBTweet
tweetValide=db.valide
tweetRealTime=db.real_time

serverStatusResult=db.command("serverStatus")


d = datetime.datetime.strptime("2021-02-07T16:44:53", "%Y-%m-%dT%H:%M:%S")

listeTV = tweetValide.find()
for tweet in listeTV:
        print(tweet)

    
"""
Cette fonction ajoute un tweet à la base de données "real-time" du programme.
Elle prends en paramètre :
        - L'ID du tweet, qui sera utilisé comme _id dans MongoDB
        - Le string JSON du tweet
        - La date de publication du tweet (convertissable en objet Date)
        - La location GPS du tweet (longitude puis latitude)
"""
def addTweetRealTimeDB(idTweet, text, disasterType, url, jsonData, date, location):
        d = datetime.datetime.strptime("2021-02-07T16:44:53", "%Y-%m-%dT%H:%M:%S")
        
        tweetRealTime.insert_one({
            "_id": str(idTweet),
            "text": text,
            "disasterType": disasterType,
            "url": url,
            "json": jsonData,
            "date": date,
            "location": {"lng":-73.41 , "lat":40.764},
        })

def addTweetValideDB(idTweet, text, disasterType, url, jsonData, date, locations):
        d = datetime.datetime.strptime("2021-02-07T16:44:53", "%Y-%m-%dT%H:%M:%S")

        tweetValide.insert_one({
                "_id": str(idTweet),
                "text": text,
                "disasterType": disasterType,
                "url": url,
                "json": jsonData,
                "date": date,
                "locations": locations,
                "validated": False
}) 
        

print(serverStatusResult)
