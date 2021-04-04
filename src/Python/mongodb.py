from pymongo import MongoClient, GEO2D
import urllib
import datetime
import re

#TODO : Securely store password
password = str(input("Please enter DB password : "))
#Password needs to be encoded for URL standards
passwordEncoded = urllib.parse.quote_plus(password)

client = MongoClient("mongodb+srv://terL3:" + passwordEncoded + "@dbtweet.fakza.mongodb.net/DBTweet?retryWrites=true&w=majority")
db=client.DBTweet
tweetRealTime=db.real_time

serverStatusResult=db.command("serverStatus")


d = datetime.datetime.strptime("2021-02-07T16:44:53", "%Y-%m-%dT%H:%M:%S")

regx = re.compile("web")

print("valide")
for doc in tweetValide.find():
    #doc['url'] = doc['url'].replace('/web', '')
    print(doc['url'])
    #db.valide.replace_one({'_id': doc['_id']}, doc)


print("real time")
for doc in tweetRealTime.find():
    #doc['url'] = doc['url'].replace('/web', '')
    print(doc['url'])
    #db.real_time.replace_one({'_id': doc['_id']}, doc)

print(serverStatusResult)
