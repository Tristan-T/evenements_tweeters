import spacy
import geonamescache
import re
from spacy.matcher import DependencyMatcher
from spacy import displacy
import inspect

global nlp
nlp = spacy.load("en_core_web_sm")

#Faudra load depuis le fichier de config
disasters = ["floodwater", "Earthquake", "Volcanic Eruptions", "Volcanic Eruption", "Hurricane", "Cyclone", "Storm", "Flooding", "Extreme precipitation", "Wildfire", "Landslide", "Tsunami"]

# Retrieve the default token-matching regex pattern
re_token_match = spacy.tokenizer._get_regex_pattern(nlp.Defaults.token_match)
# Add #hashtag pattern
# Pas forcément bon
re_token_match = f"({re_token_match}|#\\w+|@\\w+)"
nlp.tokenizer.token_match = re.compile(re_token_match).match

#s = "I CAN FEEL THE MIGHT OF ZEUS !! THERE IS A TRULY REMARKABLE STORM IN Athens NOW!! #STORM #ATHENS #ANCIENTGOD"
s = "I can feel the might of Zeus !! There is a truly remarkable storm in Athens and Paris now !! #storm #athens #ancientGod"

doc = nlp(s)

gc = geonamescache.GeonamesCache()

def onlyHashtags(doc) :

    #Tester la vitesse
    listHashtags = list(filter(lambda tok: ('#' in tok.text[0]), doc))

    foundCity = False
    foundDisaster = False

    for hashtag in listHashtags:
        hashtagValue = hashtag.text[1:].casefold()
        if(hashtagValue in [x.casefold() for x in disasters]):
            foundDisaster = True
        if(len(gc.search_cities(hashtagValue.capitalize())) > 0):
            foundCity = True

    return (foundCity and foundDisaster)

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
        if (token.text in [x.casefold() for x in disasters]) :
            return True
    return False

def spacyGPE(doc, firstTime=True):
    gpeList = getGPE(doc)
    #Utiliser split spaCy
    newWords = []
    if (len(gpeList) == 0):
        if (not firstTime):
            #envoie BD
            return False
        else :
            for word in doc:
                newWord = word.text_with_ws.casefold().capitalize()
                newWords.append(newWord)
                doc2 = nlp(''.join(newWords))
                spacyGPE(doc2, firstTime=False)
    if (len(gpeList) == 1) :
        #Si pas au passé et contient un désastre c'est ok
        if(not isPast(doc) and containsDisaster(doc)) :
            return True
    if (len(gpeList) > 1) :
        for gpe in gpeList:
            #On supprime les GPE qui ne sont pas des villes
            if (len(gc.search_cities(gpe.capitalize())) == 0) :
                print("Suppression GPE : "+ gpe)
                gpeList.remove(gpe)

        if (len(gpeList) == 0) :
            #envoie bd
            return False

        if (len(gpeList) == 1) :
            if(not isPast(doc) and containsDisaster(doc)) :
                return True

        if (len(gpeList) > 1) :
            for sentence in doc.sents:
                print("")
                print("phrase :", sentence.text)
                print("gpe :", getGPE(sentence))
                print("contient disaster :", containsDisaster(sentence))
                if (len(getGPE(sentence)) == 1 and containsDisaster(sentence)) :
                    return True
            return False

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
    print(doc[matches[0][1][-1]].text)
    #print(doc[3].dep_)
    #([print(str(name)+" : "+str(thing)) for name,thing in inspect.getmembers(doc[
    return bool(matches)
    

#print(onlyHashtags(doc))
#print(isPast(doc))
#print(getGPE(doc))
#print(containsDisaster(doc))
#print(spacyGPE(doc))
doc = nlp("There was a tsunami in Tokyo last night. Wtf was that")
#doc = nlp("I like playing Granblue")

print(spacyDep(doc))
