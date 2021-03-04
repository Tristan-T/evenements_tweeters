#Nominatim can also be a good candidate
#from geopy.geocoders import Nominatim

#geolocator = geolocator = Nominatim(user_agent="TER_L3_Tweet_catastrophe")
#location = geolocator.geocode("Montpellier")
#print(location)


from geopy.geocoders import GeoNames
import json

def getLocation(textLoc):
    geolocator = GeoNames(username='ter_l3_10')  #Compte geoname
    location = geolocator.geocode(textLoc, timeout=10) #10 secondes avant erreur
    #On pourra aussi demander une liste de résultats avec exactly_one=False
    #Il existe aussi un paramètre country
    if location != None:
        f = open("test.json", "w")
        json.dump(location.raw, f, indent=4)
        print(location.address)
        print(location.point.format_unicode())
    else:
        print("Location non trouvée : " + textLoc)
        raise NameError("LocationNotFound")

getLocation("Tadcaster (England)")
getLocation("Pampa Bachongo")
#getLocation("Barangay Matangkil")
getLocation("Laurel Highlands")
getLocation("Skewen")
