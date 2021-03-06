#Nominatim can also be a good candidate
#from geopy.geocoders import Nominatim

#geolocator = geolocator = Nominatim(user_agent="TER_L3_Tweet_catastrophe")
#location = geolocator.geocode("Montpellier")
#print(location)


import geocoder
import json

def getLocation(textLoc):
    # geolocator = GeoNames(username='ter_l3_10')  #Compte geoname
    location = geocoder.geonames(textLoc, key='ter_l3_10')
    # location = geolocator.geocode(textLoc, timeout=10) #10 secondes avant erreur
    #On pourra aussi demander une liste de résultats avec exactly_one=False
    #Il existe aussi un paramètre country
    if len(location) == 1:
        # f = open("test.json", "w")
        # json.dump(location.raw, f, indent=4)
        # print(location.address)
        # print(location.point.format_unicode())
        print("Location : " + str(location))
        print("What type is it :" + str(type(location)))
        print("Location length : " + str(len(location)))
        print("Type of location.lng : " + str(type(location.lng)))
        print("Type of float(location.lng) : " + str(type(float(location.lng))))
        return [float(location.lng), float(location.lat)]
    else:
        print("Location non trouvée : " + textLoc)
        raise NameError("LocationNotFound")

getLocation("Paris")
getLocation("ghfkjskldq")
