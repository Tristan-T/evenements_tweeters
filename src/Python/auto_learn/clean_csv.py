import csv
import pandas as pd
import math

# Equilibre le fichier file contenant des tweets selon le dataset :
# socialmedia-disaster-tweets-DFE.csv (https://www.kaggle.com/szelee/disasters-on-social-media)
# Note : Pas vraiment une solution très propre mais ça fonctionne


file="disaster_tweet_cleaned.csv"

with open('socialmedia-disaster-tweets-DFE.csv', 'rt', encoding="utf8", newline='') as inp, open('disaster_tweet_cleaned_0.csv', 'wt', encoding="utf8", newline='') as out:
    writer = csv.writer(out)
    for row in csv.reader(inp):
        if row[2] == "finalized" and row[5]!="Can't Decide":
            writer.writerow(row)

names=["tweet_id", "relevancy", "keyword", "text"]

df = pd.read_csv(file[:-4]+"_0.csv", usecols=[0,5,8,10], names=names)
print("Nombre d'occurences par classe :\n",df['relevancy'].value_counts())


def equilibrate(nameIn, nameOut):    
    keyword = ""
    beenDeleted = False
    
    with open(nameIn, 'rt', encoding="utf8", newline='') as inp, open(nameOut, 'wt', encoding="utf8", newline='') as out:
        writer = csv.writer(out)
        for row in csv.reader(inp):
            if keyword!=row[8]:
                if row[5]=="Not Relevant" and not beenDeleted:
                    beenDeleted==True
                    keyword=row[8]
                else:
                    writer.writerow(row)
            else:
                beenDeleted=False
                writer.writerow(row)
                

isEq = False
i=1
while not isEq:
    equilibrate(file[:-4]+"_"+str(i-1)+".csv", file[:-4]+"_"+str(i)+".csv")
    df = pd.read_csv(file[:-4]+"_"+str(i)+".csv", usecols=[0,5,8,10], names=names)
    tab = df['relevancy'].value_counts(normalize=True)
    print(tab)
    i+=1
    #Descending order by default, so we know tab[0] is bigger
    if(math.isclose(tab[0], tab[1], abs_tol=0.02)):
        isEq=True
        print("Le dataset est équilibré")

