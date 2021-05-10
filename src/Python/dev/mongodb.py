from pymongo import MongoClient, GEO2D
import urllib
import datetime
import re
import bson

#TODO : Securely store password
password = str(input("Please enter DB password : "))
#Password needs to be encoded for URL standards
passwordEncoded = urllib.parse.quote_plus(password)

client = MongoClient("mongodb+srv://terL3:" + passwordEncoded + "@dbtweet.fakza.mongodb.net/DBTweet?retryWrites=true&w=majority")
db=client.DBTweet
tweetRealTime=db.real_time
tweetValide=db.valide

"""
tweetValide.update_many( 
    {}, 
    {'$set': {"offTopic":None}}
)
"""

"""maxi = 0
tempDoc = ""

cursor = tweetRealTime.find({})
for document in cursor:
    a = len(bson.BSON.encode(document))
    print(a)
    if a>maxi:
        maxi = a
        tempDoc = document

print("Fichier taille max : ", maxi)
print(tempDoc)
"""

tweetRealTime.create_index([("date", -1)], name="date_index")
tweetValide.create_index([("date", -1)], name="date_index")
