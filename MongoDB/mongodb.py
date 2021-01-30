from pymongo import MongoClient
import urllib

#TODO : Securely store password
password = str(input("Please enter DB password : "))
#Password needs to be encoded for URL standards
passwordEncoded = urllib.parse.quote_plus(password)

client = MongoClient("mongodb+srv://terL3:" + passwordEncoded + "@dbtweet.fakza.mongodb.net/DBTweet?retryWrites=true&w=majority")
db=client.admin
serverStatusResult=db.command("serverStatus")
print(serverStatusResult)
