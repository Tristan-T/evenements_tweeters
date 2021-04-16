#spaCy
import spacy
from spacy.language import Language
from spacy.matcher import Matcher
from spacy.tokens import Token

import re

nlp = ""

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

def showTokens(tweetText, toPrint=False):
    print(tweetText)
    doc = nlp(tweetText)
    if(toPrint):
        for token in doc:
            print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.is_alpha, token.is_stop)


    return doc;


loadSpacy()

# matcher = Matcher(nlp.vocab)
# matcher.add("HASHTAG", [[{"ORTH": "#"}, {"IS_ASCII": True}]])
#
# # Register token extension
# Token.set_extension("is_hashtag", default=False)
#
#
# #The following is only for testing purposes, it is not exhaustive enough to constitue valid proof
# hashtagTest = "There is a tornado in Tsunami #Tsunami"
#
# doc = showTokens(hashtagTest, True)
#
# matches = matcher(doc)
# hashtags = []
# for match_id, start, end in matches:
#     if doc.vocab.strings[match_id] == "HASHTAG":
#         hashtags.append(doc[start:end])
# with doc.retokenize() as retokenizer:
#     for span in hashtags:
#         retokenizer.merge(span)
#         for token in span:
#             token._.is_hashtag = True
#
# for token in doc:
#     print(token.text, token._.is_hashtag)


# Retrieve the default token-matching regex pattern
re_token_match = spacy.tokenizer._get_regex_pattern(nlp.Defaults.token_match)
# Add #hashtag pattern
re_token_match = f"({re_token_match}|#\\w+)"
nlp.tokenizer.token_match = re.compile(re_token_match).match
# Now let's try again
s = "2020 can't get any worse #ihate2020 @bestfriend <https://t.co>"
doc = nlp(s)
# Let's look at the lemmas and is stopword of each token
print(f"Token\\t\\tLemma\\t\\tStopword")
print("="*40)
for token in doc:
    print(f"{token}\\t\\t{token.lemma_}\\t\\t{token.is_stop}")
