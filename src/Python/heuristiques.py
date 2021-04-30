import spacy
import geonamescache
import re

global nlp
nlp = spacy.load("en_core_web_sm")

disasters = ["floodwater", "Earthquake", "Volcanic Eruptions", "Volcanic Eruption", "Hurricane", "Cyclone", "Storm", "Flooding", "Extreme precipitation", "Wildfire", "Landslide", "Tsunami"]

# Retrieve the default token-matching regex pattern
re_token_match = spacy.tokenizer._get_regex_pattern(nlp.Defaults.token_match)
# Add #hashtag pattern
re_token_match = f"({re_token_match}|#\\w+|@\\w+)"
nlp.tokenizer.token_match = re.compile(re_token_match).match

#s = "I CAN FEEL THE MIGHT OF ZEUS !! THERE IS A TRULY REMARKABLE STORM IN Athens NOW!! #STORM #ATHENS #ANCIENTGOD"
s = "I can feel the might of Zeus !! There is a truly remarkable storm in Athens and Paris now !! #storm #athens #ancientGod"

doc = nlp(s)

gc = geonamescache.GeonamesCache()

def onlyHashtags(doc) :

    listHashtags = list(filter(lambda tok: ('#' in tok.text[0]), doc))

    foundCity = False
    foundDisaster = False

    for hashtag in listHashtags:
        hashtagValue = hashtag.text[1:].casefold()
        if(hashtagValue in [x.casefold() for x in disasters]):
            foundDisaster = True
        elif(len(gc.search_cities(hashtagValue.capitalize())) > 0):
            foundCity = True

    return True if (foundCity and foundDisaster) else False

def isPast(doc):
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
        if (token.text in [x.casefold() for x in disasters]) : 
            return True
    return False

def spacyGPE(doc, firstTime=True):
    gpeList = getGPE(doc)
    text = doc.text.split(" ")
    newWords = []
    if (len(gpeList) == 0):
        if (not firstTime):
            #envoie BD
            return False
        else :
            for word in text:
                newWord = word.casefold().capitalize()
                newWords.append(newWord)
                doc2 = nlp(" ".join(newWords))
                spacyGPE(doc2, firstTime=False)
    if (len(gpeList) == 1) :
        if(not isPast(doc) and containsDisaster(doc)) :
            return True
    if (len(gpeList) > 1) :
        for gpe in gpeList:
            if (len(gc.search_cities(gpe.capitalize())) == 0) :
                print("je supprime ce gpe")
                gpeList.remove(gpe)

        if (len(gpeList) == 0) :
            #envoie bd
            return False

        if (len(gpeList) == 1) :
            if(not isPast(doc) and containsDisaster(doc)) :
                return True

        if (len(gpeList) > 1) :
            sentences = re.split(r"\.|\?{1,10}|\!{1,10}", doc.text)
            for sentence in sentences:
                newDoc = nlp(sentence)
                print("phrase :", newDoc)
                print("gpe :", getGPE(newDoc))
                print("contient disaster :", containsDisaster(newDoc))
                if (len(getGPE(newDoc)) == 1 and containsDisaster(newDoc)) :
                    return True
            return False

# print(onlyHashtags(doc))
# print(isPast(doc))
# print(getGPE(doc))
#print(containsDisaster(doc))
print(spacyGPE(doc))