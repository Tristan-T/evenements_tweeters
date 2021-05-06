from nltk import word_tokenize 
import string

import dill as pickle

import re
import emoji

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline

# Cette fonction ne prends en charge que les lettres latines
def MyCleanText(X,
               removeEmoji=False, #Emojis
               removeHashtags=False, #Suppression hashtags
              ):

    sentence=str(X)

    #Substitution des espaces multiples par un seul espace
    sentence = re.sub(r'\s+', ' ', sentence, flags=re.I)

    #Suppression mentions et url
    sentence = re.sub(r"(?:\@[a-zA-Z\_0-9]+|https?\:\/\/\S+)", "", sentence)

    # decoupage en mots
    tokens = word_tokenize(sentence)

    # suppression ponctuation
    table = str.maketrans('', '', string.punctuation)
    words = [token.translate(table) for token in tokens]

    # suppression des tokens non alphabetique ou numerique
    words = [word for word in words if word.isalnum()]

    #Suppression hashtag
    if removeHashtags:
      sentence = re.sub(r"\B(\#[a-zA-Z0-9\_]+\b)", "", sentence)

    #Suppression emojis
    if removeEmoji:
      sentence = emoji.get_emoji_regexp().sub(u'', sentence) #On utilise le package emojis car les règles unicodes des emojis changent constamment

    return sentence

class TextNormalizer(BaseEstimator, TransformerMixin):
    def __init__(self, 
                 removeEmoji=False, #Emojis
                 removeHashtags=False, #Suppression hashtags
                ):
        
        self.removeEmoji=removeEmoji
        self.removeHashtags=removeHashtags
        

    def transform(self, X, **transform_params):
        # Nettoyage du texte
        X=X.copy() # pour conserver le fichier d'origine
        return [MyCleanText(text,
                            removeEmoji=self.removeEmoji,
                            removeHashtags=self.removeHashtags) for text in X]

    def fit(self, X, y=None, **fit_params):
        return self
    
    def fit_transform(self, X, y=None, **fit_params):
        return self.fit(X).transform(X)

    def get_params(self, deep=True):
        return {
            'removeEmoji':self.removeEmoji,
            'removeHashtags':self.removeHashtags
        }    
    
    def set_params (self, **parameters):
        for parameter, value in parameters.items():
            setattr(self,parameter,value)
        return self

model = ""

def loadModel():
    global model
    print("RELEVANCY :: INFO :: Chargement du modèle")
    filename = 'disasterRelevantModelMultiNB_alpha06.pkl'
    model = pickle.load(open(filename, 'rb'))
    print("RELEVANCY :: INFO :: Modèle " + filename + " chargé")


def testModel():
    print(model)
    text = "There is a tsunami in Tokyo"
    text2 = "He won the elections in Puerto Rico by a landslide"
    text3 = "I just stormed out of this trash office in Vancouver"
    text4 = "I'm gonna blow up like a volcano if this keeps up"
    text5 = "I had burritos in the storm city of Estalucia #burritos #estalucia"
    text6 = "I love playing granblue fantasy"

    print(text)
    print(model.predict([text]))
    print(text2)
    print(model.predict([text2]))
    print(text3)
    print(model.predict([text3]))
    print(text4)
    print(model.predict([text4]))
    print(text5)
    print(model.predict([text5]))
    print(text6)
    print(model.predict([text6]))

loadModel()
