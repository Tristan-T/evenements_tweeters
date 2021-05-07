Instructions réalisées sous Windows 10 Build 21364.1011 et Ubuntu 20.04 LTS :

0. Si vous n'avez pas d'hébergement pour votre site web il vous faudra installer Wamp (https://www.wampserver.com/) pour Windows ou Xampp sur Linux (https://doc.ubuntu-fr.org/xampp)
Pour simplifier la procédure, vous pouvez cloner le repository Github directement dans les dossiers Wamp/Xampp

1. Clonez le dépot Github : https://github.com/Tristan-T/evenements_tweeters
 
2. Faites une copie du fichier config_sample.json dans le repertoire src/Python puis nommez-le config.json
/!\ Ce fichier contiendra des informations sensibles, veuillez ne pas le partager

3. Il vous faudra renseigner les différents champs vides :
Pour la section Tweepy : Veuillez-vous référer aux instructions sur https://developer.twitter.com/apps concernant la création d'une application (Votre application doit disposer des accés en lecture et écriture)·
Pour la section Mongodb :
	- address : L'adresse de votre serveur MongoDB (et uniquement l'adresse, par exemple dbtweet.torisu.fr)
	- username : Le nom d'un utilisateur disposant des accés en lecture et écriture
	- password : Le mot de passe de l'utilisateur
	- db_name : Le nom de votre base de données
	- collection_valid_name : Le nom de la collection contenant les tweets à valider à la main
    - collection_real_time_name : Le nom de la collection contenant les tweets visibles sur la page web
	- collection_invalid_name : Le nom de la collection contenant les tweets invalidés par le programme
    - collection_rules_name : Le nom de la base contenant les règles d'heuristique pour l'interface de validation
    - optional_URI_parameters": Paramètres de connexion MongoDB, peut être vide
Pour la section geoname : Le nom de votre compte geoname, vous pouvez garder la valeur par défaut pour un déploiement de test
Pour la section misc et evenements_tweeters : Il est conseillé de conserver les valeurs par défaut

4. Dans votre base MongoDB, assurez-vous que la base contiennent bien 4 collections vides correspondant aux noms des collections du fichier de config (par défaut, "valide", "real_time", "invalide", "rules")

5. Installez node.js v14 au minimum
Sous Windows : Installez Node.js (version 14 minimum) : https://nodejs.org/fr/, puis redémarrez
Sous Linux : Les dépôts d'Ubuntu ne contiennent pas une version suffisamment récente de Node.js, il faut l'installer via les dépots officiel de l'équipe Node.js
Ajout dépôt :
$ wget -qO- https://deb.nodesource.com/setup_15.x | sudo -E bash -
Installation node.js et npm
$ sudo apt install -y nodejs

6. Dirigez vous dans le répertoire evenements_tweeters dans un invité de commande
Exécutez la commande :
npm install mongodb

7. Vous pouvez désormais lancez le serveur via la commande : 
node src/Node/app.js

8. Lancez votre serveur web, le site web devrait être disponible à l'adresse localhost:8080

9. Pour lancer le collecteur de tweets, il vous faut installer Python 3 (v3.8 minimum)
Sur Windows : Vous pouvez installer Python3 via le Windows Store
Si vous décidez de l'installer via l'installateur classique, il faudra vous diriger dans Paramètres -> Applications -> Alias d'exécution puis décochez Python et Python3
Installez ensuite en sélectionnant ajouter au PATH : https://www.python.org/downloads/release/python-3810/
Sur Ubuntu : sudo apt install python3 python3-pip

10. Il est conseillé de créer un environnement virtuel pour ne pas changer les dépendances de vos autres programmes :
Selon votre installation, il vous faudra utiliser python ou python3 pour utiliser la version 3 de Python, on utilisera python par la suite, implicitement la version 3
python -m venv evenements-tweeter

Ubuntu :
evenements-tweeter/bin/activate
Windows :
evenements-tweeter\Scripts\activate

Sur Windows :
Installez Visual C++ Redistribuable si vous n'avez pas une version plus récente déjà installée (https://www.microsoft.com/en-in/download/details.aspx?id=48145)

pip install -r requirements.txt (Assurez vous que pip3 soit appelé)
/!\ Si une erreur intervient concernant smart-open, vous pouvez l'ignorer

Il vous faut ensuite téléchargez le modèle de spaCy et les corpora de NLTK :
python -m spacy download en_core_web_sm
Tapez python :
Dans l'invité de commande python faites :
import nltk
nltk.download('punkt')
exit()

Félicitations, vous pouvez désormais lancer le fichier main.py
