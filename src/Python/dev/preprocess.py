import spacy

#spaCy
global nlp
nlp = spacy.load("en_core_web_sm")

import emoji
import regex
import re
from spellchecker import SpellChecker
# Retrieve the default token-matching regex pattern
re_token_match = spacy.tokenizer._get_regex_pattern(nlp.Defaults.token_match)
# Add #hashtag pattern
re_token_match = f"({re_token_match}|#\\w+|@\\w+)"
nlp.tokenizer.token_match = re.compile(re_token_match).match

s = "2020 can't get any worse 💕👭👙 #ihate2020 👨‍👩‍👦‍👦 @bestfriend https://t.co"
#doc = nlp(s)

#-------------------------------------------------------------#
#                        Useful functions                     #
#-------------------------------------------------------------#

def containsEmoji(text):
    text = emoji.demojize(text)
    text = re.findall(r'(:[^:]*:)', text)
    list_emoji = [emoji.emojize(x) for x in text]
    return len(list_emoji) > 0

def keep_token(tok):
    # This is only an example rule
    return not tok.like_url | ('@' in tok.text) | containsEmoji(tok.text)

def delete_mentions_url_uselessChars(text):
    doc = nlp(text)

    final_tokens = list(filter(keep_token, doc))

    original_doc = final_tokens[0].doc

    newText = ''.join(map(lambda x: x.text_with_ws, final_tokens))

    newDoc = nlp(newText)

    return newText

#-------------------------------------------------------------#

def spellCheck(text) :
    spell = SpellChecker()
    words = text.split(" ")
    newWords = []
    correctedText = ""
    for i in range(len(words)) :
        misspelled = spell.unknown([words[i]])
        if len(misspelled) == 0:
            newWords.append(words[i])
        else :
            for word in misspelled:
                newWords.append(spell.correction(word))
    correctedText = " ".join(newWords) 
    return correctedText

#-------------------------------------------------------------#

def lemmatization(text):
    doc = nlp(text)
    processed = ""
    tokens = []
    for token in doc:
        tokens.append(token.lemma_) #les mots contenant ' ne vont être split : can't => ["ca", "n't"]
    processed = " ".join(tokens)
    return processed

#-------------------------------------------------------------#

def delete_stopWords(text):
    doc = nlp(text)
    processed = ""
    tokens = []
    for token in doc:
        if(not token.is_stop):
            tokens.append(token.text)
    processed = " ".join(tokens)
    return processed

#---------------------------------------------------------------#
#                      PreProcessing Functions                  #
#---------------------------------------------------------------#

def spchk_lem(text):
    # Suprresion mentions / url / charactères inutiles
    newText = delete_mentions_url_uselessChars(text)
    # SpellCheck sur le nouveau text
    spchked = spellCheck(newText)
    # Lemmatization
    return lemmatization(spchked)

def spchk_stop_lem(text):
    # Suprresion mentions / url / charactères inutiles
    newText = delete_mentions_url_uselessChars(text)
    # SpellCheck sur le nouveau text
    spchked = spellCheck(newText)
    # Suppression des stop word
    spchked_noStopWords = delete_stopWords(spchked)
    # Lemmatization
    return lemmatization(spchked_noStopWords)

def spchk_stop(text):
    # Suprresion mentions / url / charactères inutiles
    newText = delete_mentions_url_uselessChars(text)
    # SpellCheck sur le nouveau text
    spchked = spellCheck(newText)
    # Suppression des stop word
    return delete_stopWords(spchked)

def onlyHashtags(text) :
    newText = delete_mentions_url_uselessChars(text)
    doc = nlp(newText)
    return list(filter(lambda tok: ('#' in tok.text[0]), doc))

def onlyDates(text) :
    newText = delete_mentions_url_uselessChars(text)
    doc = nlp(newText)
    dates = []
    for ent in doc.ents:
        if ent.label_ == 'DATE':
            dates.append(ent.text)
    return dates

def getTenses(text):
    newText = delete_mentions_url_uselessChars(text)
    doc = nlp(newText)
    tenses = []
    for token in doc:
        tense = token.morph.get("Tense")
        if len(tense) == 1:
            if (tense[0] == 'Past') | (tense[0] == 'Pres'):
                tenses.append([token.text, tense[0]])
    return tenses

print("text :", s)
print("")
print("spchk_lem :",spchk_lem(s))
print("")
print("spchk_stop_lem :",spchk_stop_lem(s))
print("")
print("spchk_stop :",spchk_stop(s))
print("")
print("onlyHashtags :",onlyHashtags(s))
print("")
print("onlyDates :",onlyDates(s))
print("")
print("getTenses :",getTenses(s))